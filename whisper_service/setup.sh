#!/bin/bash
# Whisper STT Service Setup Script

echo "🎤 Setting up Whisper STT Service..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python 3 found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
echo "⏳ This may take a few minutes (downloading Whisper and PyTorch)..."
pip install -r requirements.txt

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment configuration..."
    cp .env.example .env
fi

# Test Whisper installation
echo "🧪 Testing Whisper installation..."
python3 -c "
import whisper
print('✅ Whisper imported successfully')
model = whisper.load_model('tiny')
print('✅ Whisper tiny model loaded successfully')
print('🎉 Whisper service setup complete!')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎤 Whisper STT Service setup complete!"
    echo ""
    echo "📡 To start the service:"
    echo "   source venv/bin/activate"
    echo "   python app.py"
    echo ""
    echo "🌐 Service will be available at: http://localhost:5001"
    echo ""
    echo "📋 API Endpoints:"
    echo "   GET  / - Service info"
    echo "   GET  /health - Health check"  
    echo "   POST /transcribe - Speech to text"
    echo "   POST /pronunciation - Pronunciation scoring"
    echo "   POST /detect-accent - Accent detection"
else
    echo "❌ Setup failed. Please check the error messages above."
    exit 1
fi