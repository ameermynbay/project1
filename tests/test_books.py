# tests/test_books.py
from fastapi.testclient import TestClient


def register_and_login(client: TestClient, email: str, password: str) -> str:
    # Helper to create a user and return their access token
    client.post("/auth/register", json={"email": email, "password": password})
    res = client.post("/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def test_books_crud_flow(client: TestClient):
    # Setup: create user + token
    token = register_and_login(client, "bookuser@example.com", "bookpassword")
    headers = {"Authorization": f"Bearer {token}"}

    # 1) Create a book
    create_payload = {
        "title": "Demian",
        "author": "Hermann Hesse",
        "total_pages": 200,
    }
    res = client.post("/books", json=create_payload, headers=headers)
    assert res.status_code == 201, res.text
    book = res.json()
    assert book["title"] == "Demian"
    assert book["author"] == "Hermann Hesse"
    assert book["total_pages"] == 200
    book_id = book["id"]

    # 2) List books
    res = client.get("/books", headers=headers)
    assert res.status_code == 200
    books = res.json()
    assert len(books) == 1
    assert books[0]["id"] == book_id

    # 3) Get book by id
    res = client.get(f"/books/{book_id}", headers=headers)
    assert res.status_code == 200
    detail_book = res.json()
    assert detail_book["id"] == book_id

    # 4) Update book
    update_payload = {
        "title": "Demian (Updated)",
        "total_pages": 210,
    }
    res = client.put(f"/books/{book_id}", json=update_payload, headers=headers)
    assert res.status_code == 200
    updated = res.json()
    assert updated["title"] == "Demian (Updated)"
    assert updated["total_pages"] == 210

    # 5) Delete book
    res = client.delete(f"/books/{book_id}", headers=headers)
    assert res.status_code == 204

    # 6) Get deleted book → 404
    res = client.get(f"/books/{book_id}", headers=headers)
    assert res.status_code == 404
