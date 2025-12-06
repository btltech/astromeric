FROM python:3.11-slim

WORKDIR /app

# Install build deps needed for pyswisseph/flatlib
RUN apt-get update && apt-get install -y --no-install-recommends \
	gcc \
	build-essential \
	bash \
	&& rm -rf /var/lib/apt/lists/*

# Install runtime deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY app ./app

# Copy ephemeris files
COPY app/ephemeris ./app/ephemeris

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV EPHEMERIS_PATH=/app/app/ephemeris
ENV SE_EPHE_PATH=/app/app/ephemeris

EXPOSE 8000

# Railway uses $PORT environment variable
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
