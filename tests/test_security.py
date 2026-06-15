# tests/test_security.py
import pytest
from app.security import hash_password, verify_password
from app.security import create_access_token, decode_access_token
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from app.service import authenticate_user, AuthenticationError
from app.store import User

from app import security
from app.store import User  


def test_token_round_trip_returns_subject():
    token = create_access_token(subject="roshan")
    assert decode_access_token(token) == "roshan"


def test_decode_returns_none_for_garbage_token():
    assert decode_access_token("not-a-real-token") is None


def test_expired_token_is_rejected():
    # Arrange — a token that expired 5 minutes ago
    token = create_access_token(subject="roshan", expires_minutes=-5)

    # Act + Assert — decoding an expired token yields None
    assert decode_access_token(token) is None


def test_verify_returns_true_for_correct_password():
    # Arrange — make a real hash from a known password
    password = "correct-horse-battery-staple"
    hashed = hash_password(password)

    # Act — verify the SAME password against that hash
    result = verify_password(password, hashed)

    # Assert — it should accept it
    assert result is True


def test_verify_returns_false_for_wrong_password():
    # Arrange
    hashed = hash_password("the-real-password")

    # Act — verify a DIFFERENT password against that hash
    result = verify_password("the-wrong-password", hashed)

    # Assert — it should reject it
    assert result is False


def test_verify_returns_false_for_malformed_hash_and_does_not_raise():
    # Arrange — garbage that is not a valid Argon2 hash
    not_a_real_hash = "this-is-not-a-hash"

    # Act — the function must catch the error internally...
    result = verify_password("any-password", not_a_real_hash)

    # Assert — ...and return False instead of blowing up
    assert result is False



@pytest.mark.parametrize("bad_token", [
    "not-a-real-token",
    "",
    "a.b.c",                       # looks JWT-shaped but is nonsense
    "Bearer xyz",
])
def test_decode_returns_none_for_invalid_tokens(bad_token):
    assert decode_access_token(bad_token) is None


@pytest.mark.parametrize("subject", ["alice", "bob", "charlie"])
def test_token_round_trips_for_various_subjects(subject):
    token = create_access_token(subject=subject)
    assert decode_access_token(token) == subject


def test_token_is_rejected_after_it_expires():
    # A fixed point in time we'll call "now" when CREATING the token.
    creation_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    # --- Arrange + Act 1: create a normal 30-min token, pretending "now" = creation_time
    with patch("app.security.datetime") as mock_datetime:
        mock_datetime.now.return_value = creation_time
        token = security.create_access_token(subject="roshan")  # expires at 12:30

    # --- Act 2: decode it, but pretend "now" is 31 minutes LATER (12:31) — past expiry
    later_time = creation_time + timedelta(minutes=31)
    with patch("app.security.datetime") as mock_datetime:
        mock_datetime.now.return_value = later_time
        result = security.decode_access_token(token)

    # --- Assert: a 30-min token checked at +31 min must be expired → None
    assert result is None


def test_authenticate_unknown_user_raises():
    # Arrange — a fake store whose .get() returns None (user not found)
    fake_store = MagicMock()
    fake_store.get.return_value = None

    # Act + Assert — authenticating a non-existent user raises
    with pytest.raises(AuthenticationError):
        authenticate_user(fake_store, username="ghost", password="whatever")

    # Bonus: confirm our code actually asked the store for this user
    fake_store.get.assert_called_once_with("ghost")

def test_authenticate_wrong_password_raises():
    # Arrange — a fake store whose .get() returns a user with a known password hash
    fake_store = MagicMock()
    correct_password = "correct-horse-battery-staple"
    hashed = security.hash_password(correct_password)
    fake_store.get.return_value = User(username="alice", hashed_password=hashed)

    # Act + Assert — authenticating with the wrong password raises
    with pytest.raises(AuthenticationError):
        authenticate_user(fake_store, username="alice", password="wrong-password")

    # Bonus: confirm our code actually asked the store for this user
    fake_store.get.assert_called_once_with("alice")

def test_authenticate_correct_password_returns_valid_token():
    # Arrange — a fake store whose .get() returns a user with a known password hash
    fake_store = MagicMock()
    correct_password = "correct-horse-battery-staple"
    hashed = security.hash_password(correct_password)
    fake_store.get.return_value = User(username="alice", hashed_password=hashed)

    # Act — authenticate with the correct password
    token = authenticate_user(fake_store, username="alice", password=correct_password)

    # Assert — it should return the user object (not raise)
    assert security.decode_access_token(token) == "alice"

    # Bonus: confirm our code actually asked the store for this user
    fake_store.get.assert_called_once_with("alice")