from functools import wraps
from uuid import uuid4
from datetime import datetime, timezone
import data.db_connect as dbc

COLLECTION = "scores"

ID = "id"
PLAYER = "player"
SCORE = "score"
GUESSES_USED = "guesses_used"
ENTITY_TYPE = "entity_type"
TIMESTAMP = "timestamp"

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

    dbc.create(COLLECTION, doc)
    score_cache[sid] = doc
    return sid


@needs_cache
def read() -> list:
    docs = list(score_cache.values())
    docs.sort(key=lambda d: d.get(SCORE, 0), reverse=True)
    return docs
