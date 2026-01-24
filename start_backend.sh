#!/bin/bash

# Quick Start Script for SilverSentinel Backend
# Runs the complete backend setup and demo

set -e

echo "🪙 SilverSentinel Backend - Quick Start"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env and add your API keys"
    echo ""
fi

# Initialize database
echo "💾 Initializing database..."
cd backend
python database.py

# Seed demo data
echo "🌱 Seeding demo data..."
python seed_demo_data.py

# Run tests (optional)
read -p "🧪 Run integration tests? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running tests..."
    pytest tests/test_integration.py -v
fi

echo ""
echo "="*50
echo "✅ Backend Setup Complete!"
echo "="*50
echo ""
echo "🚀 Starting FastAPI server..."
echo "   API docs: http://localhost:8000/docs"
echo "   Health check: http://localhost:8000/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
