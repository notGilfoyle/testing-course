# tests/test_security.py
import pytest
from app.security import hash_password, verify_password
from app.security import create_access_token, decode_access_token


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
