#!/bin/bash

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! pg_isready -h ${PGHOST:-db} -p ${PGPORT:-5432} -U ${PGUSER:-postgres}; do
    echo "Database is not ready yet. Waiting..."
    sleep 2
done

echo "Database is ready!"

# Start the application
exec "$@"