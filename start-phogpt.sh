#!/bin/bash

# Quick PhoGPT AI Service Launcher
echo "🚀 Starting PhoGPT Vietnamese AI Tutor..."

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR/ai"

# Stop existing service
echo "🛑 Stopping existing AI service..."
lsof -ti:5000 | xargs kill -9 2>/dev/null || true
sleep 2

# Start PhoGPT service
echo "🤖 Starting PhoGPT service..."
source venv/bin/activate
python3 phogpt_direct.py

echo "✅ PhoGPT service ready at http://localhost:5000"