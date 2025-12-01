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

# Copy uvicorn wrapper
COPY bin/uvicorn-wrapper.sh /usr/local/bin/uvicorn
RUN chmod +x /usr/local/bin/uvicorn

EXPOSE 8000

# Let Python entrypoint resolve PORT via os.environ for Railway
CMD ["python", "-m", "app.main"]
