import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.database import Base, engine

logger = logging.getLogger("test_logger")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)

@pytest.fixture(scope="session")
def client():
    """Create a test client with database setup and teardown."""
    try:
        # Create tables for testing
        Base.metadata.create_all(bind=engine)
        logger.info("Test database tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating test database tables: {e}")
        raise

    with TestClient(app) as c:
        yield c

    try:
        # Drop all tables after tests
        Base.metadata.drop_all(bind=engine)
        logger.info("Test database tables dropped successfully.")
    except Exception as e:
        logger.error(f"Error dropping test database tables: {e}")
