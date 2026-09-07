import os

os.environ["SECURE_COOKIES"] = "false"
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.deps import get_db
from app.main import app
from app.models import Base


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_client(client, db_session):
    """A TestClient already registered+logged in as 'alice'."""
    client.post("/api/auth/register", json={"username": "alice", "password": "password123"})
    client.post("/api/auth/login", json={"username": "alice", "password": "password123"})
    return client


@pytest.fixture()
def admin_client(client, db_session):
    """A TestClient registered+logged in as the first (and thus admin) user 'admin'."""
    client.post("/api/auth/register", json={"username": "admin", "password": "password123"})
    client.post("/api/auth/login", json={"username": "admin", "password": "password123"})
    return client


def make_other_user_client(db_session):
    """Helper: create a second logged-in client ('bob') sharing the same db_session."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    c = TestClient(app)
    c.post("/api/auth/register", json={"username": "bob", "password": "password123"})
    c.post("/api/auth/login", json={"username": "bob", "password": "password123"})
    return c
