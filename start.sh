#!/bin/bash

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is ready!"

# Create database tables
echo "Creating database tables..."
python create_db.py

# Start the application
echo "Starting FastAPI application..."
exec python main.py
