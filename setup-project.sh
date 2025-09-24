#!/bin/bash

echo "==================================="
echo "  Vietnamese AI Tutor - Full Setup"
echo "==================================="
echo

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check requirements
echo "Checking system requirements..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Install with: brew install python3"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "Install with: brew install node"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed"
    echo "Install with: brew install node"
    exit 1
fi

echo "✅ All requirements found"

# Check if port 8000 is in use
if lsof -i:8000 &> /dev/null; then
    echo "❌ Port 8000 is already in use!"
    echo "Finding process using port 8000..."
    lsof -i:8000
    echo "Please stop the process or use: sudo lsof -ti:8000 | xargs kill -9"
    exit 1
fi

echo
echo "[1/3] Setting up Backend (FastAPI)..."
cd "$SCRIPT_DIR/backend"

# Remove old virtual environment if exists
if [ -d "venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf venv
fi

# Create fresh virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate and install requirements
source venv/bin/activate
echo "Installing backend dependencies..."
pip install --upgrade pip
pip install email-validator  # Fix for pydantic EmailStr
pip install -r requirements.txt

# Create sample data
if [ -f "create_sample_data.py" ]; then
    echo "Creating sample data..."
    python create_sample_data.py || echo "Warning: Sample data creation failed, continuing..."
fi

# Create environment file
echo "Creating backend environment configuration..."
cat > .env << EOF
DATABASE_URL=sqlite:///./vietnamese_tutor.db
AI_SERVICE_URL=http://localhost:5000
REDIS_URL=redis://localhost:6379
EOF

echo
echo "[2/3] Setting up AI Service (PhoGPT-4B)..."
cd "$SCRIPT_DIR/ai"

# Remove old virtual environment if exists
if [ -d "venv" ]; then
    echo "Removing old AI virtual environment..."
    rm -rf venv
fi

# Create fresh virtual environment
echo "Creating Python virtual environment for AI..."
python3 -m venv venv

# Activate and install requirements
source venv/bin/activate
echo "Installing AI dependencies... (this may take a while)"
pip install --upgrade pip
pip install -r requirements.txt

# Create models directory
mkdir -p "$SCRIPT_DIR/models"

echo
echo "[3/3] Setting up Frontend (NextJS)..."
cd "$SCRIPT_DIR/frontend"

# Remove old node_modules if exists
if [ -d "node_modules" ]; then
    echo "Removing old node_modules..."
    rm -rf node_modules
fi

# Install fresh node modules
echo "Installing Node.js dependencies..."
npm install

# Create environment file
echo "Creating environment configuration..."
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AI_URL=http://localhost:5000
EOF

echo
echo "==================================="
echo "✅ Setup completed successfully!"
echo "==================================="
echo
echo "To start all services: ./start-services.sh"
echo "To stop all services:  ./stop-services.sh"
echo "To test setup:         ./test-setup.sh"
echo
echo "Services will be available at:"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo "🤖 AI API:   http://localhost:5000"
echo