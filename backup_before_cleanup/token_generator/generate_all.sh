#!/bin/bash

echo "============================================================"
echo "FREE FIRE TOKEN GENERATOR - BATCH MODE"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo "💡 Install Python 3.7+ from python.org"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check dependencies
echo "[1/3] Checking dependencies..."
if ! python3 -c "import requests" &> /dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "[2/3] Generating tokens from test_credentials.txt..."
# Copy test credentials to credentials.txt
cp test_credentials.txt credentials.txt
python3 token_gen.py --batch

echo ""
echo "[3/3] Testing generated tokens..."
python3 test_token.py

echo ""
echo "============================================================"
echo "✅ COMPLETE! Check generated_tokens.json for your tokens"
echo "============================================================"
