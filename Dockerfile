FROM python:3.11-slim

WORKDIR /app

# Install build dependencies for pyswisseph
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    bash \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Install runtime deps
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY backend/alembic.ini ./
COPY backend/alembic ./alembic
COPY backend/app ./app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV EPHEMERIS_PATH=/app/app/ephemeris

EXPOSE 8080

# Railway uses $PORT environment variable
# Run migrations before starting the app. Use || true to ensure the app starts even if migrations have issues (e.g. DB not ready)
CMD ["sh", "-c", "alembic upgrade heads 2>&1 || echo 'Migration failed, continuing anyway...'; exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
