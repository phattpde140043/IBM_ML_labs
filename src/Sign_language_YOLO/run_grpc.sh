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

echo "Compiling gRPC proto..."
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. yolo.proto

echo "Starting Accelerated AI Server (Lab 2 — OpenVINO/ONNX)..."
python -m inference_service.server_accelerated &
SERVER_PID=$!

echo "Waiting for server to be ready..."
python - <<'EOF'
import grpc, sys
channel = grpc.insecure_channel("localhost:50051")
try:
    grpc.channel_ready_future(channel).result(timeout=30)
    print("Server is ready!")
except grpc.FutureTimeoutError:
    print("ERROR: Server did not start within 30s.")
    sys.exit(1)
EOF

echo "Starting Stream Ingestion Client..."
python ingest_grpc.py

kill $SERVER_PID
wait $SERVER_PID 2>/dev/null
deactivate
echo "Done."
