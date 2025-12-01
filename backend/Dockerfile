FROM python:3.11-slim

WORKDIR /app

# Install build deps needed for pyswisseph/flatlib
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

# Copy ephemeris files
COPY backend/app/ephemeris ./app/ephemeris

EXPOSE 8000

# Let Python entrypoint resolve PORT via os.environ for Railway
CMD ["python", "-m", "app.main"]
