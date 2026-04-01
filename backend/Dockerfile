FROM python:3.11-slim

WORKDIR /app

# Install build deps needed for pyswisseph/flatlib
RUN apt-get update && apt-get install -y --no-install-recommends \
	gcc \
	build-essential \
	bash \
	tzdata \
	&& rm -rf /var/lib/apt/lists/*

# Install runtime deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Alembic migrations
COPY alembic.ini ./
COPY alembic ./alembic

# Copy app
COPY app ./app

# Copy ephemeris files
COPY app/ephemeris ./app/ephemeris

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV EPHEMERIS_PATH=/app/app/ephemeris
ENV SE_EPHE_PATH=/app/app/ephemeris

EXPOSE 8080

# Railway uses $PORT environment variable
CMD ["sh", "-c", "alembic upgrade heads 2>&1 || echo 'Migration failed, continuing anyway...'; exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
