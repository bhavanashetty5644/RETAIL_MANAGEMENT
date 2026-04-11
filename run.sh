#!/bin/bash
echo "╔══════════════════════════════════════════╗"
echo "║   RetailOS v2 — Starting up...           ║"
echo "╚══════════════════════════════════════════╝"

# Create virtualenv if needed
if [ ! -d "venv" ]; then
  echo "[1/3] Creating virtual environment..."
  python3 -m venv venv
fi

echo "[2/3] Installing dependencies..."
source venv/bin/activate
pip install -q -r requirements.txt

echo "[3/3] Starting RetailOS..."
echo ""
echo "  ✓  Open browser → http://127.0.0.1:5000"
echo "  ✓  First time?  → http://127.0.0.1:5000/register"
echo "  ✗  Stop:        Ctrl+C"
echo ""
python app.py
