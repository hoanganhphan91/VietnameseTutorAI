#!/bin/bash
# Start Whisper STT Service

echo "🎤 Starting Whisper STT Service..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found! Please run setup.sh first"
    exit 1
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
python3 -c "import whisper" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Whisper not installed! Please run setup.sh first"
    exit 1
fi

# Kill any existing service on port 5001
echo "🛑 Stopping any existing service on port 5001..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
sleep 2

# Start the service
echo "🚀 Starting Whisper STT service on port 5001..."
echo "📡 Service will be available at: http://localhost:5001"
echo ""
echo "📋 Available endpoints:"
echo "   GET  /health - Health check"
echo "   POST /transcribe - Convert speech to text" 
echo "   POST /pronunciation - Score pronunciation accuracy"
echo "   POST /detect-accent - Detect Vietnamese regional accent"
echo ""
echo "💡 Press Ctrl+C to stop the service"
echo ""

# Start the Flask application
python3 app.py