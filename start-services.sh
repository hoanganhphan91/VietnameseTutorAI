#!/bin/bash

echo "==================================="
echo "  Vietnamese AI Tutor - Local Setup"
echo "==================================="
echo

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if port 8000 is in use
if lsof -i:8000 &> /dev/null; then
    echo "❌ Port 8000 is already in use!"
    echo "Finding process using port 8000..."
    lsof -i:8000
    echo "Please stop the process or use: sudo lsof -ti:8000 | xargs kill -9"
    echo "Then run this script again."
    exit 1
fi

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

# Start backend in background
echo "Starting backend on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
sleep 5

echo
echo "[2/3] Setting up AI Service (PhoGPT-4B)..."
cd "$SCRIPT_DIR/ai"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment for AI service..."
    python3 -m venv venv
fi

# Activate and install requirements
source venv/bin/activate
echo "Installing/updating AI service dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create models directory if not exists
mkdir -p "$SCRIPT_DIR/models"

# Start AI service in background
echo "Starting AI service on port 5000..."
python app.py &
AI_PID=$!
echo "AI Service PID: $AI_PID"
sleep 3

echo
echo "[3/3] Setting up Frontend (NextJS)..."
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
NEXT_PUBLIC_AI_URL=http://localhost:5000
EOF

# Start frontend in background
echo "Starting frontend on port 3000..."
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo
echo "==================================="
echo "Services are starting up..."
echo "==================================="
echo
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo "🤖 AI API:   http://localhost:5000"
echo
echo "Process IDs:"
echo "Backend:  $BACKEND_PID"
echo "AI:       $AI_PID"
echo "Frontend: $FRONTEND_PID"
echo
echo "📝 View logs: Use Ctrl+C to stop all services"
echo "🛑 Or run: ./stop-services.sh"
echo
echo "Waiting for services to fully start..."
sleep 10

# Check if services are running
echo "Checking service status..."
if curl -s http://localhost:8000 >/dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend failed to start"
fi

if curl -s http://localhost:5000 >/dev/null; then
    echo "✅ AI Service is running"
else
    echo "❌ AI Service failed to start"
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
    kill $BACKEND_PID $AI_PID $FRONTEND_PID 2>/dev/null
    echo "All services stopped."
    exit 0
}

# Trap Ctrl+C to cleanup
trap cleanup SIGINT

# Keep script running
wait