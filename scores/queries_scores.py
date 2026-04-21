from functools import wraps
from uuid import uuid4
from datetime import datetime, timezone, timedelta
import data.db_connect as dbc

COLLECTION = "scores"

ID = "id"
PLAYER = "player"
SCORE = "score"
GUESSES_USED = "guesses_used"
ENTITY_TYPE = "entity_type"
TIMESTAMP = "timestamp"
USER_ID = "user_id"

VALID_ENTITY_TYPES = {"cities", "states", "countries"}

score_cache = {}


def needs_cache(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not score_cache:
            docs = dbc.read(COLLECTION)
            for doc in docs:
                sid = doc.get(ID)
                if sid:
                    score_cache[sid] = doc
        return fn(*args, **kwargs)
    return wrapper


def _require_int(fields: dict, key: str):
    val = fields.get(key)
    if val is None or not isinstance(val, int):
        raise ValueError(f"Missing/invalid {key}")


def _require_str(fields: dict, key: str):
    if not fields.get(key) or not isinstance(fields[key], str):
        raise ValueError(f"Missing/invalid {key}")


@needs_cache
def create(fields: dict) -> str:
    if not isinstance(fields, dict):
        raise ValueError("fields must be a dict")

    _require_int(fields, SCORE)
    _require_int(fields, GUESSES_USED)
    _require_str(fields, ENTITY_TYPE)

    entity_type = fields[ENTITY_TYPE].strip().lower()
    if entity_type not in VALID_ENTITY_TYPES:
        raise ValueError(
            f"entity_type must be one of {sorted(VALID_ENTITY_TYPES)}"
        )

    sid = uuid4().hex
    now = datetime.now(timezone.utc).isoformat()

    doc = {
        ID: sid,
        PLAYER: fields.get(PLAYER, "anonymous"),
        SCORE: fields[SCORE],
        GUESSES_USED: fields[GUESSES_USED],
        ENTITY_TYPE: entity_type,
        TIMESTAMP: now,
    }

    if fields.get(USER_ID):
        doc[USER_ID] = fields[USER_ID]

    dbc.create(COLLECTION, doc)
    score_cache[sid] = doc
    return sid


@needs_cache
def read() -> list:
    docs = list(score_cache.values())
    docs.sort(key=lambda d: d.get(SCORE, 0), reverse=True)
    return docs


@needs_cache
def read_by_user_ids(user_ids: list) -> list:
    if not user_ids:
        return []
    uid_set = set(user_ids)
    docs = [
        doc for doc in score_cache.values()
        if doc.get(USER_ID) in uid_set
    ]
    docs.sort(key=lambda d: d.get(SCORE, 0), reverse=True)
    return docs


PERIOD_DAYS = {
    "week": 7,
    "month": 30,
}


def _filter_by_period(docs, period: str = None):
    if not period or period == "all":
        return docs
    days = PERIOD_DAYS.get(period)
    if days is None:
        return docs
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    return [d for d in docs if d.get(TIMESTAMP, "") >= cutoff]


def _aggregate(docs: list) -> list:
    buckets = {}
    for doc in docs:
        uid = doc.get(USER_ID)
        if not uid:
            continue
        if uid not in buckets:
            buckets[uid] = {
                "user_id": uid,
                "score": 0,
                "guesses_used": 0,
                "games_played": 0,
            }
        buckets[uid]["score"] += doc.get(SCORE, 0)
        buckets[uid]["guesses_used"] += doc.get(GUESSES_USED, 0)
        buckets[uid]["games_played"] += 1
    result = list(buckets.values())
    result.sort(key=lambda d: d["score"], reverse=True)
    return result


@needs_cache
def read_aggregated(period: str = None) -> list:
    docs = _filter_by_period(score_cache.values(), period)
    return _aggregate(docs)


@needs_cache
def read_aggregated_by_user_ids(user_ids: list,
                                period: str = None) -> list:
    if not user_ids:
        return []
    uid_set = set(user_ids)
    docs = [
        doc for doc in score_cache.values()
        if doc.get(USER_ID) in uid_set
    ]
    docs = _filter_by_period(docs, period)
    return _aggregate(docs)
