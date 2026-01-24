#!/usr/bin/env sh
set -e

echo "Starting container..."

# Wait for Postgres to be ready (basic loop)
echo "Waiting for Postgres..."
until python -c "import os; import sqlalchemy as sa; from sqlalchemy import text; \
url=os.environ.get('DATABASE_URL'); \
engine=sa.create_engine(url, future=True); \
conn=engine.connect(); conn.execute(text('SELECT 1')); conn.close(); print('Postgres ready')"; do
  echo "Postgres not ready yet - sleeping..."
  sleep 2
done

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting FastAPI (Uvicorn)..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

