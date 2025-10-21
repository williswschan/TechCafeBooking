#!/bin/bash

# Build script for TechCafeBooking Docker container
# Usage: ./build-docker.sh [tag]

set -e

# Default tag
TAG=${1:-latest}
IMAGE_NAME="techcafebooking"

echo "🐳 Building Docker image: ${IMAGE_NAME}:${TAG}"

# Build the Docker image
docker build -t ${IMAGE_NAME}:${TAG} .

echo "✅ Docker image built successfully!"
echo "📦 Image: ${IMAGE_NAME}:${TAG}"
echo ""
echo "🚀 To run the container:"
echo "   docker run -d -p 5000:5000 --name techcafebooking-app ${IMAGE_NAME}:${TAG}"
echo ""
echo "🔧 Or use docker-compose:"
echo "   docker-compose up -d"
echo ""
echo "📋 To see running containers:"
echo "   docker ps"
echo ""
echo "🛑 To stop the container:"
echo "   docker stop techcafebooking-app"
echo "   docker rm techcafebooking-app"
