#!/bin/bash

cd "$(dirname "$0")"

VENV_DIR="venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Installing / updating dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "Starting webcam inference (standalone, no gRPC)..."
python webcam_inference.py

deactivate
echo "Done."
