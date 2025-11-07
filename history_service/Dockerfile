# ──────────────────────────────────────────────────────────────
#  Build stage
# ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder
# FROM python:3.11-alpine AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

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

RUN adduser --disabled-password --gecos '' appuser

COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

WORKDIR /app
COPY history_service .

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

USER appuser
EXPOSE 8004

# Health‑check that pings Kafka
HEALTHCHECK --interval=10s --timeout=3s --start-period=30s --retries=3 \
  CMD nc -z kafka 9092 || exit 1

# History service only runs the Kafka consumer management command
CMD ["sh", "-c", "python manage.py migrate --no-input && python manage.py consume_kafka"]
# CMD ["sh", "-c", "python manage.py consume_kafka"]




# # ──────── Build ────────
# FROM python:3.12-slim AS builder
# RUN apt-get update && apt-get install -y --no‑install‑recommends gcc libpq-dev \
#     && rm -rf /var/lib/apt/lists/*
# WORKDIR /app
# COPY requirements.txt .
# RUN python -m venv /venv && /venv/bin/pip install --upgrade pip && /venv/bin/pip install -r requirements.txt

# # ──────── Runtime ────────
# FROM python:3.12-slim
# RUN adduser --disabled‑password --gecos '' appuser
# COPY --from=builder /venv /venv
# ENV PATH="/venv/bin:$PATH"
# WORKDIR /app
# COPY . .
# RUN apt-get update && apt-get install -y --no‑install‑recommends libpq5 netcat-openbsd \
#     && rm -rf /var/lib/apt/lists/*
# USER appuser

# # Health‑check that pings Kafka
# HEALTHCHECK --interval=10s --timeout=3s --start-period=30s --retries=3 \
#   CMD nc -z kafka 9092 || exit 1

# CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py consume_kafka"]
