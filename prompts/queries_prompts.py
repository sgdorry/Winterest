# prompts/queries_prompts.py
from functools import wraps
from uuid import uuid4
import random
import data.db_connect as dbc

COLLECTION = "prompts"

ID = "id"
TYPE = "type"                 # "COUNTRY_FLAG" | "STATE_FACT" | "CITY_LANDMARK"
ENTITY_TYPE = "entity_type"   # "country" | "state" | "city"
ENTITY_ID = "entity_id"       # "US" | "NY" | etc
ASSET_URL = "asset_url"       # image url
ASSET_TEXT = "asset_text"     # fun fact text
ANSWER = "answer"             # string
APPROVED = "approved"         # bool

prompt_cache = {}  # id -> doc

def needs_cache(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not prompt_cache:
            docs = dbc.read(COLLECTION) 
            for doc in docs:
                pid = doc.get(ID)
                if pid:
                    prompt_cache[pid] = doc
        return fn(*args, **kwargs)
    return wrapper


@needs_cache
def create(fields: dict) -> str:
    if not isinstance(fields, dict):
        raise ValueError("fields must be a dict")

    # Required keys
    for k in [TYPE, ENTITY_TYPE, ENTITY_ID, ANSWER]:
        if not fields.get(k) or not isinstance(fields[k], str):
            raise ValueError(f"Missing/invalid {k}")

    # Must have an asset
    if not fields.get(ASSET_URL) and not fields.get(ASSET_TEXT):
        raise ValueError("Must provide asset_url or asset_text")

    pid = fields.get(ID) or uuid4().hex

    doc = {
        ID: pid,
        TYPE: fields[TYPE].strip(),
        ENTITY_TYPE: fields[ENTITY_TYPE].strip(),
        ENTITY_ID: fields[ENTITY_ID].strip(),
        ANSWER: fields[ANSWER].strip(),
        APPROVED: bool(fields.get(APPROVED, True)),
        ASSET_URL: (fields.get(ASSET_URL) or "").strip(),
        ASSET_TEXT: (fields.get(ASSET_TEXT) or "").strip(),
    }

    dbc.create(COLLECTION, doc)
    prompt_cache[pid] = doc
    return pid

@needs_cache
def read(prompt_type: str | None = None) -> list:
    docs = list(prompt_cache.values())
    if prompt_type:
        docs = [d for d in docs if d.get(TYPE) == prompt_type]
    return docs


@needs_cache
def random_questions(prompt_type: str, count: int = 5) -> list:
    if not prompt_type:
        raise ValueError("type is required")

    if not isinstance(count, int) or count < 1:
        count = 5
    count = min(count, 50)

    pool = [
        p for p in prompt_cache.values()
        if p.get(TYPE) == prompt_type and p.get(APPROVED) is True
    ]

    if not pool:
        return []

    if count >= len(pool):
        random.shuffle(pool)
        return pool

    return random.sample(pool, count)