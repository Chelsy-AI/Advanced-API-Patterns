import pytest
from fastapi import status

@pytest.mark.order(1)
def test_user_registration(client):
    """Test registering a new user"""
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "strongpassword123"
    }
    response = client.post("/v1/auth/register", json=payload)

    try:
        assert response.status_code == status.HTTP_201_CREATED, f"Unexpected status: {response.status_code}, {response.text}"
        data = response.json()
        assert data["username"] == payload["username"], f"Username mismatch: {data}"
    except AssertionError as e:
        pytest.fail(f"User registration test failed: {e}")


@pytest.mark.order(2)
def test_duplicate_registration(client):
    """Test that registering with the same username/email fails"""
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "strongpassword123"
    }
    response = client.post("/v1/auth/register", json=payload)
    try:
        assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Duplicate registration should fail: {response.text}"
    except AssertionError as e:
        pytest.fail(f"Duplicate registration test failed: {e}")


@pytest.mark.order(3)
def test_login_success(client):
    """Test successful login"""
    response = client.post("/v1/auth/login", data={
        "username": "testuser",
        "password": "strongpassword123"
    })

    try:
        assert response.status_code == status.HTTP_200_OK, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, f"No access token in response: {data}"
    except AssertionError as e:
        pytest.fail(f"Login test failed: {e}")


@pytest.mark.order(4)
def test_login_invalid(client):
    """Test login with invalid credentials"""
    response = client.post("/v1/auth/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    })

    try:
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Invalid login should be 401: {response.text}"
    except AssertionError as e:
        pytest.fail(f"Invalid login test failed: {e}")
