#!/bin/bash
set -e

echo "Starting application deployment..."

# Prepare database before migrations
echo "Preparing database..."
python manage.py prepare_db || echo "Database preparation skipped (tables not ready)"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput --run-syncdb

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn job_portal.wsgi:application \
  --bind 0.0.0.0:$PORT \
  --workers=3 \
  --timeout=60
