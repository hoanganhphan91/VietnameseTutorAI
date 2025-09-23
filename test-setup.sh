#!/bin/bash

echo "==================================="
echo "  Vietnamese AI Tutor - Setup Test"
echo "==================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is not installed"
        return 1
    fi
}

# Function to check if port is available
check_port() {
    if lsof -i:$1 &> /dev/null; then
        echo -e "${YELLOW}⚠${NC} Port $1 is already in use"
        return 1
    else
        echo -e "${GREEN}✓${NC} Port $1 is available"
        return 0
    fi
}

echo "Checking system requirements..."
echo

# Check required commands
PYTHON_OK=0
NODE_OK=0

if check_command python3; then
    PYTHON_VERSION=$(python3 --version)
    echo "  Version: $PYTHON_VERSION"
    PYTHON_OK=1
fi

if check_command node; then
    NODE_VERSION=$(node --version)
    echo "  Version: $NODE_VERSION"
    NODE_OK=1
fi

if check_command npm; then
    NPM_VERSION=$(npm --version)
    echo "  NPM Version: $NPM_VERSION"
fi

check_command git

echo
echo "Checking ports..."
check_port 3000  # Frontend
check_port 5000  # AI Service
check_port 8000  # Backend

echo
echo "Checking project structure..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check directories
if [ -d "$SCRIPT_DIR/frontend" ]; then
    echo -e "${GREEN}✓${NC} Frontend directory exists"
else
    echo -e "${RED}✗${NC} Frontend directory missing"
fi

if [ -d "$SCRIPT_DIR/backend" ]; then
    echo -e "${GREEN}✓${NC} Backend directory exists"
else
    echo -e "${RED}✗${NC} Backend directory missing"
fi

if [ -d "$SCRIPT_DIR/ai" ]; then
    echo -e "${GREEN}✓${NC} AI directory exists"
else
    echo -e "${RED}✗${NC} AI directory missing"
fi

# Check key files
if [ -f "$SCRIPT_DIR/frontend/package.json" ]; then
    echo -e "${GREEN}✓${NC} Frontend package.json exists"
else
    echo -e "${RED}✗${NC} Frontend package.json missing"
fi

if [ -f "$SCRIPT_DIR/backend/requirements.txt" ]; then
    echo -e "${GREEN}✓${NC} Backend requirements.txt exists"
else
    echo -e "${RED}✗${NC} Backend requirements.txt missing"
fi

if [ -f "$SCRIPT_DIR/ai/requirements.txt" ]; then
    echo -e "${GREEN}✓${NC} AI requirements.txt exists"
else
    echo -e "${RED}✗${NC} AI requirements.txt missing"
fi

echo
echo "==================================="
if [ $PYTHON_OK -eq 1 ] && [ $NODE_OK -eq 1 ]; then
    echo -e "${GREEN}✓ Setup looks good! You can run: ./start-services.sh${NC}"
else
    echo -e "${RED}✗ Please install missing requirements first${NC}"
    echo
    echo "Installation commands:"
    if [ $PYTHON_OK -eq 0 ]; then
        echo "Python 3: brew install python3"
    fi
    if [ $NODE_OK -eq 0 ]; then
        echo "Node.js: brew install node"
    fi
fi
echo "==================================="