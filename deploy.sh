#!/bin/bash

echo "🚀 Setting up AI Vietnamese Tutor..."

# Create required directories
mkdir -p models data

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "📦 Building containers..."
docker-compose build

echo "⬇️ Downloading AI models (this may take a while)..."
# Models will be downloaded on first run

echo "🔥 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 30

echo "🎉 Setup complete!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "🤖 AI Service: http://localhost:5000"
echo "📊 Database: localhost:3306"
echo ""
echo "📝 View logs: docker-compose logs -f"
echo "🛑 Stop services: docker-compose down"