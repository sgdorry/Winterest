"""Password helpers for Winterest user accounts."""

import bcrypt

MIN_PASSWORD_LEN = 6


def is_valid_password(password):
	"""Return True when the password satisfies the minimum policy."""
	return isinstance(password, str) and len(password) >= MIN_PASSWORD_LEN


def hash_password(password: str) -> str:
	if not is_valid_password(password):
		raise ValueError(
			f"Password must be at least {MIN_PASSWORD_LEN} characters"
		)
	return bcrypt.hashpw(
		password.encode("utf-8"),
		bcrypt.gensalt(),
	).decode("utf-8")


def check_password(password_hash: str, password: str) -> bool:
	if not isinstance(password_hash, str) or not password_hash:
		return False
	if not is_valid_password(password):
		return False
	return bcrypt.checkpw(
		password.encode("utf-8"),
		password_hash.encode("utf-8"),
	)