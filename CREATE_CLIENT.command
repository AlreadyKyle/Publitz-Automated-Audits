#!/bin/bash
# Double-click this file to create a new client folder
# You'll be asked for the client name

cd "$(dirname "$0")"

echo "📁 Create New Client Folder"
echo ""
read -p "Enter client name (lowercase, no spaces): " client_name

if [ -z "$client_name" ]; then
    echo "❌ No client name provided"
    read -p "Press Enter to exit..."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Create client folder
python generate_audit.py --create-example "$client_name"

echo ""
echo "✅ Client folder created!"
echo ""
echo "Next steps:"
echo "1. Open the inputs/$client_name/ folder"
echo "2. Fill in the 4 files with client info"
echo "3. Double-click GENERATE_AUDIT.command"
echo ""
echo "Opening folder now..."
open "inputs/$client_name/"

read -p "Press Enter to exit..."
