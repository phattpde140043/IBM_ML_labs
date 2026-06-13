"""
Script tối giản - Kết nối Azure Storage Tables và cập nhật dữ liệu OSP
(Sử dụng phiên bản này nếu bạn muốn code ngắn gọn hơn)
"""

from azure.data.tables import TableServiceClient
import os


def main():
    # 1. Kết nối Azure Storage Tables
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING') or input("Connection String: ")
    table_service_client = TableServiceClient.from_connection_string(connection_string)
    
    # 2. Lấy danh sách bảng bắt đầu với "OSP"
    osp_tables = [table.name for table in table_service_client.list_tables() 
                  if table.name.startswith("OSP")]
    
    print(f"Tìm thấy {len(osp_tables)} bảng OSP: {osp_tables}\n")
    
    # 3. Xử lý từng bảng OSP
    total_updated = 0
    for table_name in osp_tables:
        print(f"Xử lý bảng: {table_name}")
        table_client = table_service_client.get_table_client(table_name=table_name)
        
        # Lấy tất cả entities
        entities = list(table_client.query_entities(""))
        
        for entity in entities:
            # Kiểm tra có cột "Tenant" và cập nhật "quatas"
            if "Tenant" in entity:
                entity['quatas'] = 'search365'
                table_client.update_entity(entity, mode="MERGE")
                total_updated += 1
                print(f"  ✓ Cập nhật: {entity.get('PartitionKey')}/{entity.get('RowKey')}")
        
        print(f"  {table_name}: Cập nhật {len([e for e in entities if 'Tenant' in e])} rows\n")
    
    print(f"✓ Tổng cộng cập nhật {total_updated} rows")


if __name__ == "__main__":
    main()
