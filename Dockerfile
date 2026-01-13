FROM python:3.11-slim

WORKDIR /app

# Install build dependencies for pyswisseph
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Install runtime deps
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY backend/app ./app

EXPOSE 8080

# Railway uses $PORT environment variable
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
