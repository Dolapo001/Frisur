#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z pgdb 5432; do
  sleep 1
done

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 1
done

# Run migrations
echo "Applying migrations..."
python manage.py migrate

# Create superuser if not exists
echo "Creating superuser if not exists..."
python manage.py create_superuser || true

# Start the Django server
echo "Starting Django server..."
exec "$@"
