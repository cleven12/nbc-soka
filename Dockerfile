# Lightweight image to serve NBC Ligi Kuu data over HTTP.
# Build:  docker build -t nbc-ligikuu-data .
# Run:    docker run --rm -p 8000:8000 -v "$PWD/data:/app/data" nbc-ligikuu-data

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/app/data \
    PORT=8000

WORKDIR /app

# Install only what the API needs to run
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY pyproject.toml README.md ABOUT.md ./
COPY scraper ./scraper
COPY api ./api
COPY data ./data

RUN pip install --no-cache-dir --no-deps -e .

EXPOSE 8000

# Production-friendly defaults
CMD ["sh", "-c", "uvicorn api.app:app --host 0.0.0.0 --port ${PORT}"]
