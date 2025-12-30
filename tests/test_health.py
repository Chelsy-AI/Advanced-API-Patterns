import pytest
from fastapi import status

def test_health_basic(client):
    """Basic health check"""
    response = client.get("/health")
    try:
        assert response.status_code == status.HTTP_200_OK, f"Health endpoint failed: {response.text}"
        data = response.json()
        assert data.get("status") == "ok", f"Unexpected health status: {data}"
    except AssertionError as e:
        pytest.fail(f"Basic health check failed: {e}")


def test_health_detailed(client):
    """Detailed health check for DB and Redis"""
    response = client.get("/health/detailed")
    try:
        assert response.status_code == status.HTTP_200_OK, f"Detailed health failed: {response.text}"
        data = response.json()
        assert data.get("status") == "ok", f"Status not ok: {data}"
        assert data.get("database") == "ok", f"Database check failed: {data}"
        assert data.get("redis") == "ok", f"Redis check failed: {data}"
    except AssertionError as e:
        pytest.fail(f"Detailed health check failed: {e}")
