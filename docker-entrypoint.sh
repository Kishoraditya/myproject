#!/bin/bash
set -e

echo "Waiting for database to be ready..."
# Give the database some time to start up
sleep 5

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Creating cache tables..."
python manage.py createcachetable

echo "Starting application server..."
exec "$@" 