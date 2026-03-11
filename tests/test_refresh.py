from fastapi.testclient import TestClient


def test_refresh_rotation(client: TestClient):
    # register + login
    client.post("/auth/register", json={"email": "rt@example.com", "password": "password123"})
    res = client.post("/auth/login", json={"email": "rt@example.com", "password": "password123"})
    assert res.status_code == 200, res.text
    tokens = res.json()

    old_refresh = tokens["refresh_token"]

    # refresh -> get new pair
    res = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert res.status_code == 200, res.text
    new_tokens = res.json()

    new_refresh = new_tokens["refresh_token"]
    assert new_refresh != old_refresh

    # old refresh should fail (rotated)
    res = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert res.status_code == 401

    # new refresh works
    res = client.post("/auth/refresh", json={"refresh_token": new_refresh})
    assert res.status_code == 200


def test_logout_revokes_refresh(client: TestClient):
    client.post("/auth/register", json={"email": "logout@example.com", "password": "password123"})
    res = client.post("/auth/login", json={"email": "logout@example.com", "password": "password123"})
    refresh = res.json()["refresh_token"]

    # logout
    res = client.post("/auth/logout", json={"refresh_token": refresh})
    assert res.status_code == 204

    # refresh should fail
    res = client.post("/auth/refresh", json={"refresh_token": refresh})
    assert res.status_code == 401