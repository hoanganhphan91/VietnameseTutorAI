#!/bin/bash

echo "==================================="
echo "  Stopping Vietnamese AI Tutor"
echo "==================================="
echo

# Function to kill process on specific port
kill_port() {
    local port=$1
    local service_name=$2
    
    PID=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$PID" ]; then
        echo "Stopping $service_name (PID: $PID) on port $port..."
        kill -TERM $PID 2>/dev/null
        sleep 2
        # Force kill if still running
        if kill -0 $PID 2>/dev/null; then
            kill -9 $PID 2>/dev/null
        fi
        echo "✅ $service_name stopped."
    else
        echo "ℹ️  No process found on port $port ($service_name)"
    fi
}

# Stop each service
echo "Stopping services on ports 3000, 5000, 8000..."
kill_port 3000 "Frontend (NextJS)"
kill_port 5000 "AI Service (PhoGPT)" 
kill_port 8000 "Backend (FastAPI)"

echo
echo "Cleaning up remaining processes..."

# Kill any remaining uvicorn processes (FastAPI)
pkill -f "uvicorn.*main:app" 2>/dev/null && echo "✅ Stopped remaining uvicorn processes"

# Kill any remaining python processes running our app files
pkill -f "python.*main.py" 2>/dev/null && echo "✅ Stopped backend python processes"
pkill -f "python.*app.py" 2>/dev/null && echo "✅ Stopped AI python processes"

# Kill any remaining npm/node processes for our project
pkill -f "npm run dev" 2>/dev/null && echo "✅ Stopped npm dev processes"
pkill -f "next dev" 2>/dev/null && echo "✅ Stopped Next.js dev processes"

echo
echo "==================================="
echo "✅ All services stopped successfully!"
echo "==================================="
echo
echo "You can now run ./start-services.sh to restart"