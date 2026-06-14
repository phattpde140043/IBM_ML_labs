#!/bin/bash

# Change to the directory where the script is located
cd "$(dirname "$0")"

VENV_DIR="venv"

# 1. Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    
    # Kích hoạt venv tạm để cài đặt
    source "$VENV_DIR/bin/activate"
    
    echo "Installing dependencies from requirements.txt (This might take a few minutes as it downloads PyTorch)..."
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
fi

# 2. Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# 4. Run the inference script
echo "Starting webcam inference..."
python webcam_inference.py

# 5. Deactivate environment when finished
deactivate
echo "Inference finished."
