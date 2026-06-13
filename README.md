# IBM ML Labs

Dự án Machine Learning của IBM Labs.

## Cấu trúc thư mục

```
IBM_ML_labs/
├── src/              # Mã nguồn chính
├── tests/            # Unit tests
├── data/             # Dữ liệu
├── main.py           # Điểm vào chính
├── requirements.txt  # Các dependencies
└── README.md         # Tài liệu
```

## Cài đặt

1. Tạo virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# hoặc
venv\Scripts\activate  # Windows
```

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

## Chạy dự án

```bash
python main.py
```

## Chạy tests

```bash
pytest tests/
```
