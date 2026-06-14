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
    
    # Biên dịch file giao thức gRPC
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. yolo.proto
    deactivate
fi

# 2. Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# 3. Khởi chạy Server gRPC ở chế độ ngầm (Background)
echo "Starting AI Model Serving (Server)..."
python serve_grpc.py &
SERVER_PID=$!

# Đợi 3 giây để Server nạp model YOLO vào GPU
sleep 3

# 4. Khởi chạy Client lấy dữ liệu Camera
echo "Starting Stream Ingestion (Client)..."
python ingest_grpc.py

# 5. Dọn dẹp: Tắt Server khi Client đóng
kill $SERVER_PID
wait $SERVER_PID 2>/dev/null
deactivate
echo "Inference finished."
