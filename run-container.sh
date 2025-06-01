#!/bin/bash
set -e

# Get the current directory (project root)
PROJECT_DIR=$(pwd)

# Check if required files/directories exist
if [ ! -f "$PROJECT_DIR/survin.db" ]; then
    echo "Error: survin.db not found in current directory"
    exit 1
fi

if [ ! -d "$PROJECT_DIR/snapshots" ]; then
    echo "Error: snapshots directory not found in current directory"
    exit 1
fi

echo "Starting survin container..."
echo "Mounting:"
echo "  - Database: $PROJECT_DIR/survin.db -> /app/survin.db"
echo "  - Snapshots: $PROJECT_DIR/snapshots -> /app/snapshots"

docker stop survin-app || true
docker rm survin-app || true

docker run -d \
    --name survin-app \
    -p 8001:8000 \
    -v "$PROJECT_DIR/survin.db:/app/survin.db:ro" \
    -v "$PROJECT_DIR/snapshots:/app/snapshots:ro" \
    --restart unless-stopped \
    survin

echo "Container started successfully!"
echo "Access the application at: http://localhost:8001"
echo "To view logs: docker logs -f survin-app"
echo "To stop: docker stop survin-app"
echo "To remove: docker rm survin-app"
