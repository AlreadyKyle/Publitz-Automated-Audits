#!/bin/bash

# Setup script for Publitz Automated Audits Tool

echo "🎮 Setting up Publitz Automated Audits Tool..."
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Install playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Create output directory
mkdir -p output

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit .env and add your ANTHROPIC_API_KEY"
    echo ""
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the app:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Add your API key to .env"
echo "  3. Run: streamlit run app.py"
echo ""
