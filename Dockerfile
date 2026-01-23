FROM python:3.11-slim

# Prevent python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (optional but helpful for psycopg2 and build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python deps first (better caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app

# Ensure entrypoint script is executable
RUN chmod +x /app/scripts/entrypoint.sh

EXPOSE 8000

# Entrypoint will run migrations then start server
CMD ["/app/scripts/entrypoint.sh"]