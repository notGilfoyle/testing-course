"""
service.py — business logic for registration and login.

These functions sit BETWEEN the pure logic (security.py) and the web layer
(main.py). They orchestrate: "to register, hash the password then save the
user"; "to log in, look up the user then verify the password."

Because they depend on the store (our stand-in database), they're the natural
place to learn MOCKING in Phase 2 — and they're exercised end-to-end by the
API tests in Phase 3.
"""

from app.security import hash_password, verify_password, create_access_token
from app.store import User, UserStore


class RegistrationError(Exception):
    """Raised when registration cannot proceed (e.g. duplicate username)."""


class AuthenticationError(Exception):
    """Raised when login credentials are invalid."""


def register_user(store: UserStore, username: str, password: str) -> User:
    """
    Register a new user: hash the password and persist the user.

    Raises RegistrationError if the username is taken or inputs are empty.
    """
    if not username or not password:
        raise RegistrationError("Username and password are required")

    if store.get(username) is not None:
        raise RegistrationError(f"Username '{username}' is already taken")

    user = User(username=username, hashed_password=hash_password(password))
    store.add(user)
    return user


def authenticate_user(store: UserStore, username: str, password: str) -> str:
    """
    Authenticate a user and return a signed access token.

    Raises AuthenticationError if the user doesn't exist or the password is wrong.
    """
    user = store.get(username)
    if user is None:
        raise AuthenticationError("Invalid username or password")

    if not verify_password(password, user.hashed_password):
        raise AuthenticationError("Invalid username or password")

    return create_access_token(subject=username)
