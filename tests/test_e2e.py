# tests/test_e2e.py
import threading
import time

import uvicorn
import pytest

from app.main import app
from app.store import store, User
from app.security import hash_password
playwright=pytest.importorskip("playwright")
from playwright.sync_api import expect 

HOST, PORT = "127.0.0.1", 8001          # 8001 to avoid clashing with your dev server on 8000
BASE_URL = f"http://{HOST}:{PORT}"


@pytest.fixture(scope="module")
def live_server():
    """Start the real app in a background thread for the duration of this module."""
    config = uvicorn.Config(app, host=HOST, port=PORT, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait for the server to actually be ready before any test runs.
    while not server.started:
        time.sleep(0.05)

    yield BASE_URL                       # tests run here

    server.should_exit = True            # teardown: stop the server
    thread.join(timeout=5)


@pytest.fixture(autouse=True)
def seed_user():
    """Before each test, ensure a known user exists; clean up after."""
    store.clear()
    store.add(User(username="alice", hashed_password=hash_password("s3cret-pw")))
    yield
    store.clear()

@pytest.mark.e2e
def test_successful_login_shows_welcome(live_server, page):
    # Arrange — open the login page in a real browser
    page.goto(live_server)

    # Act — fill the form and click, using the stable data-testid hooks
    page.get_by_test_id("username").fill("alice")
    page.get_by_test_id("password").fill("s3cret-pw")
    page.get_by_test_id("login-button").click()

    # Assert — the welcome message appears (Playwright AUTO-WAITS for it)
    expect(page.get_by_test_id("result")).to_have_text("Welcome, alice!")