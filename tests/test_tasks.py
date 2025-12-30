import pytest
from fastapi import status

def get_token(client):
    """Helper to get JWT token for auth"""
    response = client.post(
        "/v1/auth/login",
        data={"username": "testuser", "password": "strongpassword123"},
    )
    try:
        assert response.status_code == status.HTTP_200_OK, f"Login failed: {response.text}"
        token = response.json().get("access_token")
        assert token, "No access token returned"
        return token
    except AssertionError as e:
        pytest.fail(f"Authentication setup failed: {e}")


def test_create_task(client):
    """Test creating a new task"""
    token = get_token(client)

    response = client.post(
        "/v1/tasks/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Test Task", "description": "Test desc"},
    )
    try:
        assert response.status_code == status.HTTP_201_CREATED, f"Task creation failed: {response.text}"
        data = response.json()
        assert data.get("title") == "Test Task", f"Unexpected task title: {data}"
        assert "id" in data, f"Task ID missing: {data}"
    except AssertionError as e:
        pytest.fail(f"Create task test failed: {e}")


def test_get_tasks(client):
    """Test retrieving all tasks"""
    token = get_token(client)

    response = client.get(
        "/v1/tasks/",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        assert response.status_code == status.HTTP_200_OK, f"Fetching tasks failed: {response.text}"
        tasks = response.json()
        assert isinstance(tasks, list), f"Expected list, got: {type(tasks)}"
        if tasks:
            assert "title" in tasks[0], f"Task structure invalid: {tasks[0]}"
    except AssertionError as e:
        pytest.fail(f"Get tasks test failed: {e}")
