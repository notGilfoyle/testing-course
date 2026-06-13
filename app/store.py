"""
store.py — a tiny in-memory user store.

This stands in for a real database. In Phase 2 (mocking) we'll treat this as the
"external dependency" that we don't want to actually hit in a unit test, and
learn to replace it with a test double.

The store is intentionally just a dict so the whole app runs with zero setup.
"""

from dataclasses import dataclass


@dataclass
class User:
    username: str
    hashed_password: str


class UserStore:
    """In-memory user store. One instance acts as the app's 'database'."""

    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def get(self, username: str) -> User | None:
        """Return the user with this username, or None if not found."""
        return self._users.get(username)

    def add(self, user: User) -> None:
        """Persist a new user. Raises ValueError if the username already exists."""
        if user.username in self._users:
            raise ValueError(f"User '{user.username}' already exists")
        self._users[user.username] = user

    def clear(self) -> None:
        """Wipe all users — handy for resetting state between tests."""
        self._users.clear()


# A single shared instance used by the app at runtime.
store = UserStore()
