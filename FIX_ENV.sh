#!/bin/bash
# Fix .env file formatting - run this on your Mac

cd ~/Documents/GitHub/Publitz-Automated-Audits

# Backup current .env
cp .env .env.backup

# Fix the spacing issue
sed -i '' 's/ANTHROPIC_API_KEY = "/ANTHROPIC_API_KEY="/g' .env
sed -i '' 's/RAWG_API_KEY = "/RAWG_API_KEY="/g' .env

echo "✅ Fixed .env file formatting"
echo "   Backup saved to .env.backup"
echo ""
echo "Run the test now:"
echo "  source venv/bin/activate"
echo "  python generate_audit.py --test"
