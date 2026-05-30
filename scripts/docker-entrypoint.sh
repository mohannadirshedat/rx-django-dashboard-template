#!/bin/sh
# Container entrypoint for the rxdjango-dashboard image.
#
# Responsibilities, in order:
#   1. Ensure the SQLite data dir exists (no-op when running on Postgres).
#   2. Apply pending Django migrations (``python manage.py migrate``).
#   3. Collect static files when explicitly requested (``RUN_COLLECTSTATIC=True``).
#      The production image stages the SPA into ``staticfiles/`` at build
#      time, so this is normally only useful in development.
#   4. Exec the container ``CMD`` (uvicorn in production, ``run_reflex`` in
#      development).
#
# Override the default migration/collectstatic behaviour with env vars:
#
#   * ``SKIP_MIGRATIONS=True``     — do not run ``migrate``.
#   * ``RUN_COLLECTSTATIC=True``   — run ``collectstatic --noinput`` on boot.
#   * ``DJANGO_DB_PATH``           — when set, the SQLite parent dir is created.
#
# Boolean env vars use ``True`` / ``False`` (``1`` / ``0`` are still accepted).

set -e

_is_env_true() {
    case "$(printf '%s' "${1:-}" | tr '[:upper:]' '[:lower:]')" in
        1|true|yes|on) return 0 ;;
        *) return 1 ;;
    esac
}

if [ -n "${DJANGO_DB_PATH:-}" ]; then
    mkdir -p "$(dirname "$DJANGO_DB_PATH")"
fi

mkdir -p /app/media /app/staticfiles /app/uploaded_files

if ! _is_env_true "${SKIP_MIGRATIONS:-False}"; then
    python manage.py migrate --noinput
fi

if _is_env_true "${RUN_COLLECTSTATIC:-False}"; then
    python manage.py collectstatic --noinput
fi

exec "$@"
