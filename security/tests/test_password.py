import pytest

from security import password as pw


def test_is_valid_password():
	assert pw.is_valid_password("abcdef")
	assert pw.is_valid_password("longer password")


def test_is_not_valid_password():
	assert not pw.is_valid_password("abc")
	assert not pw.is_valid_password(123456)


def test_hash_and_check_password_round_trip():
	hashed = pw.hash_password("abcdef")
	assert isinstance(hashed, str)
	assert pw.check_password(hashed, "abcdef")
	assert not pw.check_password(hashed, "ghijkl")


def test_hash_password_rejects_short_password():
	with pytest.raises(ValueError, match="Password must be at least 6 characters"):
		pw.hash_password("abc")