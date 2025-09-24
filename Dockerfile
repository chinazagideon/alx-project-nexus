# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project
COPY . /app

# Entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Environment defaults for production
ENV DJANGO_DEBUG=false

EXPOSE 8001

CMD ["/entrypoint.sh"]
