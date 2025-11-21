from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import engine

app = FastAPI()

@app.on_event("startup")
def test_db_connection():
    """
    This function runs when the app starts.
    It checks if the database is reachable.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful.")
    except Exception as e:
        print("❌ Database connection failed.")
        print(e)


@app.get("/health")
def read_health():
    return {"status": "ok"}
