import pytest
from app.service import register_user, RegistrationError
from unittest.mock import MagicMock

def test_register_empty_username_raises():
    fake_store = MagicMock()
    with pytest.raises(RegistrationError):
        register_user(fake_store, username="", password="pw")