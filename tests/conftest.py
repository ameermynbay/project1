# tests/conftest.py
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db
from app import models


# Use SQLite for tests (in-memory or file). Here we'll use a file-based DB.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_reading_tracker.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # needed for SQLite + SQLAlchemy
    future=True,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)


@pytest.fixture(scope="session", autouse=True)
def create_test_database() -> Generator:
    """
    Create tables in the test database before any tests run,
    and drop them after the test session finishes (optional).
    """
    Base.metadata.create_all(bind=engine)
    yield
    # If you want to drop tables after tests:
    Base.metadata.drop_all(bind=engine)


def override_get_db() -> Generator:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the dependency in the FastAPI app
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db() -> Generator:
    """
    Provide a database session for tests that need direct DB access.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client() -> TestClient:
    """
    Provide a TestClient that uses the overridden DB dependency.
    """
    with TestClient(app) as c:
        yield c
