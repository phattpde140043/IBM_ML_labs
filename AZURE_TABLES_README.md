# Azure Storage Tables Script

Script Python để kết nối Azure Storage Tables, lọc bảng có tên bắt đầu với "OSP", và cập nhật dữ liệu.

## Chức năng

1. **Kết nối Azure Storage** - Kết nối đến Azure Storage Tables
2. **Liệt kê bảng** - Liệt kê tất cả các bảng và lọc những bảng bắt đầu với "OSP"
3. **Đọc & Cập nhật dữ liệu** - Đọc dữ liệu từ các bảng OSP và cập nhật giá trị cột `quatas` thành `search365` cho các row có cột `Tenant`

## Yêu cầu

### 1. Cài đặt Azure SDK

```bash
pip install azure-data-tables
```

Hoặc cài từ `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Cấu hình xác thực Azure Storage

Có 3 cách để xác thực:

#### Cách 1: Dùng Connection String (Khuyến khích)

Đặt biến môi trường:

```bash
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=<your-account>;AccountKey=<your-key>;EndpointSuffix=core.windows.net"
```

Hoặc trên Windows (PowerShell):

```powershell
$env:AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=<your-account>;AccountKey=<your-key>;EndpointSuffix=core.windows.net"
```

#### Cách 2: Dùng Account Name & Key

Đặt biến môi trường:

```bash
export AZURE_STORAGE_ACCOUNT_NAME="your-account-name"
export AZURE_STORAGE_ACCOUNT_KEY="your-account-key"
```

#### Cách 3: Nhập trực tiếp

Script sẽ yêu cầu nhập Storage Account Name và Key nếu không tìm thấy biến môi trường.

## Cách sử dụng

### Chạy script

```bash
python azure_tables_script.py
```

### Output ví dụ

```
Script bắt đầu tại: 2026-04-12 10:30:45

1. Đang kết nối đến Azure Storage Tables...
   ✓ Kết nối thành công

2. Đang liệt kê các bảng...
============================================================
DANH SÁCH CÁC BẢNG
============================================================
✓ [OSP] OSPTable1
✓ [OSP] OSPConfig
  OtherTable
  MetadataTable

Tổng bảng: 4
Bảng bắt đầu với 'OSP': 2

3. Đang xử lý các bảng OSP...
============================================================
XỬ LÝ BẢNG: OSPTable1
============================================================
Tổng entities trong bảng: 5
Có cột 'Tenant': ✓ Có
  ✓ Cập nhật PartitionKey=tenant1, RowKey=row001
    quatas: old_value → search365
  ✓ Cập nhật PartitionKey=tenant1, RowKey=row002
    quatas: old_value → search365

Bảng OSPTable1: Cập nhật 2/5 entities

...

============================================================
TỔNG KẾT
============================================================
Tổng entities đã cập nhật: 5

Script kết thúc tại: 2026-04-12 10:30:50
```

## Tìm Azure Storage Connection String

### Từ Azure Portal

1. Vào **Azure Portal** (https://portal.azure.com)
2. Tìm và chọn **Storage accounts**
3. Chọn Storage account của bạn
4. Vào **Access keys** trên menu bên trái
5. Copy **Connection string** từ key1 hoặc key2

### Từ Azure CLI

```bash
az storage account show-connection-string --name <storage-account-name> --resource-group <resource-group-name>
```

## Lưu ý

- **Backup dữ liệu** trước khi chạy script để tránh mất dữ liệu
- Script chỉ cập nhật entities có cả cột `Tenant` và `quatas`
- Nếu cột `quatas` không tồn tại, nó sẽ được tạo tự động
- Mỗi entity có `PartitionKey` và `RowKey` để xác định duy nhất

## Sửa đổi script

Bạn có thể sửa đổi logic cập nhật trong hàm `read_and_update_osp_tables`:

```python
# Ví dụ: Cập nhật based on điều kiện khác
if entity.get('Tenant') == 'specific_tenant':
    entity['quatas'] = 'search365'
    table_client.update_entity(entity, mode="MERGE")
```

## Xử lý lỗi

Nếu gặp lỗi authentication:
- Kiểm tra Connection String hoặc Account Key có đúng không
- Đảm bảo Storage account đang hoạt động
- Kiểm tra quyền truy cập

Nếu gặp lỗi timeout:
- Kiểm tra kết nối mạng
- Giảm số lượng entities xử lý cùng lúc

## Liên hệ

Để tìm hiểu thêm về Azure Storage Tables API, xem:
- https://learn.microsoft.com/en-us/azure/cosmos-db/table/
- https://learn.microsoft.com/en-us/python/api/overview/azure/data-tables-readme
