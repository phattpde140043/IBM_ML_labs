#!/bin/bash
# Script để thiết lập biến môi trường cho Azure Storage
# Sử dụng: source setup_azure_env.sh

echo "Thiết lập biến môi trường Azure Storage Tables"
echo "=============================================="

# Phương pháp 1: Dùng Connection String
read -p "Bạn muốn dùng Connection String? (y/n): " use_conn_string

if [[ $use_conn_string == "y" || $use_conn_string == "Y" ]]; then
    read -p "Nhập Connection String: " connection_string
    export AZURE_STORAGE_CONNECTION_STRING="$connection_string"
    echo "✓ Connection String đã được thiết lập"
else
    # Phương pháp 2: Dùng Account Name & Key
    read -p "Nhập Storage Account Name: " account_name
    read -p "Nhập Storage Account Key: " account_key
    
    export AZURE_STORAGE_ACCOUNT_NAME="$account_name"
    export AZURE_STORAGE_ACCOUNT_KEY="$account_key"
    
    echo "✓ Account Name & Key đã được thiết lập"
fi

echo ""
echo "Biến môi trường hiện tại:"
if [ ! -z "$AZURE_STORAGE_CONNECTION_STRING" ]; then
    echo "  AZURE_STORAGE_CONNECTION_STRING: ***hidden***"
fi
if [ ! -z "$AZURE_STORAGE_ACCOUNT_NAME" ]; then
    echo "  AZURE_STORAGE_ACCOUNT_NAME: $AZURE_STORAGE_ACCOUNT_NAME"
fi

echo ""
echo "Bạn có thể chạy script bằng:"
echo "  python azure_tables_script.py"
echo "  hoặc"
echo "  python azure_tables_simple.py"
