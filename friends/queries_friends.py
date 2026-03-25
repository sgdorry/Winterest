from functools import wraps
from uuid import uuid4
import data.db_connect as dbc

COLLECTION = "friends"

ID = "id"
USER_ID = "user_id"
FRIEND_ID = "friend_id"

friend_cache = {}


def needs_cache(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not friend_cache:
            docs = dbc.read(COLLECTION)
            for doc in docs:
                fid = doc.get(ID)
                if fid:
                    friend_cache[fid] = doc
        return fn(*args, **kwargs)
    return wrapper


@needs_cache
def create(user_id, friend_id):
    if not user_id or not friend_id:
        raise ValueError("user_id and friend_id are required")
    if user_id == friend_id:
        raise ValueError("Cannot add yourself as a friend")

    for doc in friend_cache.values():
        if doc[USER_ID] == user_id and doc[FRIEND_ID] == friend_id:
            raise ValueError("Already friends")

    doc_a = {
        ID: uuid4().hex,
        USER_ID: user_id,
        FRIEND_ID: friend_id,
    }
    doc_b = {
        ID: uuid4().hex,
        USER_ID: friend_id,
        FRIEND_ID: user_id,
    }

    dbc.create(COLLECTION, doc_a)
    dbc.create(COLLECTION, doc_b)
    friend_cache[doc_a[ID]] = doc_a
    friend_cache[doc_b[ID]] = doc_b


@needs_cache
def read(user_id):
    if not user_id:
        return []
    return [
        doc[FRIEND_ID]
        for doc in friend_cache.values()
        if doc[USER_ID] == user_id
    ]


@needs_cache
def delete(user_id, friend_id):
    if not user_id or not friend_id:
        raise ValueError("user_id and friend_id are required")

    to_remove = []
    for fid, doc in friend_cache.items():
        if (doc[USER_ID] == user_id and doc[FRIEND_ID] == friend_id) or \
           (doc[USER_ID] == friend_id and doc[FRIEND_ID] == user_id):
            to_remove.append(fid)

    for fid in to_remove:
        doc = friend_cache[fid]
        dbc.delete(COLLECTION, {ID: doc[ID]})
        del friend_cache[fid]
