#!/usr/bin/env sh
set -e

echo "Running database migrations..."
python manage.py migrate --noinput --run-syncdb
python manage.py collectstatic --noinput || true

exec gunicorn job_portal.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers ${GUNICORN_WORKERS:-3} \
  --timeout ${GUNICORN_TIMEOUT:-60}
