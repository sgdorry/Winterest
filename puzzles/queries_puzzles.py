from functools import wraps
from uuid import uuid4
import random
import data.db_connect as dbc

COLLECTION = "puzzles"

ID = "id"
ENTITY_TYPE = "entity_type"  
ANSWER = "answer"
POPULATION = "population"
CLIMATE = "climate"
LANGUAGE = "language"
FLAG_URL = "flag_url"
APPROVED = "approved"

puzzle_cache = {}


def needs_cache(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not puzzle_cache:
            docs = dbc.read(COLLECTION)
            for doc in docs:
                pid = doc.get(ID)
                if pid:
                    puzzle_cache[pid] = doc
        return fn(*args, **kwargs)
    return wrapper


def _require_str(fields: dict, key: str):
    if not fields.get(key) or not isinstance(fields[key], str):
        raise ValueError(f"Missing/invalid {key}")


@needs_cache
def create(fields: dict) -> str:
    if not isinstance(fields, dict):
        raise ValueError("fields must be a dict")

    _require_str(fields, ENTITY_TYPE)
    _require_str(fields, ANSWER)
    _require_str(fields, POPULATION)
    _require_str(fields, CLIMATE)
    _require_str(fields, LANGUAGE)
    _require_str(fields, FLAG_URL)

    pid = fields.get(ID) or uuid4().hex

    doc = {
        ID: pid,
        ENTITY_TYPE: fields[ENTITY_TYPE].strip().lower(),
        ANSWER: fields[ANSWER].strip(),
        POPULATION: fields[POPULATION].strip(),
        CLIMATE: fields[CLIMATE].strip(),
        LANGUAGE: fields[LANGUAGE].strip(),
        FLAG_URL: fields[FLAG_URL].strip(),
        APPROVED: bool(fields.get(APPROVED, True)),
    }

    dbc.create(COLLECTION, doc)
    puzzle_cache[pid] = doc
    return pid


@needs_cache
def read(entity_type: str | None = None) -> list:
    docs = list(puzzle_cache.values())
    if entity_type and entity_type != "mixed":
        et = entity_type.strip().lower()
        docs = [d for d in docs if d.get(ENTITY_TYPE) == et]
    return docs


@needs_cache
def random_puzzles(entity_type: str, count: int = 1) -> list:
    if not isinstance(count, int) or count < 1:
        count = 1
    count = min(count, 50)

    pool = [p for p in puzzle_cache.values() if p.get(APPROVED) is True]
    if entity_type and entity_type != "mixed":
        et = entity_type.strip().lower()
        pool = [p for p in pool if p.get(ENTITY_TYPE) == et]

    if not pool:
        return []

    if count >= len(pool):
        random.shuffle(pool)
        return pool

    return random.sample(pool, count)