#!/bin/bash
set -e

echo "Waiting for database to be ready..."
# Simple wait - in production you might want a more robust health check
sleep 5

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"
