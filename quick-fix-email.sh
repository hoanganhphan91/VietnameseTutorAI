#!/bin/bash

echo "==================================="
echo "  Quick Fix - Install email-validator"
echo "==================================="

cd /Users/Shared/PearBit/VietnameseTutorAI/backend

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run ./setup-project.sh first"
    exit 1
fi

echo "Installing email-validator..."
source venv/bin/activate
pip install email-validator

echo "✅ email-validator installed successfully!"
echo "Now you can restart the backend service."