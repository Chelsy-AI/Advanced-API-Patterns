def get_token(client):
    res = client.post(
        "/v1/auth/login",
        data={"username": "testuser", "password": "strongpassword123"},
    )
    return res.json()["access_token"]


def test_create_task(client):
    token = get_token(client)

    response = client.post(
        "/v1/tasks/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Test Task", "description": "Test desc"},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"


def test_get_tasks(client):
    token = get_token(client)

    response = client.get(
        "/v1/tasks/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
