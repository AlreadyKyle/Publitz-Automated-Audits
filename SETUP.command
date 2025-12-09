#!/bin/bash
# Double-click this file to set up the audit system
# It will open Terminal automatically

cd "$(dirname "$0")"

echo "🚀 Setting up Publitz Audit System..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python from python.org"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ Python 3 found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment exists"
fi

# Activate and install
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Double-click RUN_TEST.command to test the system"
echo "2. Or double-click CREATE_CLIENT.command to start a real audit"
echo ""
read -p "Press Enter to exit..."
