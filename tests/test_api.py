# tests/test_api.py
from fastapi.testclient import TestClient

from app.main import app
from app.store import store, User
from app.security import hash_password
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_store():
    store.clear()
    yield
    store.clear()

def test_register_returns_201_and_username():

    # Act — POST /register with a new user
    response = client.post("/register", json={"username": "alice", "password": "s3cret-pw"})

    # Assert — created, and the body echoes the username (never the password)
    assert response.status_code == 201
    assert response.json() == {"username": "alice"}

def test_login_with_wrong_password_returns_401():
    # Arrange — a user in the store with a known password
    store.add(User(username="alice", hashed_password=hash_password("correct-password")))
    response = client.post("/login", json={"username": "alice", "password": "wrong-password"})

    # Assert — it should reject the credentials
    assert response.status_code == 401

def test_me_endpoint_with_valid_token_returns_user():
    # Arrange — a user and a valid token for that user
    store.add(User(username="alice", hashed_password=hash_password("s3cret-pw")))
    login_response = client.post("/login", json={"username": "alice", "password": "s3cret-pw"})
    token = login_response.json()["access_token"]

    # Act — call /me with that token
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    # Assert — it should return the user's info
    assert response.status_code == 200
    assert response.json() == {"username": "alice"}

def test_me_endpoint_with_invalid_token_returns_401():
    # Act — call /me with a token that isn't a real JWT
    response = client.get("/me", headers={"Authorization": "Bearer not-a-real-token"})

    # Assert — rejected
    assert response.status_code == 401

def test_me_endpoint_with_no_token_returns_401():
    response = client.get("/me")     # no headers
    assert response.status_code == 401

def test_register_duplicate_username_returns_400():
    client.post("/register", json={"username": "alice", "password": "pw"})
    # second registration of same username
    response = client.post("/register", json={"username": "alice", "password": "other"})
    assert response.status_code == 400