def test_user_registration(client):
    response = client.post(
        "/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "strongpassword123"
        },
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"


def test_login(client):
    response = client.post(
        "/v1/auth/login",
        data={
            "username": "testuser",
            "password": "strongpassword123"
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
