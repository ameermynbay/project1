# tests/test_auth.py
from fastapi.testclient import TestClient


def test_register_and_login_and_me(client: TestClient):
    # 1) Register a user
    register_payload = {
        "email": "testuser@example.com",
        "password": "supersecretpassword",
    }
    res = client.post("/auth/register", json=register_payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["email"] == register_payload["email"]
    assert "id" in data

    # 2) Login with the same user
    login_payload = {
        "email": "testuser@example.com",
        "password": "supersecretpassword",
    }
    res = client.post("/auth/login", json=login_payload)
    assert res.status_code == 200, res.text
    token_data = res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    access_token = token_data["access_token"]

    # 3) Call /auth/me with Bearer token
    headers = {"Authorization": f"Bearer {access_token}"}
    res = client.get("/auth/me", headers=headers)
    assert res.status_code == 200, res.text
    me_data = res.json()
    assert me_data["email"] == register_payload["email"]
    assert me_data["id"] == data["id"]


def test_register_duplicate_email(client: TestClient):
    # First registration
    payload = {"email": "dup@example.com", "password": "password123"}
    res = client.post("/auth/register", json=payload)
    assert res.status_code == 201

    # Second with same email should fail with 400
    res2 = client.post("/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["error" if "error" in res2.json() else "detail"]
