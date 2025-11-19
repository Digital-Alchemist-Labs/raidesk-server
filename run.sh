#!/bin/bash

# RAiDesk Server Startup Script

echo "🚀 Starting RAiDesk Backend Server..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed!"
    echo "Please install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment with uv..."
    uv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies if needed
if [ ! -f ".venv/.installed" ]; then
    echo "📥 Installing dependencies with uv..."
    uv pip install -r requirements.txt
    touch .venv/.installed
fi

# Check if Ollama is running
echo "🔍 Checking Ollama connection..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️  Warning: Ollama is not running!"
    echo "Please start Ollama: ollama serve"
    echo "And ensure GPT-OSS model is available: ollama pull gpt-oss"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Using default configuration."
fi

# Start the server
echo "✅ Starting FastAPI server..."
python app/main.py

