#!/bin/bash

echo "==================================="
echo "  Vietnamese AI Tutor - Clean Reset"
echo "==================================="
echo

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "This will remove all installed dependencies and virtual environments."
read -p "Are you sure? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operation cancelled."
    exit 1
fi

echo
echo "🧹 Cleaning up project..."

# Stop any running services first
echo "Stopping any running services..."
./stop-services.sh

# Clean backend
echo "Cleaning backend..."
cd "$SCRIPT_DIR/backend"
if [ -d "venv" ]; then
    echo "Removing backend virtual environment..."
    rm -rf venv
fi

# Clean AI service
echo "Cleaning AI service..."
cd "$SCRIPT_DIR/ai"
if [ -d "venv" ]; then
    echo "Removing AI virtual environment..."
    rm -rf venv
fi

# Clean frontend
echo "Cleaning frontend..."
cd "$SCRIPT_DIR/frontend"
if [ -d "node_modules" ]; then
    echo "Removing node_modules..."
    rm -rf node_modules
fi
if [ -f "package-lock.json" ]; then
    echo "Removing package-lock.json..."
    rm -f package-lock.json
fi

# Clean other temp files
cd "$SCRIPT_DIR"
echo "Cleaning temporary files..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".next" -type d -exec rm -rf {} + 2>/dev/null || true

echo
echo "==================================="
echo "✅ Project cleaned successfully!"
echo "==================================="
echo
echo "Now run: ./setup-project.sh to reinstall everything"