#!/bin/sh
set -e

if [ -n "${DJANGO_DB_PATH:-}" ]; then
  mkdir -p "$(dirname "$DJANGO_DB_PATH")"
fi

mkdir -p /app/media /app/staticfiles

reflex django migrate --noinput

if [ "${RUN_COLLECTSTATIC:-0}" = "1" ]; then
  reflex django collectstatic --noinput
fi

exec "$@"
