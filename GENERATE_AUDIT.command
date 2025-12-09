#!/bin/bash
# Double-click this file to generate an audit for a client
# Takes about 10 minutes

cd "$(dirname "$0")"

echo "📊 Generate Audit Report"
echo ""
echo "Available clients:"
ls -1 inputs/ | grep -v "test-client"
echo ""
read -p "Enter client name: " client_name

if [ -z "$client_name" ]; then
    echo "❌ No client name provided"
    read -p "Press Enter to exit..."
    exit 1
fi

if [ ! -d "inputs/$client_name" ]; then
    echo "❌ Client folder not found: inputs/$client_name"
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "🚀 Generating audit for $client_name..."
echo "This will take about 10 minutes."
echo ""

# Activate virtual environment
source venv/bin/activate

# Generate audit
python generate_audit.py --client "$client_name"

echo ""
echo "✅ Audit complete!"
echo ""
echo "Opening output folder..."
open "output/$client_name/"

read -p "Press Enter to exit..."
