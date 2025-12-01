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

EXPOSE 8000

# Copy startup script
COPY backend/start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD /app/start.sh
