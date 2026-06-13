"""
Script để kết nối Azure Storage Tables, lọc bảng có tên bắt đầu với "OSP",
và cập nhật giá trị "quatas" thành "search365" cho các row có cột "Tenant"
"""

from azure.data.tables import TableServiceClient
import os
from datetime import datetime


def get_table_service_client():
    """
    Khởi tạo kết nối đến Azure Storage Tables
    
    Có 3 cách để cung cấp credentials:
    1. Connection string từ biến môi trường: AZURE_STORAGE_CONNECTION_STRING
    2. Account name & key từ biến môi trường: AZURE_STORAGE_ACCOUNT_NAME, AZURE_STORAGE_ACCOUNT_KEY
    3. Trực tiếp trong code (không khuyến khích cho production)
    """
    
    # Cách 1: Dùng connection string
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if connection_string:
        return TableServiceClient.from_connection_string(connection_string)
    
    # Cách 2: Dùng account name và key
    account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
    account_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
    if account_name and account_key:
        return TableServiceClient(
            account_url=f"https://{account_name}.table.core.windows.net",
            credential=account_key
        )
    
    # Cách 3: Nhập trực tiếp (chỉ cho testing)
    print("Vui lòng nhập thông tin Azure Storage:")
    account_name = input("Storage Account Name: ").strip()
    account_key = input("Storage Account Key: ").strip()
    
    if not account_name or not account_key:
        raise ValueError("Thiếu thông tin xác thực Azure Storage")
    
    return TableServiceClient(
        account_url=f"https://{account_name}.table.core.windows.net",
        credential=account_key
    )


def list_osp_tables(table_service_client):
    """
    Liệt kê tất cả bảng và lọc những bảng có tên bắt đầu với "OSP"
    """
    print("\n" + "="*60)
    print("DANH SÁCH CÁC BẢNG")
    print("="*60)
    
    all_tables = []
    osp_tables = []
    
    try:
        # Lấy danh sách tất cả các bảng
        for table in table_service_client.list_tables():
            table_name = table.name
            all_tables.append(table_name)
            
            if table_name.startswith("OSP"):
                osp_tables.append(table_name)
                print(f"✓ [OSP] {table_name}")
            else:
                print(f"  {table_name}")
        
        print(f"\nTổng bảng: {len(all_tables)}")
        print(f"Bảng bắt đầu với 'OSP': {len(osp_tables)}")
        
    except Exception as e:
        print(f"Lỗi khi liệt kê bảng: {e}")
        return []
    
    return osp_tables


def read_and_update_osp_tables(table_service_client, osp_tables):
    """
    Đọc dữ liệu từ các bảng OSP và cập nhật cột 'quatas' nếu có cột 'Tenant'
    """
    
    if not osp_tables:
        print("\nKhông có bảng nào bắt đầu với 'OSP'")
        return
    
    total_updated = 0
    
    for table_name in osp_tables:
        print(f"\n{'='*60}")
        print(f"XỬ LÝ BẢNG: {table_name}")
        print(f"{'='*60}")
        
        try:
            table_client = table_service_client.get_table_client(table_name=table_name)
            
            # Lấy tất cả entities từ bảng
            entities = list(table_client.query_entities(""))
            
            print(f"Tổng entities trong bảng: {len(entities)}")
            
            if not entities:
                print("Bảng trống, bỏ qua...")
                continue
            
            # Kiểm tra xem có cột 'Tenant' không
            has_tenant = 'Tenant' in entities[0]
            print(f"Có cột 'Tenant': {'✓ Có' if has_tenant else '✗ Không'}")
            
            if not has_tenant:
                print("Bảng này không có cột 'Tenant', bỏ qua...")
                continue
            
            # Xử lý từng entity
            updated_count = 0
            for entity in entities:
                if 'Tenant' in entity and 'quatas' in entity:
                    old_value = entity.get('quatas', 'N/A')
                    entity['quatas'] = 'search365'
                    
                    try:
                        # Cập nhật entity
                        table_client.update_entity(entity, mode="MERGE")
                        updated_count += 1
                        print(f"  ✓ Cập nhật PartitionKey={entity['PartitionKey']}, RowKey={entity['RowKey']}")
                        print(f"    quatas: {old_value} → search365")
                    except Exception as e:
                        print(f"  ✗ Lỗi cập nhật PartitionKey={entity['PartitionKey']}, RowKey={entity['RowKey']}: {e}")
            
            print(f"\nBảng {table_name}: Cập nhật {updated_count}/{len(entities)} entities")
            total_updated += updated_count
            
        except Exception as e:
            print(f"Lỗi khi xử lý bảng {table_name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"TỔNG KẾT")
    print(f"{'='*60}")
    print(f"Tổng entities đã cập nhật: {total_updated}")


def main():
    """
    Hàm chính
    """
    print(f"Script bắt đầu tại: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Bước 1: Kết nối đến Azure Storage Tables
        print("\n1. Đang kết nối đến Azure Storage Tables...")
        table_service_client = get_table_service_client()
        print("   ✓ Kết nối thành công")
        
        # Bước 2: Liệt kê và lọc bảng OSP
        print("\n2. Đang liệt kê các bảng...")
        osp_tables = list_osp_tables(table_service_client)
        
        # Bước 3: Đọc và cập nhật dữ liệu
        if osp_tables:
            print("\n3. Đang xử lý các bảng OSP...")
            read_and_update_osp_tables(table_service_client, osp_tables)
        
        print(f"\nScript kết thúc tại: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n✗ Lỗi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
