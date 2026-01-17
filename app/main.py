from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from fastapi import FastAPI, Request
from sqlalchemy import text

from app.db.session import engine
from app.routers.auth import router as auth_router
from app.routers.books import router as books_router
from app.routers.reading_logs import router as reading_logs_router
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as FastAPIHTTPException

app = FastAPI()

# CORS (only enabled if origins are provided)
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Include routers
app.include_router(auth_router)
app.include_router(books_router)
app.include_router(reading_logs_router)


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
    db_ok = True
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    return {
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else "down",
    }


@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
        },
    )
