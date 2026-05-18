# Multi-stage image for reflex-django dashboard (local dev + production).

ARG PYTHON_VERSION=3.14

FROM python:${PYTHON_VERSION}-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        unzip \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# reflex init loads rxconfig.py, which bootstraps Django (backend.settings).
COPY rxconfig.py manage.py ./
COPY backend/ backend/
COPY dashboard/ dashboard/
COPY items/ items/
COPY accounts/ accounts/
COPY analytics/ analytics/
COPY assets/ assets/

ENV DJANGO_SETTINGS_MODULE=backend.settings \
    PYTHONPATH=/app

RUN reflex init

ARG API_URL=http://localhost:8080
ENV REFLEX_API_URL=${API_URL}

COPY . .

RUN reflex export --frontend-only --no-zip

FROM python:${PYTHON_VERSION}-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=backend.settings \
    PORT=8080

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        unzip \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app /app

COPY scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint.sh \
    && chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/bin/sh", "/usr/local/bin/docker-entrypoint.sh"]
CMD ["reflex", "run", "--env", "prod", "--single-port", "--frontend-port", "8080"]
