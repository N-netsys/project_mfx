import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.config import settings
from app.core.database import Base, get_db

# --- Create a separate Test Database ---
# Use a different database for testing. An in-memory SQLite DB is fast and isolated.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Setup and Teardown ---
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Create test database tables before tests run, and drop them after.
    'autouse=True' makes this fixture run automatically for the session.
    """
    Base.metadata.drop_all(bind=engine) # Ensure a clean slate
    Base.metadata.create_all(bind=engine) # Create tables
    yield
    Base.metadata.drop_all(bind=engine) # Clean up after tests

# --- Fixture to Override the 'get_db' Dependency ---
@pytest.fixture(scope="function")
def db_session() -> Generator:
    """

    Provides a clean database session for each test function.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def test_client(db_session: Generator) -> TestClient:
    """
    Creates a TestClient with the database dependency overridden to use the test DB.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    return client