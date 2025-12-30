import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from fastapi.testclient import TestClient
from app.database import Base, engine
import pytest

@pytest.fixture(scope="session")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
