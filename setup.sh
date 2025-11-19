#!/bin/bash

# RAiDesk Server Setup Script

echo "🔧 Setting up RAiDesk Backend Server..."

# Check if uv is installed
echo "📌 Checking uv installation..."
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed!"
    echo "Please install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo "✅ uv is installed"

# Check Python version
echo "📌 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment using uv
echo "📦 Creating virtual environment with uv..."
uv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies using uv
echo "📥 Installing dependencies with uv..."
uv pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gpt-oss

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# LangSmith (Optional - for debugging)
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=your_api_key_here
# LANGCHAIN_PROJECT=raidesk
EOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Check Ollama installation
echo "🔍 Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed!"
    echo "Please install Ollama from: https://ollama.ai"
else
    echo "✅ Ollama is installed"
    
    # Check if GPT-OSS model is available
    echo "🔍 Checking GPT-OSS model..."
    if ollama list | grep -q "gpt-oss"; then
        echo "✅ GPT-OSS model is available"
    else
        echo "⚠️  GPT-OSS model not found"
        echo "Pulling GPT-OSS model..."
        ollama pull gpt-oss
    fi
fi

# Mark as installed
touch .venv/.installed

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  ./run.sh"
echo ""
echo "Or manually:"
echo "  source .venv/bin/activate"
echo "  python app/main.py"
echo ""
echo "API Documentation will be available at:"
echo "  http://localhost:8000/docs"
echo ""

