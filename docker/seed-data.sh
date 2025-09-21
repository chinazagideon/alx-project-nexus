#!/bin/bash
# Docker script to seed data in production environment

set -e

echo "Starting data seeding process..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
python manage.py migrate --noinput

# Check if we should reset data
if [ "$RESET_DATA" = "true" ]; then
    echo "Resetting existing data..."
    python manage.py seed_data --reset
else
    echo "Seeding data without reset..."
    python manage.py seed_data
fi

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='${ADMIN_DEFAULT_USERNAME}').exists():
    User.objects.create_superuser('${ADMIN_DEFAULT_USERNAME}', '${ADMIN_DEFAULT_EMAIL}', '${ADMIN_DEFAULT_PASSWORD}')
    print('Superuser created: ${ADMIN_DEFAULT_USERNAME}/${ADMIN_DEFAULT_PASSWORD}')
else:
    print('Superuser already exists')
EOF

echo "Data seeding completed successfully!"
