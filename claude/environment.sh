#!/bin/bash
# Claude Code Environment Setup Script
# Sets up the AI Management Layer System environment

echo "🚀 Setting up AI Management Layer System..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "📥 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "⚠️  requirements.txt not found. Skipping dependency installation."
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p logs
mkdir -p memory
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/exports
mkdir -p projects

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
export MANAGEMENT_TEAM_ROOT="$(pwd)"

echo "✅ Environment setup complete!"
echo "💡 To activate the environment, run: source venv/bin/activate"
echo "💡 PYTHONPATH is set to include: $(pwd)/src"

