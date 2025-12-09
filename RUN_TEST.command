#!/bin/bash
# Double-click this file to run a test audit (Hades game)
# Takes about 10 minutes

cd "$(dirname "$0")"

echo "🧪 Running test audit..."
echo "This will take about 10 minutes."
echo ""

# Activate virtual environment
source venv/bin/activate

# Run test
python generate_audit.py --test

echo ""
echo "✅ Test complete!"
echo ""
echo "Check the output folder:"
open output/test-client/

read -p "Press Enter to exit..."
