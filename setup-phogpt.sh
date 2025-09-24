#!/bin/bash

# Vietnamese AI Tutor - Complete Setup Script with PhoGPT
# This script will download PhoGPT-4B and setup all services

set -e  # Exit on any error

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_BACKEND="$PROJECT_DIR/backend/venv"
VENV_AI="$PROJECT_DIR/ai/venv"

echo "🇻🇳 Vietnamese AI Tutor - Complete Setup with PhoGPT-4B"
echo "=================================================="

# Function to check if Python is available
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "❌ Python not found. Please install Python 3.8+ first."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    echo "✅ Found Python $PYTHON_VERSION"
}

# Function to setup AI service
setup_ai_service() {
    echo "🤖 Setting up AI Service (PhoGPT-4B)..."
    cd "$PROJECT_DIR/ai"
    
    # Create virtual environment for AI
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment for AI service..."
        $PYTHON_CMD -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    echo "Installing AI service requirements..."
    pip install -r requirements.txt
    
    # Check if model is already downloaded
    if [ -d ".cache/models--vinai--PhoGPT-4B-Chat" ]; then
        MODEL_SIZE=$(du -sh .cache 2>/dev/null | cut -f1 || echo "0B")
        echo "📦 Found existing model cache: $MODEL_SIZE"
        
        # Check if model seems complete (should be several GB)
        if [[ "$MODEL_SIZE" == *"G"* ]] || [[ "$MODEL_SIZE" =~ ^[5-9][0-9]*M$ ]]; then
            echo "✅ Model appears to be complete"
        else
            echo "⚠️  Model cache appears incomplete ($MODEL_SIZE)"
            echo "🔄 Re-downloading model..."
            rm -rf .cache/models--vinai--PhoGPT-4B-Chat
            $PYTHON_CMD download_model.py
        fi
    else
        echo "📥 Downloading PhoGPT-4B model (this will take 10-20 minutes)..."
        echo "💾 Model size: ~7-8GB"
        echo "⏳ Please be patient..."
        $PYTHON_CMD download_model.py
    fi
    
    deactivate
    echo "✅ AI Service setup complete!"
}

# Function to setup backend
setup_backend() {
    echo "🔧 Setting up Backend..."
    cd "$PROJECT_DIR/backend"
    
    # Create virtual environment for backend
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment for backend..."
        $PYTHON_CMD -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    echo "Installing backend requirements..."
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        cat > .env << 'EOF'
# Backend Environment Variables
DATABASE_URL=mysql://root:password@localhost:3306/vietnamese_tutor
REDIS_URL=redis://localhost:6379
AI_SERVICE_URL=http://localhost:5000
DEBUG=True
EOF
        echo "✅ Created backend .env file"
    fi
    
    deactivate
    echo "✅ Backend setup complete!"
}

# Function to setup frontend
setup_frontend() {
    echo "🎨 Setting up Frontend..."
    cd "$PROJECT_DIR/frontend"
    
    # Check if Node.js is available
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js not found. Please install Node.js first."
        exit 1
    fi
    
    # Install npm dependencies
    echo "Installing frontend dependencies..."
    npm install
    
    # Create .env.local file if it doesn't exist
    if [ ! -f ".env.local" ]; then
        cat > .env.local << 'EOF'
# Frontend Environment Variables
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AI_URL=http://localhost:5000
EOF
        echo "✅ Created frontend .env.local file"
    fi
    
    echo "✅ Frontend setup complete!"
}

# Function to start all services
start_services() {
    echo "🚀 Starting all services..."
    
    # Kill existing processes
    echo "🔄 Stopping existing services..."
    pkill -f "uvicorn.*main:app" 2>/dev/null || true
    pkill -f "uvicorn.*app_phogpt:app" 2>/dev/null || true
    pkill -f "next dev" 2>/dev/null || true
    sleep 2
    
    # Start AI Service
    echo "🤖 Starting PhoGPT AI Service..."
    cd "$PROJECT_DIR/ai"
    source venv/bin/activate
    nohup $PYTHON_CMD phogpt_direct.py > ai_service.log 2>&1 &
    AI_PID=$!
    deactivate
    echo "PhoGPT Service PID: $AI_PID"
    
    # Wait for AI service to start
    echo "⏳ Waiting for AI service to load model..."
    sleep 10
    
    # Start Backend
    echo "🔧 Starting Backend..."
    cd "$PROJECT_DIR/backend"
    source venv/bin/activate
    nohup $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
    BACKEND_PID=$!
    deactivate
    echo "Backend PID: $BACKEND_PID"
    
    # Start Frontend
    echo "🎨 Starting Frontend..."
    cd "$PROJECT_DIR/frontend"
    nohup npm run dev > frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    
    # Save PIDs
    echo "$AI_PID" > "$PROJECT_DIR/ai_service.pid"
    echo "$BACKEND_PID" > "$PROJECT_DIR/backend.pid"
    echo "$FRONTEND_PID" > "$PROJECT_DIR/frontend.pid"
    
    echo "⏳ Waiting for services to start..."
    sleep 5
    
    # Check service status
    echo ""
    echo "📊 Service Status:"
    echo "=================="
    
    # Check AI Service
    if curl -s http://localhost:5000/health > /dev/null; then
        echo "✅ AI Service: Running (http://localhost:5000)"
    else
        echo "❌ AI Service: Failed to start"
    fi
    
    # Check Backend
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend: Running (http://localhost:8000)"
    else
        echo "❌ Backend: Failed to start"
    fi
    
    # Check Frontend
    if curl -s http://localhost:3000 > /dev/null; then
        echo "✅ Frontend: Running (http://localhost:3000)"
    else
        echo "⏳ Frontend: Still starting... (http://localhost:3000)"
    fi
    
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "🤖 AI Service: http://localhost:5000"
    echo ""
    echo "📝 Logs:"
    echo "  AI Service: $PROJECT_DIR/ai/ai_service.log"
    echo "  Backend: $PROJECT_DIR/backend/backend.log"
    echo "  Frontend: $PROJECT_DIR/frontend/frontend.log"
    echo ""
    echo "🛑 To stop services: ./stop-services.sh"
}

# Main execution
main() {
    echo "Starting complete setup..."
    
    check_python
    setup_ai_service
    setup_backend  
    setup_frontend
    start_services
    
    echo ""
    echo "🇻🇳 Vietnamese AI Tutor is ready!"
    echo "Visit http://localhost:3000 to start learning!"
}

# Run main function
main