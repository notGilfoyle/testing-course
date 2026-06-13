# Testing Course — Practice Project

A small FastAPI auth service built to learn software testing from scratch.
Each phase of the course adds tests against this codebase.

## What this app does
A minimal user auth service with:
- Password hashing (Argon2id)
- JWT access tokens (create + decode/verify)
- In-memory user store (no real DB — keeps setup zero-friction)
- API endpoints: register, login, and a protected "me" route

## Project layout
```
testing-course/
├── app/
│   ├── __init__.py
│   ├── security.py      # password hashing + JWT logic  (PHASE 1: unit tests)
│   ├── store.py         # in-memory user store          (PHASE 2: mocking)
│   ├── service.py       # business logic (register/login) (PHASE 2)
│   └── main.py          # FastAPI app + endpoints        (PHASE 3: API tests)
├── tests/
│   └── __init__.py      # (test files added per phase)
├── requirements.txt
└── README.md
```

## Setup
```bash
cd testing-course
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the app
```bash
uvicorn app.main:app --reload
# open http://127.0.0.1:8000/docs  for interactive API docs
```

## Run the tests
```bash
pytest                # from the project root
```
