#!/bin/bash

echo "==================================="
echo "  Vietnamese AI Tutor - Local Setup"
echo "==================================="
echo

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Auto-stop existing services
echo "Stopping any existing services..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:5000 | xargs kill -9 2>/dev/null || true  
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
lsof -ti:5002 | xargs kill -9 2>/dev/null || true
lsof -ti:5005 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 2

echo "[1/3] Setting up Backend Service (FastAPI)..."
cd "$SCRIPT_DIR/backend"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment for backend..."
    python3 -m venv venv
fi

# Activate and install requirements
source venv/bin/activate
echo "Installing/updating backend dependencies..."
pip install --upgrade pip
pip install email-validator  # Fix for pydantic EmailStr
pip install -r requirements.txt

# Create sample data if needed
if [ -f "create_sample_data.py" ]; then
    echo "Creating sample data..."
    python create_sample_data.py || echo "Warning: Sample data creation failed, continuing..."
fi

# Create/update environment file
echo "Creating backend environment configuration..."
cat > .env << EOF
DATABASE_URL=sqlite:///./vietnamese_tutor.db
AI_SERVICE_URL=http://localhost:5002
REDIS_URL=redis://localhost:6379
EOF

# Start backend in background
echo "Starting backend on port 8000..."
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
sleep 5

echo
echo "[2/4] Setting up Whisper STT Service..."
cd "$SCRIPT_DIR/whisper_service"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment for Whisper..."
    python3 -m venv venv
fi

# Activate and install requirements
source venv/bin/activate
echo "Installing Whisper dependencies..."
pip install --upgrade pip

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Whisper requirements.txt not found! Please run whisper_service/setup.sh first"
    exit 1
fi

pip install -r requirements.txt

# Start Whisper STT service in background using the working app_simple.py
echo "Starting Whisper STT service on port 5001..."
nohup python app_simple.py > whisper.log 2>&1 &
WHISPER_PID=$!
echo "Whisper Service PID: $WHISPER_PID"
sleep 5

echo
echo "[3/4] Setting up AI Service (PhoGPT)..."
cd "$SCRIPT_DIR/ai"

echo "Starting Rasa Chatbot service on port 5005..."
cd "$SCRIPT_DIR/rasa"

# Create virtual environment if not exists
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment for Rasa..."
    python3 -m venv .venv
fi

# Activate and install requirements
source .venv/bin/activate
echo "Installing Rasa dependencies..."
pip install --upgrade pip
pip install rasa
echo
# Start Rasa server in background
nohup rasa run --enable-api --cors '*' --debug > rasa.log 2>&1 &
RASA_PID=$!
echo "Rasa Chatbot PID: $RASA_PID"
sleep 3
echo "[4/4] Setting up Frontend (NextJS)..."
cd "$SCRIPT_DIR/frontend"

# Install node modules if not exists
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Create/update environment file
echo "Creating environment configuration..."
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AI_URL=http://localhost:5005
EOF

# Start frontend in background
echo "Starting frontend on port 3000..."
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo
echo "==================================="
echo "Services are starting up..."
echo "==================================="
echo
echo "🌐 Frontend:     http://localhost:3000"
echo "🔧 Backend:      http://localhost:8000"
echo "🤖 AI Service:   http://localhost:5002"
echo "🤖 AI Service:   http://localhost:5005 (Rasa Chatbot)"
echo "🎤 Whisper STT:  http://localhost:5001"
echo
echo "Process IDs:"
echo "Backend:  $BACKEND_PID"
echo "Whisper:  $WHISPER_PID"
echo "Rasa:     $RASA_PID"
echo "Frontend: $FRONTEND_PID"
echo
echo "📝 View logs: Use Ctrl+C to stop all services"
echo "🛑 Or run: ./stop-services.sh"
echo
echo "Waiting for services to fully start..."
sleep 30

# Check if services are running
echo "Checking service status..."
if curl -s http://localhost:8000 >/dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend failed to start"
fi

if curl -s http://localhost:5001/health >/dev/null; then
    echo "✅ Whisper STT is running"
else
    echo "❌ Whisper STT failed to start"
fi

if curl -s http://localhost:5005 >/dev/null; then
    echo "✅ Rasa Chatbot is running"
else
    echo "❌ Rasa Chatbot failed to start"
fi

if curl -s http://localhost:3000 >/dev/null; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend failed to start"
fi

echo
echo "Press Ctrl+C to stop all services..."

# Function to cleanup on exit
cleanup() {
    echo
    echo "Stopping all services..."
    kill $BACKEND_PID $WHISPER_PID $RASA_PID $FRONTEND_PID 2>/dev/null
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    lsof -ti:5001 | xargs kill -9 2>/dev/null || true  
    lsof -ti:5005 | xargs kill -9 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    echo "All services stopped."
    exit 0
}

# Trap Ctrl+C to cleanup
trap cleanup SIGINT

# Keep script running
wait