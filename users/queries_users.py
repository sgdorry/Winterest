from functools import wraps
from uuid import uuid4
import re
import bcrypt
import data.db_connect as dbc

COLLECTION = "users"

ID = "id"
EMAIL = "email"
USERNAME = "username"
PASSWORD = "password"
FRIENDS = "friends"
SCORE = "score"
GAMES_PLAYED = "games_played"

user_cache = {}
USERNAME_PATTERN = re.compile(r"^[a-z0-9_]+$")


def needs_cache(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not user_cache:
            docs = dbc.read(COLLECTION)
            for doc in docs:
                uid = doc.get(ID)
                if uid:
                    _normalize_user_doc(doc)
                    user_cache[uid] = doc
        return fn(*args, **kwargs)
    return wrapper


def _require_str(fields: dict, key: str):
    if not fields.get(key) or not isinstance(fields[key], str):
        raise ValueError(f"Missing/invalid {key}")


def _normalize_user_doc(doc: dict):
    if not isinstance(doc, dict):
        return

    if isinstance(doc.get(EMAIL), str):
        doc[EMAIL] = doc[EMAIL].strip().lower()

    if isinstance(doc.get(USERNAME), str):
        doc[USERNAME] = doc[USERNAME].strip().lower()

    friends = doc.get(FRIENDS)
    if not isinstance(friends, list):
        doc[FRIENDS] = []

    if not isinstance(doc.get(SCORE), int):
        doc[SCORE] = 0

    if not isinstance(doc.get(GAMES_PLAYED), int):
        doc[GAMES_PLAYED] = 0


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


@needs_cache
def create(fields: dict) -> str:
    if not isinstance(fields, dict):
        raise ValueError("fields must be a dict")

    _require_str(fields, EMAIL)
    _require_str(fields, USERNAME)
    _require_str(fields, PASSWORD)

    email = fields[EMAIL].strip().lower()
    username = fields[USERNAME].strip().lower()
    if not username:
        raise ValueError("Missing/invalid username")
    if not USERNAME_PATTERN.fullmatch(username):
        raise ValueError(
            "Username can only include letters, numbers, and underscores"
        )

    existing_user = find_by_email(email)
    if existing_user:
        raise ValueError("User already exists")

    existing_username = find_by_username(username)
    if existing_username:
        raise ValueError("Username already exists")

    uid = fields.get(ID) or uuid4().hex
    stored_password = _hash_password(fields[PASSWORD])

    doc = {
        ID: uid,
        EMAIL: email,
        USERNAME: username,
        PASSWORD: stored_password,
        FRIENDS: list(fields.get(FRIENDS, [])),
        SCORE: fields.get(SCORE, 0),
        GAMES_PLAYED: fields.get(GAMES_PLAYED, 0),
    }

    _normalize_user_doc(doc)

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


@needs_cache
def find_by_username(username: str):
    if not username or not isinstance(username, str):
        return None

    username = username.strip().lower()

    for user in user_cache.values():
        if user.get(USERNAME) == username:
            return user

    return None


@needs_cache
def verify(email_or_username: str, password: str):
    if not email_or_username or not isinstance(email_or_username, str):
        return None
    if not password or not isinstance(password, str):
        return None

    user = find_by_email(email_or_username)
    if not user:
        user = find_by_username(email_or_username)
    if not user:
        return None

    stored_password = user.get(PASSWORD, "")
    if not isinstance(stored_password, str) or not stored_password:
        return None

    if bcrypt.checkpw(
        password.encode("utf-8"),
        stored_password.encode("utf-8"),
    ):
        return user

    return None


@needs_cache
def add_friend(user_id: str, friend_id: str):
    if not user_id or not friend_id:
        raise ValueError("user_id and friend_id are required")
    if user_id == friend_id:
        raise ValueError("Cannot add yourself as a friend")

    user = user_cache.get(user_id)
    friend = user_cache.get(friend_id)
    if not user or not friend:
        raise ValueError("User not found")

    user_friends = user.get(FRIENDS, [])
    friend_friends = friend.get(FRIENDS, [])

    if friend_id not in user_friends:
        user_friends.append(friend_id)
    if user_id not in friend_friends:
        friend_friends.append(user_id)

    dbc.update(COLLECTION, {ID: user_id}, {FRIENDS: user_friends})
    dbc.update(COLLECTION, {ID: friend_id}, {FRIENDS: friend_friends})

    user[FRIENDS] = user_friends
    friend[FRIENDS] = friend_friends

    return user_friends


@needs_cache
def update_score(user_id: str, score_delta: int, games_delta: int = 1):
    if not user_id:
        raise ValueError("user_id is required")
    if not isinstance(score_delta, int):
        raise ValueError("score_delta must be an int")
    if not isinstance(games_delta, int):
        raise ValueError("games_delta must be an int")

    user = user_cache.get(user_id)
    if not user:
        raise ValueError("User not found")

    new_score = user.get(SCORE, 0) + score_delta
    new_games_played = user.get(GAMES_PLAYED, 0) + games_delta

    update_fields = {
        SCORE: new_score,
        GAMES_PLAYED: new_games_played,
    }
    dbc.update(COLLECTION, {ID: user_id}, update_fields)

    user[SCORE] = new_score
    user[GAMES_PLAYED] = new_games_played

    return {
        ID: user_id,
        SCORE: new_score,
        GAMES_PLAYED: new_games_played,
    }


@needs_cache
def get_leaderboard(limit: int = 10) -> list:
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("limit must be a positive int")

    users = list(user_cache.values())
    users.sort(key=lambda user: user.get(SCORE, 0), reverse=True)
    return users[:limit]