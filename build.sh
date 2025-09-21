#!/usr/bin/env bash
# exit on error
set -o errexit

# Create logs directory
mkdir -p logs

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate

