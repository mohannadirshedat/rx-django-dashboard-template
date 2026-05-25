# syntax=docker/dockerfile:1.7
# Multi-stage Docker image for the rxdjango-dashboard project.
#
# Targets:
#   * dev      → Python deps installed; source is bind-mounted by
#                ``docker-compose.yml`` and ``manage.py run_reflex`` builds the
#                SPA on first request.
#   * builder  → ``dev`` + the SPA build (``export_reflex`` +
#                ``collectstatic``). Internal; consumed by ``runtime``.
#   * runtime  → Production image: prebuilt SPA staged under
#                ``STATIC_ROOT/_reflex``, served by uvicorn through
#                ``reflex_django.asgi_entry:application`` on port 8000.
#
# Follows the reflex-django deployment guide:
# https://github.com/mohan-walker/reflex-django/blob/main/docs/deployment.md

ARG PYTHON_VERSION=3.14
ARG NODE_VERSION=22

# -------------------------------------------------------------------------
# dev — Python + Node toolchain for building the Reflex SPA in-place.
# -------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS dev

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=backend.settings

ARG NODE_VERSION
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        gnupg \
        unzip \
    && curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint.sh \
    && chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["python", "manage.py", "run_reflex"]

# -------------------------------------------------------------------------
# builder — bake the SPA into the image. Used as a build stage only.
# -------------------------------------------------------------------------
FROM dev AS builder

COPY . .

# DJANGO_SECRET_KEY must be set at build time so ``export_reflex`` can boot
# Django (the SPA build imports settings to discover pages). Override with
# a real key in your registry's build args / secrets manager; the default
# is only valid because ``manage.py export_reflex`` never accepts user input.
ARG DJANGO_SECRET_KEY="build-only-key-replace-at-runtime"
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY} \
    DJANGO_DEBUG=0

RUN python manage.py export_reflex \
        --frontend-only --no-zip --stage-to-static-root \
    && python manage.py collectstatic --noinput

# -------------------------------------------------------------------------
# runtime — slim production image. No Node, no source build tools.
# -------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=backend.settings \
    DJANGO_DEBUG=0

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Bring across the pre-built virtualenv, the project source, and the
# compiled SPA in ``staticfiles/_reflex``.
COPY --from=builder /app /app

COPY scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint.sh \
    && chmod +x /usr/local/bin/docker-entrypoint.sh

# Drop privileges for the runtime process.
RUN groupadd --system app \
    && useradd --system --gid app --home /app --shell /usr/sbin/nologin app \
    && mkdir -p /app/media /app/uploaded_files /data \
    && chown -R app:app /app /data
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://localhost:8000/_health || exit 1

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["uvicorn", "reflex_django.asgi_entry:application", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*"]
