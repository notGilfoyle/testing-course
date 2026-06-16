"""
main.py — the FastAPI web layer.

Thin endpoints that translate HTTP requests into service calls and service
results/errors back into HTTP responses. This is the API-TEST target (Phase 3):
we'll use FastAPI's TestClient to hit these routes and assert on status codes
and JSON payloads.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from fastapi.responses import FileResponse
from pathlib import Path

from app.security import decode_access_token
from app.service import (
    register_user,
    authenticate_user,
    RegistrationError,
    AuthenticationError,
)
from app.store import store

app = FastAPI(title="Testing Course Auth Service")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# --- Request/response schemas ----------------------------------------------
class Credentials(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    username: str


# --- Endpoints --------------------------------------------------------------
@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(creds: Credentials):
    try:
        user = register_user(store, creds.username, creds.password)
    except RegistrationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return UserResponse(username=user.username)


@app.post("/login", response_model=TokenResponse)
def login(creds: Credentials):
    try:
        token = authenticate_user(store, creds.username, creds.password)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return TokenResponse(access_token=token)


@app.get("/me", response_model=UserResponse)
def me(token: str = Depends(oauth2_scheme)):
    username = decode_access_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return UserResponse(username=username)

@app.get("/")
def serve_login_page():
    """Serve the login page so it's same-origin with the API (avoids CORS)."""
    return FileResponse(Path(__file__).parent / "static" / "login.html")
