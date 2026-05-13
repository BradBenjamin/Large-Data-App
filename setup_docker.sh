#!/bin/bash
# setup_docker.sh - Quick setup helper for Docker Compose deployment
# 
# Usage:
#   chmod +x setup_docker.sh
#   ./setup_docker.sh
#

set -e  # Exit on error

echo "🐳 Amazon Review Predictor - Docker Compose Setup"
echo "=================================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed!"
    echo "Please install Docker Desktop (includes Docker Compose)"
    exit 1
fi

echo "✅ Docker installed: $(docker --version)"
echo "✅ Docker Compose installed: $(docker-compose --version)"
echo ""

# Check if model file exists
if [ ! -f "model/amazon_lgb_model.txt" ]; then
    echo "❌ Model file not found at model/amazon_lgb_model.txt"
    echo "Please ensure your model file is in the correct location."
    exit 1
fi

echo "✅ Model file found"
echo ""

# Check if docker-compose.yaml exists
if [ ! -f "docker-compose.yaml" ]; then
    echo "❌ docker-compose.yaml not found in current directory!"
    echo "Please ensure docker-compose.yaml is in your project root."
    exit 1
fi

echo "✅ docker-compose.yaml found"
echo ""

# Check if Dockerfiles exist
if [ ! -f "Dockerfile.api" ] || [ ! -f "Dockerfile.frontend" ]; then
    echo "❌ Dockerfile.api or Dockerfile.frontend not found!"
    echo "Please ensure both Dockerfile.api and Dockerfile.frontend are in your project root."
    exit 1
fi

echo "✅ Both Dockerfile.api and Dockerfile.frontend found"
echo ""

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env created (you can edit it if needed)"
    else
        echo "⚠️  .env.example not found, skipping .env creation"
    fi
else
    echo "✅ .env already exists"
fi

echo ""
echo "=================================================="
echo "🎉 Setup complete! Ready to start Docker Compose"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. docker-compose build    (build images)"
echo "  2. docker-compose up       (start services)"
echo "  3. Open http://localhost:8501 in your browser"
echo ""
echo "Optional:"
echo "  - docker-compose logs -f   (view logs)"
echo "  - docker-compose down      (stop services)"
echo ""
echo "Tip: Read DOCKER_COMPOSE_GUIDE.md for detailed usage!"
echo ""
