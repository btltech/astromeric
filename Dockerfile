FROM python:3.11-slim

WORKDIR /app

# Install build dependencies for pyswisseph
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install runtime deps
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY backend/app ./app

# Copy ephemeris files
COPY backend/app/ephemeris ./app/ephemeris

EXPOSE 8000

# Create a startup script to handle PORT variable
RUN echo '#!/bin/bash\nport=${PORT:-8000}\nuvicorn app.main:app --host 0.0.0.0 --port $port' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
