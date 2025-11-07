# ──────────────────────────────────────────────────────────────
#  Build stage
# ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder
# FROM python:3.11-alpine AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a virtualenv and install Python deps
WORKDIR /app
COPY requirements.txt .
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r requirements.txt

# ──────────────────────────────────────────────────────────────
#  Runtime stage
# ──────────────────────────────────────────────────────────────
FROM python:3.12-slim
# FROM python:3.11-alpine

# Non-root user
RUN adduser --disabled-password --gecos '' appuser

# Copy virtualenv from builder
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy source
WORKDIR /app
COPY wallet_service .

# Runtime dependencies (psql client only needed for migrations)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

USER appuser
EXPOSE 8005

# CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8005"]
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8005"]
