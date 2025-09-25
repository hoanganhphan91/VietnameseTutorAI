#!/bin/bash
# Complete Setup Script for Vietnamese Tutor AI with Whisper Integration

echo "🇻🇳 Vietnamese Tutor AI - Complete Setup"
echo "========================================"
echo

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Check system requirements
echo "🔍 Checking system requirements..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "Please install Python 3.8+ first"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed" 
    echo "Please install Node.js 16+ first"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo "✅ Node.js found: $(node --version)"

# Setup Backend
echo ""
echo "🔧 [1/4] Setting up Backend (FastAPI)..."
cd "$PROJECT_DIR/backend"

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "Creating backend environment file..."
    cat > .env << EOF
DATABASE_URL=sqlite:///./vietnamese_tutor.db
AI_SERVICE_URL=http://localhost:5000
WHISPER_SERVICE_URL=http://localhost:5001  
REDIS_URL=redis://localhost:6379
EOF
fi

echo "✅ Backend setup complete"

# Setup Whisper Service
echo ""
echo "🎤 [2/4] Setting up Whisper STT Service..."
cd "$PROJECT_DIR/whisper_service"

if [ ! -f "setup.sh" ]; then
    echo "❌ Whisper service files not found!"
    echo "Please ensure whisper_service/ directory is properly created"
    exit 1
fi

# Run Whisper setup
chmod +x setup.sh
./setup.sh

echo "✅ Whisper STT service setup complete"

# Setup AI Service  
echo ""
echo "🤖 [3/4] Setting up AI Service (PhoGPT)..."
cd "$PROJECT_DIR/ai"

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment for AI..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install flask requests

echo "✅ AI service setup complete"

# Setup Frontend
echo ""
echo "🌐 [4/4] Setting up Frontend (NextJS)..."
cd "$PROJECT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Create .env.local
if [ ! -f ".env.local" ]; then
    echo "Creating frontend environment file..."
    cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AI_URL=http://localhost:5000
NEXT_PUBLIC_WHISPER_URL=http://localhost:5001
EOF
fi

echo "✅ Frontend setup complete"

# Create launch script
echo ""
echo "📝 Creating convenience scripts..."
cd "$PROJECT_DIR"

# Make scripts executable
chmod +x start-services.sh
chmod +x stop-services.sh

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "🚀 To start all services:"
echo "   ./start-services.sh"
echo ""
echo "🛑 To stop all services:"  
echo "   ./stop-services.sh"
echo ""
echo "🌐 Services will be available at:"
echo "   Frontend:     http://localhost:3000"
echo "   Backend API:  http://localhost:8000/docs"
echo "   AI PhoGPT:    http://localhost:5000"
echo "   Whisper STT:  http://localhost:5001"
echo ""
echo "🎯 Features enabled:"
echo "   ✅ Text chat with PhoGPT"
echo "   ✅ Voice chat with Whisper + PhoGPT"
echo "   ✅ Pronunciation assessment"
echo "   ✅ Vietnamese accent detection"  
echo "   ✅ Regional dialect support"
echo ""
echo "💡 First run will download AI models (~300MB total)"
echo "📚 Check README.md for detailed documentation"