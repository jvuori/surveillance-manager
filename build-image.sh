#!/bin/bash
set -e

echo "Building Docker image 'survin'..."
docker build -t survin .

echo "Docker image 'survin' built successfully!"
