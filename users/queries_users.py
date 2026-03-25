from functools import wraps
from uuid import uuid4
import data.db_connect as dbc

COLLECTION = "users"

ID = "id"
EMAIL = "email"
PASSWORD = "password"

user_cache = {}


def needs_cache(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not user_cache:
            docs = dbc.read(COLLECTION)
            for doc in docs:
                uid = doc.get(ID)
                if uid:
                    user_cache[uid] = doc
        return fn(*args, **kwargs)
    return wrapper


def _require_str(fields: dict, key: str):
    if not fields.get(key) or not isinstance(fields[key], str):
        raise ValueError(f"Missing/invalid {key}")


@needs_cache
def create(fields: dict) -> str:
    if not isinstance(fields, dict):
        raise ValueError("fields must be a dict")

    _require_str(fields, EMAIL)
    _require_str(fields, PASSWORD)

    email = fields[EMAIL].strip().lower()

    existing_user = find_by_email(email)
    if existing_user:
        raise ValueError("User already exists")

    uid = fields.get(ID) or uuid4().hex

    doc = {
        ID: uid,
        EMAIL: email,
        PASSWORD: fields[PASSWORD],
    }

    dbc.create(COLLECTION, doc)
    user_cache[uid] = doc
    return uid


@needs_cache
def read() -> list:
    return list(user_cache.values())


@needs_cache
def find_by_email(email: str):
    if not email or not isinstance(email, str):
        return None

    email = email.strip().lower()

    for user in user_cache.values():
        if user.get(EMAIL) == email:
            return user

    return None