#!/bin/sh
# Container entrypoint for the rxdjango-dashboard image.
#
# Responsibilities, in order:
#   1. Ensure the SQLite data dir exists (no-op when running on Postgres).
#   2. Apply pending Django migrations (``python manage.py migrate``).
#   3. Collect static files when explicitly requested (``RUN_COLLECTSTATIC=1``).
#      The production image stages the SPA into ``staticfiles/`` at build
#      time, so this is normally only useful in development.
#   4. Exec the container ``CMD`` (uvicorn in production, ``run_reflex`` in
#      development).
#
# Override the default migration/collectstatic behaviour with env vars:
#
#   * ``SKIP_MIGRATIONS=1``     — do not run ``migrate``.
#   * ``RUN_COLLECTSTATIC=1``   — run ``collectstatic --noinput`` on boot.
#   * ``DJANGO_DB_PATH``        — when set, the SQLite parent dir is created.

set -e

if [ -n "${DJANGO_DB_PATH:-}" ]; then
    mkdir -p "$(dirname "$DJANGO_DB_PATH")"
fi

mkdir -p /app/media /app/staticfiles /app/uploaded_files

if [ "${SKIP_MIGRATIONS:-0}" != "1" ]; then
    python manage.py migrate --noinput
fi

if [ "${RUN_COLLECTSTATIC:-0}" = "1" ]; then
    python manage.py collectstatic --noinput
fi

exec "$@"
