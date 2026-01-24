#!/bin/bash

# SilverSentinel Setup Script
# Automated environment setup for the hackathon project

set -e  # Exit on error

echo "🪙 SilverSentinel Setup Script"
echo "================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [[ $(echo -e "$python_version\n$required_version" | sort -V | head -n1) != "$required_version" ]]; then
    echo "❌ Python 3.11+ required, found $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"
echo ""

# Check if Ollama is installed (optional)
echo "📋 Checking Ollama installation (optional for local fallback)..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama found"
    
    # Check if user has any models
    model_count=$(ollama list | tail -n +2 | wc -l | tr -d ' ')
    if [ "$model_count" -gt 0 ]; then
        echo "✅ Found $model_count Ollama model(s)"
        echo "   Will use these as local fallback for text generation"
    else
        echo "⚠️  No Ollama models found. Download one with:"
        echo "   ollama pull llama3.2"
    fi
else
    echo "⚠️  Ollama not found (optional)"
    echo "   System will work with Groq API only"
    echo "   Install later: https://ollama.ai"
fi
echo ""

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
cd "$(dirname "$0")"

if [ -d "venv" ]; then
    echo "⚠️ Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo "✅ Dependencies installed"
echo ""

# Create environment file if not exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️ IMPORTANT: Edit .env and add your API keys!"
    echo ""
fi

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data

# Initialize database
echo "💾 Initializing database..."
cd backend
python database.py
cd ..

echo "✅ Database initialized"
echo ""

# Test orchestrator
echo "🧪 Testing multi-model orchestrator..."
cd backend
python orchestrator.py
cd ..

echo ""
echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Edit .env and add your API keys:"
echo "   - GROQ_API_KEY (Required): https://console.groq.com"
echo "   - GEMINI_API_KEY (Optional - fallback): https://aistudio.google.com/apikey"
echo "   - NEWS_API_KEY (Optional): https://newsapi.org"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the backend:"
echo "   ./start_backend.sh"
echo ""
echo "🎯 Happy hacking!"
