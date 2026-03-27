import pytest
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    # Disable rate limiting so tests never hit 429
    app.state.limiter.enabled = False
    with TestClient(app) as c:
        yield c
    app.state.limiter.enabled = True
    app.dependency_overrides.clear()


@pytest.fixture
def register_and_login(client, db):
    """Register a user, activate them (bypassing email verification), and log in.

    Returns a callable: register_and_login(email, password) -> access_token
    """

    def _inner(email: str = "user@example.com", password: str = "secret123") -> str:
        client.post("/api/v1/auth/register", json={"email": email, "password": password})
        user = db.scalar(select(User).where(User.email == email))
        user.is_active = True
        db.commit()
        r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        return r.json()["access_token"]

    return _inner
