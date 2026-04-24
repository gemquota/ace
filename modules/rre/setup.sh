#!/bin/bash

# Recursive Reinforcement Engine (RRE) Setup Script
# This script initializes the RRE dashboard and links the RRP CLI tool.

RRE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BIN_DIR="$HOME/bin"
mkdir -p "$BIN_DIR"

echo "[*] Setting up RRE (Recursive Reinforcement Engine)..."

# 1. Link the ace-rrp CLI tool
echo "[*] Linking ace-rrp CLI tool..."
ln -sf "$RRE_DIR/bin/ace-rrp" "$BIN_DIR/ace-rrp"
chmod +x "$RRE_DIR/bin/ace-rrp"

# 2. Install dependencies (if python is available)
if command -v pip &> /dev/null; then
    echo "[*] Installing RRE dependencies..."
    pip install fastapi uvicorn pydantic requests --quiet
else
    echo "[!] pip not found. Please install requirements manually: fastapi, uvicorn, pydantic, requests."
fi

# 3. Initialize data directories
mkdir -p "$RRE_DIR/data"
if [ ! -f "$RRE_DIR/data/sessions.json" ]; then
    echo "{}" > "$RRE_DIR/data/sessions.json"
fi

echo "[✓] RRE Setup complete. You can now use 'ace-rrp' in your terminal."
