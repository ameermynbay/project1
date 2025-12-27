# tests/test_reading_logs.py
from datetime import date

from fastapi.testclient import TestClient


def register_and_login(client: TestClient, email: str, password: str) -> str:
    client.post("/auth/register", json={"email": email, "password": password})
    res = client.post("/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def create_book(client: TestClient, headers: dict) -> int:
    payload = {
        "title": "Reading Book",
        "author": "Some Author",
        "total_pages": 300,
    }
    res = client.post("/books", json=payload, headers=headers)
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_reading_logs_crud_and_summary(client: TestClient):
    # Setup: user + token + book
    token = register_and_login(client, "loguser@example.com", "logpassword")
    headers = {"Authorization": f"Bearer {token}"}

    book_id = create_book(client, headers)

    # 1) Create first reading log
    log1_payload = {
        "book_id": book_id,
        "pages_read": 20,
        "date": "2025-12-10",
        "note": "First session",
    }
    res = client.post("/reading-logs", json=log1_payload, headers=headers)
    assert res.status_code == 201, res.text
    log1 = res.json()
    log1_id = log1["id"]
    assert log1["pages_read"] == 20

    # 2) Create second reading log
    log2_payload = {
        "book_id": book_id,
        "pages_read": 30,
        "date": "2025-12-11",
        "note": "Second session",
    }
    res = client.post("/reading-logs", json=log2_payload, headers=headers)
    assert res.status_code == 201, res.text
    log2 = res.json()
    log2_id = log2["id"]
    assert log2["pages_read"] == 30

    # 3) List logs (should see 2)
    res = client.get("/reading-logs", headers=headers)
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) == 2

    # 4) Get summary for this book
    res = client.get(f"/reading-logs/summary?book_id={book_id}", headers=headers)
    assert res.status_code == 200
    summary = res.json()
    assert summary["total_pages_read"] == 50

    # 5) Update first log
    update_payload = {
        "pages_read": 25,
        "note": "Updated first session",
    }
    res = client.put(f"/reading-logs/{log1_id}", json=update_payload, headers=headers)
    assert res.status_code == 200
    updated = res.json()
    assert updated["pages_read"] == 25

    # 6) Check summary again
    res = client.get(f"/reading-logs/summary?book_id={book_id}", headers=headers)
    assert res.status_code == 200
    summary2 = res.json()
    # Now total should be 25 (updated) + 30 = 55
    assert summary2["total_pages_read"] == 55

    # 7) Delete one log
    res = client.delete(f"/reading-logs/{log2_id}", headers=headers)
    assert res.status_code == 204

    # 8) Ensure listing returns only one
    res = client.get("/reading-logs", headers=headers)
    assert res.status_code == 200
    logs_after_delete = res.json()
    assert len(logs_after_delete) == 1
    assert logs_after_delete[0]["id"] == log1_id
