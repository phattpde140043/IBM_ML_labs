# SQL Tuning — Microsoft SQL Server: Performance Tuning Essentials

> Nguồn: Coursera — Microsoft SQL Server: Performance Tuning Essentials  
> Mục đích: Tối ưu hiệu năng database — giảm downtime, tăng responsiveness

---

## Mind Map tổng quan

```
SQL Server Performance Tuning
│
├── 🎯 Đối tượng
│   ├── Database Administrators
│   ├── IT Professionals
│   ├── Data Analysts
│   └── Technical Managers
│
├── 📚 3 Module chính
│   ├── 1. Fundamentals — Query tuning & Indexing strategies
│   ├── 2. Advanced Techniques — Monitoring & Troubleshooting
│   └── 3. Maintenance & Optimization — Backup, Security, Case studies
│
├── 🏆 Learning Outcomes
│   ├── Analyze & tune SQL queries → giảm latency
│   ├── Evaluate index & maintenance strategies
│   ├── Monitor & troubleshoot SQL Server issues
│   └── Apply best practices → consistent & reliable ops
│
└── 🛠️ Phương pháp học
    ├── Hands-on exercises
    ├── Case studies
    ├── Peer discussions
    └── Focus: Indexing + Execution Plans
```

---

## Tóm tắt nội dung

### Mục tiêu khóa học
Trang bị kỹ năng **performance optimization** cho SQL Server, tập trung vào:
- **Query tuning** — phân tích và tối ưu câu truy vấn
- **Indexing strategies** — chiến lược đánh index hiệu quả
- **Troubleshooting** — chẩn đoán và xử lý sự cố hiệu năng

### Yêu cầu đầu vào
- Hiểu cơ bản SQL query language
- Có kiến thức nền về SQL Server và database management

---

## Nội dung chi tiết

### Giới thiệu khóa học — Why SQL Tuning Matters

#### Bối cảnh kinh doanh
- Ứng dụng chậm → ảnh hưởng trực tiếp đến doanh thu
- **Nguyên nhân thực sự**: không phải app mà là cách app tương tác với database
- SQL Server optimization = không chỉ về tốc độ mà còn về **trải nghiệm người dùng** và **kết quả kinh doanh**

#### Instructor — Luca Berton
- 15+ năm kinh nghiệm trong ngành tech
- Kinh nghiệm từ startup nhỏ đến Fortune 500
- Phương pháp: **hands-on**, chia nhỏ khái niệm phức tạp thành bài học dễ hiểu

#### 3 Trụ cột chính của khóa học

| # | Chủ đề | Mục tiêu |
|---|--------|----------|
| 1 | **Query Performance** | Phân tích & tối ưu SQL queries → giảm latency |
| 2 | **Indexing Strategies** | Cân bằng index → database nhanh & hiệu quả |
| 3 | **Database Maintenance** | Kỹ thuật bảo trì để duy trì SQL Server ổn định |

---

### Module 1 — Fundamentals of SQL Server Query Performance Optimization

#### 1.1 Tại sao Query Tuning quan trọng với kinh doanh?

> **Core insight**: Vấn đề không phải ở app — mà ở cách app giao tiếp với database.

**Tác động thực tế của slow queries:**
- Mất khách hàng (họ chuyển sang đối thủ)
- Ảnh hưởng uy tín thương hiệu
- Chậm ra quyết định kinh doanh
- Tăng chi phí vận hành

#### 1.2 Real-world Use Cases

| Use Case | Công ty | Vấn đề | Giải pháp | Kết quả |
|----------|---------|---------|-----------|---------|
| **Reporting** | Walmart | Daily sales report chạy chậm → quyết định chậm | Tối ưu query, loại bỏ unnecessary joins | Minutes → Seconds |
| **Real-time data** | Chase Bank | App check balance hiển thị spinning wheel | Optimize queries cho real-time response | Trải nghiệm mượt, giữ chân khách hàng |
| **Logistics** | FedEx | Tracking shipment chậm → delay, miscommunication | Fine-tune queries cập nhật & truy vấn data | Giảm chi phí, giao hàng đúng hạn |

#### Mind map — Query Tuning Business Impact

```
Query Tuning
│
├── 🏪 Retail (Walmart)
│   ├── Vấn đề: Slow reporting queries
│   ├── Fix: Remove unnecessary JOINs, tighten workflows
│   └── Impact: Faster decisions, agile business
│
├── 🏦 Banking (Chase)
│   ├── Vấn đề: Real-time data lag trong mobile app
│   ├── Fix: Optimize queries cho low-latency response
│   └── Impact: Customer retention, competitive advantage
│
└── 🚚 Logistics (FedEx)
    ├── Vấn đề: Shipment tracking queries chậm
    ├── Fix: Fine-tune UPDATE & SELECT queries
    └── Impact: Giảm cost, cải thiện SLA
```

---

#### 1.3 Query Execution Plans — Blueprint của Query

> **Core insight**: Execution plan = roadmap SQL Server dùng để thực thi query. Đọc được plan → tìm được bottleneck.

**Execution plan là gì?**
- SQL Server breakdown query thành từng bước để lấy data
- Xem bằng SSMS: **Display Estimated Execution Plan**
- Phân tích plan → phát hiện inefficiency → tối ưu

---

**Key Operators cần chú ý:**

| Operator | Ý nghĩa | Dấu hiệu xấu | Hướng xử lý |
|----------|---------|--------------|-------------|
| **Table Scan** | Quét toàn bộ bảng | Không có index phù hợp | Thêm index → chuyển thành Index Seek |
| **Index Seek** | Dùng index để tìm data trực tiếp | ✅ Tốt | Giữ nguyên |
| **Nested Loops** | JOIN lặp từng row | Chậm với large tables | Rewrite sang Hash Join / Merge Join |

---

**Quy trình tối ưu từ Execution Plan:**

```
1. Chạy query → Xem Execution Plan
       ↓
2. Phát hiện operator xấu (Table Scan / Nested Loop lớn)
       ↓
3. Hành động:
   ├── Table Scan → Thêm index phù hợp (selective hơn)
   ├── Nested Loop + large table → Đổi sang Hash Join / Merge Join
   └── Index không selective → Tạo index cụ thể hơn cho query
       ↓
4. Chạy lại → So sánh execution plan mới
```

#### Mind map — Execution Plans

```
Execution Plan
│
├── Mục đích
│   ├── Roadmap của query
│   ├── Phát hiện bottleneck
│   └── Đánh giá hiệu quả index
│
├── Key Operators
│   ├── Table Scan ❌ → cần index
│   ├── Index Seek ✅ → hiệu quả
│   └── Nested Loop ⚠️ → xem xét Join type
│
└── Optimization Actions
    ├── Thêm / sửa index
    ├── Rewrite query (JOIN strategy)
    └── Adjust SQL Server config
```

### Module 2 — Advanced SQL Server Performance Techniques

#### 2.0 Troubleshooting Common Performance Problems

> **Analogy**: SQL Server như một ngã tư bận rộn — khi tắc nghẽn ở một điểm, toàn bộ hệ thống tê liệt.

**3 loại bottleneck phổ biến:**

| Loại | Triệu chứng | Công cụ phát hiện | Giải pháp |
|------|------------|-------------------|-----------|
| **CPU** | CPU luôn 100% | Windows Task Manager, Activity Monitor | Optimize queries, upgrade CPU, scale out |
| **Database** | Report chậm, deadlock, scan full table | Execution Plan, Profiler | Tune queries, thêm index, split table, rebuild index, update stats |
| **Network** | App cloud phản hồi chậm dù DB & app ổn | Network diagnostic tools | Nâng cấp hạ tầng, dùng load balancer, ưu tiên traffic |

**Quy trình xử lý bottleneck:**
```
1. Monitor resource usage (CPU / Memory / Disk / Network)
2. Xác định nguồn gốc bottleneck
3. Fix:
   ├── CPU    → optimize query hoặc upgrade hardware
   ├── DB     → index, query rewrite, partition, maintenance
   └── Network → diagnostic tools, load balancer, QoS
4. Hiểu root cause → ngăn tái phát
```

---

#### 2.1 Introduction to SQL Server Performance Tuning (sqldbaschool.com)

> **Core insight**: "Performance is not a feeling. It's a measurement." — Chuyển "database chậm" thành con số đo được.

**4 Performance Metrics cần đo:**

| Metric | Định nghĩa |
|--------|-----------|
| **Latency** | Response time per request |
| **Throughput** | Requests completed per second |
| **Concurrency** | Số users đồng thời |
| **Resource Utilization** | CPU / Memory / Disk / Network |

> Thêm: **Stability & Predictability** — hệ thống phải ổn định, không chỉ nhanh.

---

**5 Nhóm Root Cause của performance vấn đề:**

```
Root Causes
├── 1. Workload changes     → more users, new features, data growth
├── 2. Query patterns       → missing indexes, poor joins, parameter sniffing
├── 3. Resource constraints → CPU / memory / storage saturation
├── 4. Concurrency & blocking → transaction isolation, lock escalation
└── 5. Configuration gaps   → stale statistics, fragmentation, bad settings
```

---

**6-Step Tuning Workflow:**

```
1. Observe  → quan sát hệ thống và workload
2. Measure  → đo bằng metrics phù hợp
3. Diagnose → xác định đúng bottleneck
4. Change   → thay đổi MỘT biến duy nhất
5. Validate → kiểm tra improvement và side effects
6. Document → ghi lại findings, ngăn regression tái xảy ra
```

**Tuning Principles (Professional):**
- Không đoán mò — dùng evidence
- Thiết lập **baseline trước** khi thay đổi bất cứ thứ gì
- Chỉ thay đổi **một yếu tố tại một thời điểm**
- Context quan trọng: MAXDOP và memory config phụ thuộc vào từng tình huống
- Luôn test với **concurrency** thực tế

**3 Tuning Layers:**

```
Server Level   → cấu hình OS, hardware, SQL Server settings
Database Level → index, statistics, partitioning, maintenance
Query Level    → execution plan, rewrite query, join strategy
```

#### 2.2 Monitoring & Troubleshooting — 3 công cụ chính

> **Workflow**: Activity Monitor (phát hiện) → SQL Server Profiler (đào sâu) → Database Engine Tuning Advisor (sửa)

---

**① Activity Monitor** — Real-time overview

Mở: SSMS → chuột phải Server → Activity Monitor

| Section | Thông tin hiển thị |
|---------|-------------------|
| **Processes** | Active sessions + resource usage |
| **Resource Waits** | Tasks đang chờ resource → phát hiện bottleneck |
| **Data File I/O** | Read/Write ops → phát hiện disk issues |

- Sort theo CPU hoặc I/O để tìm process ngốn nhiều tài nguyên
- **Mục tiêu**: phát hiện nhanh process gây slowdown trước khi leo thang

---

**② SQL Server Profiler** — Trace & phân tích query

Mở: SSMS → Tools → SQL Server Profiler → File → New Trace

```
Các bước:
1. Chọn template: Standard (Default)
2. Click Run → để trace chạy vài phút
3. Stop trace (nút đỏ)
4. Filter kết quả: chuột phải cột Duration → Column Filter
5. Tìm query có Duration cao hoặc CPU cao
6. Lưu trace file → dùng cho Tuning Advisor
```

- **Mục tiêu**: xác định chính xác query nào đang gây slowdown

---

**③ Database Engine Tuning Advisor** — Phân tích & đề xuất fix

Mở: SSMS → Tools → Database Engine Tuning Advisor → File → New Session

```
Các bước:
1. Workload: chọn trace file từ SQL Server Profiler
2. Chọn database cần tune
3. Click Start Analysis
4. Review recommendations (thêm index, partition table, tạo statistics)
5. Apply: chuột phải recommendation → Apply to Database
6. Re-evaluate: chạy lại query chậm + kiểm tra Activity Monitor
```

- **Mục tiêu**: nhận gợi ý cụ thể và apply thay đổi có tác động thực sự

---

#### Mind map — Monitoring & Troubleshooting

```
Monitoring & Troubleshooting
│
├── 🔍 Activity Monitor (SSMS built-in)
│   ├── Processes → resource usage per session
│   ├── Resource Waits → bottleneck detection
│   └── Data File I/O → disk performance
│
├── 🎯 SQL Server Profiler
│   ├── Capture trace → filter by Duration/CPU
│   ├── Identify slow queries
│   └── Save trace file → input cho Tuning Advisor
│
└── 🛠️ Database Engine Tuning Advisor
    ├── Input: trace file từ Profiler
    ├── Output: recommendations (index, partition, stats)
    └── Apply → re-evaluate với Activity Monitor
```

---

#### Mind map — Performance Tuning Methodology

```
SQL Server Performance Tuning
│
├── 📏 Đo lường (Metrics)
│   ├── Latency
│   ├── Throughput
│   ├── Concurrency
│   └── Resource Utilization
│
├── 🔍 Root Causes (5 nhóm)
│   ├── Workload changes
│   ├── Query patterns
│   ├── Resource constraints
│   ├── Concurrency & blocking
│   └── Configuration gaps
│
├── 🔄 Workflow (6 bước)
│   └── Observe → Measure → Diagnose → Change → Validate → Document
│
└── 🏗️ Tuning Layers (3 tầng)
    ├── Server
    ├── Database
    └── Query
```

### Module 3 — Database Maintenance and Optimization

> **Analogy**: SQL Server như một khu vườn — cần chăm sóc thường xuyên để không bị "cỏ dại" (fragmentation, stale stats, bloated tables) lấn át.

#### 3.1 Rebuild & Reorganize Indexes

| Thao tác | Khi nào dùng | Cách thực hiện trong SSMS |
|----------|-------------|--------------------------|
| **Rebuild** | Fragmentation cao (>30%) | SSMS → Table → Indexes → chuột phải → Rebuild |
| **Reorganize** | Fragmentation trung bình (5-30%) | SSMS → Table → Indexes → chuột phải → Reorganize |

- **Rebuild**: toàn bộ index được xây lại từ đầu — nặng hơn nhưng triệt để
- **Reorganize**: defragment tại chỗ — nhẹ hơn, không lock bảng lâu

---

#### 3.2 Database Consistency Check

```sql
-- Kiểm tra toàn vẹn dữ liệu (integrity check)
DBCC CHECKDB ('pubs');
```
- Phát hiện corruption trong data structures
- Nếu có lỗi: repair database hoặc restore từ backup

---

#### 3.3 Update Statistics

```sql
-- Cập nhật statistics cho một bảng cụ thể
UPDATE STATISTICS authors;

-- Cập nhật statistics toàn bộ database
EXEC sp_updatestats;
```
- Statistics lỗi thời → SQL Server chọn sai execution plan → query chậm
- Sau khi update: chạy lại query để so sánh execution time

---

#### 3.4 Table Partitioning

> Chia bảng lớn thành nhiều phân vùng → SQL Server chỉ quét partition liên quan (**Partition Pruning**) → giảm I/O.

**Bước 1 — Tạo Partition Function:**
```sql
CREATE PARTITION FUNCTION MyPartitionFunction (int)
AS RANGE LEFT FOR VALUES (10000, 20000, 30000);
-- Chia data thành 4 vùng: ≤10000 | 10001-20000 | 20001-30000 | >30000
```

**Bước 2 — Tạo Partition Scheme:**
```sql
CREATE PARTITION SCHEME MyPartitionScheme
AS PARTITION MyPartitionFunction
TO ([PRIMARY], [PRIMARY], [PRIMARY], [PRIMARY]);
```

**Bước 3 — Kiểm tra Partition Function:**
```sql
USE pubs;
SELECT * FROM sys.partition_functions;
```

**Bước 4 — Áp dụng cho bảng:**
```sql
CREATE TABLE MyLargeTable_Partitioned (
    Id      int           NOT NULL PRIMARY KEY,
    Name    varchar(50)   NOT NULL,
    Age     int           NOT NULL,
    Salary  decimal(10,2) NOT NULL
) ON MyPartitionScheme(Id);
```

**Bước 5 — Query tận dụng Partition Pruning:**
```sql
-- SQL Server chỉ quét partition chứa Id 10000-20000, bỏ qua phần còn lại
SELECT * FROM MyLargeTable_Partitioned
WHERE Id BETWEEN 10000 AND 20000;
```

#### 3.5 Database Maintenance Best Practices (Tổng hợp)

> **Stats đáng nhớ**: Poorly optimized DB có thể làm chậm query tới 200%. 60% công ty mất data sẽ đóng cửa trong 6 tháng.

**3 trụ cột maintenance:**

**① Tối ưu cấu trúc Database**
- Kiểm tra và tối ưu index thường xuyên
- Thêm index vào các cột được query nhiều nhất
- ⚠️ Đừng over-index: quá nhiều index làm chậm INSERT/UPDATE

**② Backup định kỳ**

Dùng **3 loại backup kết hợp**:

| Loại | Lưu gì | Tần suất |
|------|--------|---------|
| **Full Backup** | Toàn bộ database | Hàng tuần |
| **Differential Backup** | Chỉ thay đổi từ lần Full cuối | Hàng ngày |
| **Transaction Log Backup** | Từng transaction | Mỗi giờ (hoặc thường xuyên hơn) |

- Đặt automated backup chạy ngoài giờ cao điểm (đêm khuya)
- **Quan trọng**: Test backup thường xuyên — backup không test = backup không tồn tại
- Không có backup = mất data khi crash → downtime kéo dài, mất business

**③ Quản lý Index Fragmentation**

| Mức fragmentation | Hành động | Lý do |
|-------------------|-----------|-------|
| **10% – 30%** | **Reorganize** | Nhanh hơn, làm được thường xuyên |
| **> 30%** | **Rebuild** | Triệt để hơn, nên chạy ngoài giờ cao điểm |

---

#### 3.6 Backup & Restore Strategy — Deep Dive

> **Stats**: 93% công ty mất data lớn → phá sản trong 1 năm. 23% data loss do lỗi con người.

**2 chỉ số quan trọng nhất trong backup planning:**

| Chỉ số | Định nghĩa | Ví dụ |
|--------|-----------|-------|
| **RTO** (Recovery Time Objective) | Thời gian tối đa được phép để restore | "Hệ thống phải online lại trong 2 giờ" |
| **RPO** (Recovery Point Objective) | Lượng data tối đa được phép mất | "Không mất quá 1 giờ transaction" |

---

**① Tạo Backup trong SSMS:**
```
SSMS → Object Explorer → chuột phải Database
→ Tasks → Back Up
→ Chọn loại: Full / Differential / Transaction Log
→ Chọn destination → OK
```
Tự động hóa: dùng **SQL Server Agent** để schedule backup ngoài giờ cao điểm.
Lưu nhiều nơi: **on-site + cloud** (tránh mất do thiên tai/physical damage).

---

**② Tối ưu tốc độ Backup & Restore:**
- **Bật Backup Compression** (SSMS → Backup Options) → giảm kích thước file backup
- **Differential Backup** thay vì Full mỗi ngày → chỉ lưu data thay đổi
- **Filegroup Backup** cho DB lớn → backup phần critical trước → restore nhanh hơn

---

**③ Đảm bảo khả năng Recovery:**

```
SSMS → chuột phải DB → Tasks → Restore → Database
→ Chọn backup file
→ Chọn destination: TEST ENVIRONMENT (không restore lên production!)
→ Sau khi restore: verify data integrity
```

**Checklist Recovery:**
- [ ] Tạo test environment riêng để test restore
- [ ] Verify database hoạt động đúng sau restore
- [ ] Document từng bước + vấn đề gặp phải
- [ ] Share tài liệu với team → cả team biết quy trình

---

#### Mind map — Database Maintenance

```
Database Maintenance
│
├── 🔧 Index Management
│   ├── Rebuild     → Fragmentation > 30%
│   └── Reorganize  → Fragmentation 5–30%
│
├── 🏥 Consistency Check
│   └── DBCC CHECKDB → phát hiện corruption
│
├── 📊 Statistics
│   ├── UPDATE STATISTICS <table>
│   └── EXEC sp_updatestats (toàn DB)
│
├── 🗂️ Table Partitioning
│   ├── Partition Function → định nghĩa ranges
│   ├── Partition Scheme   → map → filegroups
│   └── Partition Pruning  → chỉ scan partition cần thiết
│
└── 💾 Backup & Recovery
    ├── RTO → thời gian restore tối đa
    ├── RPO → lượng data loss tối đa chấp nhận
    ├── Full + Differential + Transaction Log
    ├── Backup Compression → giảm size
    ├── Filegroup Backup → restore nhanh phần critical
    └── Test Restore → luôn dùng test environment
```

---

---

## Module 4 — Security Best Practices

> **Analogy**: Database như Federal Reserve — tài sản quý giá nhất, phải có nhiều lớp bảo vệ.

### 4.1 Securing Database Access

**Nguyên tắc Least Privilege** — chỉ cấp quyền tối thiểu cần thiết:

| Practice | Chi tiết |
|----------|---------|
| **Strong passwords** | Mật khẩu mạnh, duy nhất cho mọi account, đổi định kỳ |
| **RBAC** (Role-Based Access Control) | Mỗi user chỉ có quyền đúng với công việc của họ |
| **MFA** (Multi-Factor Authentication) | Thêm lớp xác thực thứ 2 để ngăn tài khoản bị chiếm |

### 4.2 Data Encryption

| Loại | Áp dụng cho | Công nghệ |
|------|------------|-----------|
| **Encryption at Rest** | Data lưu trong database | TDE (Transparent Data Encryption) |
| **Encryption in Transit** | Data di chuyển giữa DB và app | SSL/TLS |

- Quản lý **encryption keys** an toàn + cập nhật định kỳ
- Hacker lấy được data đã mã hóa nhưng không có key → data vô dụng

### 4.3 Security Policies & Auditing

- **Regular security audits** — kiểm tra định kỳ xem security measures còn hiệu quả không
- **Logging & Monitoring** — ghi lại ai truy cập, thay đổi gì → review log thường xuyên
- **Employee training** — nhân viên là mắt xích yếu nhất, phải train security awareness

#### Mind map — Database Security

```
Database Security
│
├── 🔐 Access Control
│   ├── Strong passwords + rotation
│   ├── RBAC → Least Privilege
│   └── MFA → 2nd factor
│
├── 🔒 Encryption
│   ├── At Rest  → TDE
│   └── In Transit → SSL/TLS
│
└── 📋 Security Policies
    ├── Regular audits
    ├── Logging & monitoring
    └── Employee training

```

---

---

## Nguồn bổ sung — sqldbaschool.com (20 Lessons)

### DMV Scripts — Bộ công cụ triage chuẩn

**Baseline snapshot (luôn chạy đầu tiên):**
```sql
SELECT GETDATE() AS captured_at,
       cpu_count, scheduler_count,
       physical_memory_kb/1024 AS physical_memory_mb,
       sqlserver_start_time
FROM sys.dm_os_sys_info;

-- Top wait types kể từ lần restart cuối
SELECT TOP (20)
  wait_type, waiting_tasks_count,
  wait_time_ms, signal_wait_time_ms
FROM sys.dm_os_wait_stats
WHERE wait_type NOT LIKE 'SLEEP%'
ORDER BY wait_time_ms DESC;
```

**Active requests — triage realtime:**
```sql
SELECT r.session_id, s.login_name, s.host_name, s.program_name,
       r.status, r.cpu_time, r.total_elapsed_time,
       r.logical_reads, r.reads, r.writes,
       r.wait_type, r.wait_time, r.blocking_session_id,
       DB_NAME(r.database_id) AS database_name,
       SUBSTRING(t.text, (r.statement_start_offset/2)+1,
         CASE WHEN r.statement_end_offset = -1
              THEN LEN(CONVERT(nvarchar(max), t.text))
              ELSE (r.statement_end_offset - r.statement_start_offset)/2 + 1
         END) AS running_statement
FROM sys.dm_exec_requests r
JOIN sys.dm_exec_sessions s ON r.session_id = s.session_id
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
WHERE r.session_id <> @@SPID
ORDER BY r.total_elapsed_time DESC;
```

**I/O latency by file:**
```sql
SELECT DB_NAME(vfs.database_id) AS database_name,
       mf.type_desc, mf.physical_name,
       vfs.num_of_reads, vfs.num_of_writes,
       CAST(vfs.io_stall_read_ms  / NULLIF(vfs.num_of_reads,  0) AS decimal(18,2)) AS avg_read_ms,
       CAST(vfs.io_stall_write_ms / NULLIF(vfs.num_of_writes, 0) AS decimal(18,2)) AS avg_write_ms,
       CAST((vfs.io_stall_read_ms + vfs.io_stall_write_ms) /
            NULLIF(vfs.num_of_reads + vfs.num_of_writes, 0) AS decimal(18,2)) AS avg_total_ms
FROM sys.dm_io_virtual_file_stats(NULL, NULL) vfs
JOIN sys.master_files mf
  ON vfs.database_id = mf.database_id AND vfs.file_id = mf.file_id
ORDER BY avg_total_ms DESC;
```

**Blocking chain:**
```sql
-- Tìm sessions bị block
SELECT r.session_id, r.blocking_session_id,
       r.status, r.wait_type, r.wait_time, r.wait_resource,
       r.total_elapsed_time, DB_NAME(r.database_id) AS db_name,
       LEFT(t.text, 4000) AS statement_text
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
WHERE r.blocking_session_id <> 0
ORDER BY r.wait_time DESC;
```

**Top queries by logical reads (cache):**
```sql
SELECT TOP (20)
  qs.total_logical_reads,
  qs.total_logical_reads / NULLIF(qs.execution_count,0) AS avg_logical_reads,
  qs.execution_count,
  qs.total_worker_time   / NULLIF(qs.execution_count,0) AS avg_cpu,
  qs.total_elapsed_time  / NULLIF(qs.execution_count,0) AS avg_elapsed,
  DB_NAME(st.dbid) AS database_name,
  LEFT(st.text, 4000) AS query_text
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
ORDER BY qs.total_logical_reads DESC;
```

**Memory consumers:**
```sql
SELECT TOP (15)
  type AS memory_clerk,
  pages_kb/1024 AS pages_mb
FROM sys.dm_os_memory_clerks
ORDER BY pages_kb DESC;
```

**Statistics health:**
```sql
SELECT OBJECT_SCHEMA_NAME(s.object_id) AS schema_name,
       OBJECT_NAME(s.object_id)        AS table_name,
       s.name AS stats_name,
       sp.last_updated, sp.rows, sp.rows_sampled,
       sp.steps, sp.modification_counter
FROM sys.stats s
CROSS APPLY sys.dm_db_stats_properties(s.object_id, s.stats_id) sp
ORDER BY sp.last_updated ASC;
-- Rows ở trên cùng = stats lâu nhất chưa update → ưu tiên update
```

**Index usage (tìm unused indexes):**
```sql
SELECT OBJECT_SCHEMA_NAME(i.object_id) AS schema_name,
       OBJECT_NAME(i.object_id)        AS table_name,
       i.name AS index_name,
       u.user_seeks, u.user_scans, u.user_lookups, u.user_updates
FROM sys.indexes i
LEFT JOIN sys.dm_db_index_usage_stats u
  ON u.object_id   = i.object_id
 AND u.index_id    = i.index_id
 AND u.database_id = DB_ID()
WHERE i.index_id > 0
ORDER BY (ISNULL(u.user_seeks,0) + ISNULL(u.user_scans,0) + ISNULL(u.user_lookups,0)) ASC,
         ISNULL(u.user_updates,0) DESC;
-- Index có seeks/scans/lookups = 0 nhưng updates > 0 → overhead thuần, cân nhắc drop
```

**Backup recency:**
```sql
SELECT d.name AS database_name,
       MAX(CASE WHEN b.type = 'D' THEN b.backup_finish_date END) AS last_full_backup,
       MAX(CASE WHEN b.type = 'I' THEN b.backup_finish_date END) AS last_diff_backup,
       MAX(CASE WHEN b.type = 'L' THEN b.backup_finish_date END) AS last_log_backup
FROM sys.databases d
LEFT JOIN msdb.dbo.backupset b ON b.database_name = d.name
WHERE d.database_id > 4
GROUP BY d.name
ORDER BY d.name;
```

**Availability Group health:**
```sql
SELECT ag.name AS ag_name, ar.replica_server_name,
       ars.role_desc, ars.synchronization_state_desc,
       ars.connected_state_desc, ars.last_connect_error_description
FROM sys.availability_groups ag
JOIN sys.availability_replicas ar ON ag.group_id = ar.group_id
JOIN sys.dm_hadr_availability_replica_states ars
  ON ar.replica_id = ars.replica_id AND ar.group_id = ars.group_id
ORDER BY ag.name, ar.replica_server_name;
```

**Security audit — logins & roles:**
```sql
-- Server logins
SELECT sp.name AS login_name, sp.type_desc, sp.is_disabled,
       r.name AS server_role
FROM sys.server_principals sp
LEFT JOIN sys.server_role_members rm ON sp.principal_id = rm.member_principal_id
LEFT JOIN sys.server_principals r    ON rm.role_principal_id = r.principal_id
WHERE sp.type IN ('S','U','G')
ORDER BY sp.name, r.name;

-- Cấu hình nguy hiểm cần kiểm tra
SELECT name, value_in_use FROM sys.configurations
WHERE name IN ('xp_cmdshell','clr enabled',
               'Ad Hoc Distributed Queries',
               'contained database authentication')
ORDER BY name;

-- TDE status
SELECT d.name, dek.encryption_state, dek.key_algorithm, dek.key_length
FROM sys.databases d
LEFT JOIN sys.dm_database_encryption_keys dek ON d.database_id = dek.database_id
ORDER BY d.name;
```

**Server-side trace (production-safe, thay cho Profiler GUI):**
```sql
DECLARE @TraceId INT;
DECLARE @File NVARCHAR(260) = N'C:\Temp\SQLPT_SlowQueries';
DECLARE @MaxFileSize BIGINT = 50;
DECLARE @StopTime DATETIME = DATEADD(MINUTE, 5, GETDATE());

EXEC sp_trace_create @traceid = @TraceId OUTPUT, @options = 2,
     @tracefile = @File, @maxfilesize = @MaxFileSize, @stoptime = @StopTime;

-- Events: 10=RPC:Completed, 12=SQL:BatchCompleted
-- Columns: 1=TextData, 13=Duration, 16=Reads, 18=CPU, 35=DatabaseName
EXEC sp_trace_setevent @TraceId, 10, 1,  1;  -- TextData
EXEC sp_trace_setevent @TraceId, 10, 13, 1;  -- Duration
EXEC sp_trace_setevent @TraceId, 10, 16, 1;  -- Reads
EXEC sp_trace_setevent @TraceId, 10, 18, 1;  -- CPU
EXEC sp_trace_setevent @TraceId, 10, 35, 1;  -- DatabaseName
EXEC sp_trace_setevent @TraceId, 12, 1,  1;
EXEC sp_trace_setevent @TraceId, 12, 13, 1;
EXEC sp_trace_setevent @TraceId, 12, 16, 1;
EXEC sp_trace_setevent @TraceId, 12, 18, 1;
EXEC sp_trace_setevent @TraceId, 12, 35, 1;

-- Filter: chỉ capture > 500ms (Duration tính bằng microseconds)
EXEC sp_trace_setfilter @TraceId, 13, 0, 4, 500000;
EXEC sp_trace_setstatus @TraceId, 1; -- Start

-- Dừng trace:
-- EXEC sp_trace_setstatus @TraceId, 0;
-- EXEC sp_trace_setstatus @TraceId, 2;
```

---

### Wait Types — Bảng tra cứu nhanh

| Wait Type | Bottleneck | Hướng xử lý |
|-----------|-----------|-------------|
| `PAGEIOLATCH_*` | I/O — data page từ disk | Thêm index, thêm RAM, nâng cấp storage |
| `WRITELOG` | Log write latency | Di chuyển LDF sang storage nhanh hơn |
| `LCK_*` | Blocking / locking | Tìm root blocker, shorten transactions, xem xét RCSI |
| `SOS_SCHEDULER_YIELD` | CPU saturation | Optimize queries, review MAXDOP |
| `RESOURCE_SEMAPHORE` | Memory grant queue | Fix cardinality estimates, reduce sort/hash |
| `CXPACKET` | Parallelism overhead | Điều chỉnh MAXDOP, Cost Threshold |
| `ASYNC_NETWORK_IO` | Client không đọc kết quả kịp | App-side, pagination |
| `TEMPDB contention` | TempDB allocation pages | Thêm TempDB data files = số logical CPU |

---

### Key Concepts từ sqldbaschool.com

**SARGable vs Non-SARGable:**
```sql
-- NON-SARGable (không dùng được index seek)
WHERE YEAR(OrderDate) = 2026          -- function trên column
WHERE CONVERT(varchar, CustomerId) = '123'  -- implicit conversion
WHERE Name LIKE '%Smith'              -- leading wildcard

-- SARGable (dùng được index seek)
WHERE OrderDate >= '20260101' AND OrderDate < '20270101'
WHERE CustomerId = 123
WHERE Name LIKE 'Smith%'
```

**5 Case Studies thực tế (Lesson 20):**

| Case | Triệu chứng | Root Cause | Fix |
|------|------------|-----------|-----|
| Morning Freeze | Hệ thống đóng băng lúc 9h | Job UPDATE lớn trong 1 transaction → blocking chain | Batch nhỏ + index + alert blocking |
| Slow Report | Report ngày càng chậm | Data tăng → scan cost tăng | Nonclustered index + INCLUDE |
| CPU Storm | CPU đột ngột 100% | Scalar UDF / per-row computation | Rewrite sang set-based |
| Random Slowdowns | Lúc nhanh lúc chậm | Bad cardinality → oversized memory grants → RESOURCE_SEMAPHORE | Update stats + cải thiện index |
| Broke After Deploy | Chậm sau deployment mới | Parameter sniffing → plan regression | Query Store plan forcing → rewrite SP |

---

## Nguồn bổ sung — sqlservercentral.com

### Case Study: Index Tuning Wizard — Đừng áp dụng mù quáng

**Bối cảnh:** Stored procedure chạy ~240s, không reproduce được trong dev env.

**Quy trình phân tích đúng:**
```
1. Benchmark timing → xác định baseline (~240s)
2. Execution Plan + Server Trace → tìm 2 UPDATE statements là bottleneck
3. Chạy Index Tuning Wizard → wizard gợi ý:
   a) Non-clustered index trên bảng target
   b) Schema-bound view + clustered index + non-clustered index
   c) CREATE STATISTICS cho nhiều bảng
4. Áp dụng toàn bộ → 240s → 7-8s ✅ nhưng lỗi ARITHABORT ❌
```

**Bẫy ARITHABORT:**
> Schema-bound view với clustered index yêu cầu `ARITHABORT ON`.  
> OLE DB / ODBC connections mặc định `ARITHABORT OFF` → INSERT lỗi.  
> Fix: `SET ARITHABORT OFF` trước mỗi query — nhưng cần regression test toàn bộ app.

**Giải pháp thực tế — áp dụng từng bước:**
```
Apply step 1 only → timing run → 240s → 8s ✅
Apply step 2      → timing run → không cải thiện thêm
Apply step 3      → timing run → không cải thiện thêm
→ Kết luận: CHỈ cần non-clustered index, bỏ schema-bound view
```

**Bài học:**
- Wizard/Advisor gợi ý, không ra lệnh — phải phân tích từng step
- Apply **một thay đổi tại một thời điểm** với timing run giữa mỗi bước
- Đôi khi 1 index đơn giản = 95% improvement, không cần giải pháp phức tạp

---

## Nguồn bổ sung — sqlops.com

### Index Optimization (Travis Walker — sqlops.com)

**Trước/Sau khi thêm index — ví dụ cụ thể:**
```sql
-- Before: Full table scan (~5 seconds)
SELECT * FROM Customers WHERE LastName = 'Smith';

-- Tạo index
CREATE INDEX idx_lastname ON Customers(LastName);

-- After: Index seek (~0.5 seconds) — cải thiện 90%
SELECT * FROM Customers WHERE LastName = 'Smith';
```

**DMV hữu ích để quản lý index:**
```sql
-- Tìm index bị thiếu
SELECT * FROM sys.dm_db_missing_index_details;

-- Kiểm tra index nào đang được dùng / không dùng
SELECT * FROM sys.dm_db_index_usage_stats;
-- → Drop index có 0 seeks/scans để giảm overhead
```

**ALTER INDEX — cú pháp chuẩn:**
```sql
-- Fragmentation 10–30%: Reorganize (nhẹ, không lock)
ALTER INDEX idx_lastname ON Customers REORGANIZE;

-- Fragmentation > 30%: Rebuild (triệt để, nên chạy off-peak)
ALTER INDEX idx_lastname ON Customers REBUILD;
```

---

### Query Tuning Tips (sqlops.com)

**Đo lường trước khi tối ưu:**
```sql
SET STATISTICS IO ON;
SET STATISTICS TIME ON;
-- Chạy query → xem Logical Reads và CPU time
-- So sánh trước/sau khi thay đổi
```

**Các anti-pattern cần tránh:**

| Anti-pattern | Vấn đề | Fix |
|---|---|---|
| `SELECT *` | Đọc thừa cột → tăng I/O & memory | Chỉ SELECT các cột cần thiết |
| Correlated subquery | Chạy lại 1 lần / mỗi row | Rewrite thành JOIN |
| Table Scan | Không có index | Thêm index phù hợp |
| Key Lookup | Index thiếu included columns | Tạo covering index |

---

### SQL Server Configuration — MAXDOP & Memory

**MAXDOP (Maximum Degree of Parallelism):**
- Điểm bắt đầu: `MAXDOP = số physical cores / NUMA node`, tối đa 8
- Quá cao → resource contention; quá thấp → lãng phí CPU

**Memory:**
```sql
-- Cấu hình max server memory (để lại 10-15% hoặc ≥4GB cho OS)
sp_configure 'max server memory (MB)', 28672; -- ví dụ: 32GB RAM → để lại 4GB cho OS
RECONFIGURE;
```

---

### Monitoring — Key PerfMon Counters

| Counter | Ngưỡng tốt | Ý nghĩa khi vượt ngưỡng |
|---------|-----------|------------------------|
| **Buffer Cache Hit Ratio** | > 90% | Data không nằm trong memory → cần thêm RAM |
| **Page Life Expectancy** | > 300s | Pages bị đẩy ra cache quá nhanh |
| **Batch Requests/sec** | Baseline | Spike đột ngột → workload tăng |
| **SQL Compilations/sec** | Thấp | Cao → thiếu plan reuse, cần parameterization |

---

## Nguồn bổ sung — sqlshack.com (10 Articles)

### Case Study: 220s → 33s (Scalar UDF + TempDB Spill)

**3 vấn đề ban đầu:**

| # | Vấn đề | Hệ quả |
|---|--------|--------|
| 1 | Scalar UDF chạy mỗi row | Chiếm 142/220s tổng thời gian |
| 2 | Scalar UDF chặn parallelism | Query chạy serial dù cost cao |
| 3 | Computed expression trong ORDER BY | Sort spill sang TempDB |

**Bước 1 — Thay scalar UDF bằng CROSS APPLY (220s → 71s):**
```sql
-- BEFORE: scalar UDF chạy mỗi row (non-parallelizable)
SELECT dbo.[ufnGetStock](p.ProductID) AS Stock ...
WHERE LEN(CreditCardApprovalCode) > 10

-- AFTER: CROSS APPLY inline subquery (parallel-capable)
CROSS APPLY (
    SELECT ISNULL(SUM(Quantity), 0) AS Stock
    FROM Production.ProductInventory
    WHERE ProductID = p.ProductID AND LocationID = '6'
) AS Warehouse
```

**Bước 2 — Temp table + persisted computed column (71s → ~40s):**
```sql
CREATE TABLE #PerfmonTable (
    ...
    SortParameter nvarchar(6) NOT NULL,
    SmallApp AS ISNULL(LEN(CreditCardApprovalCode), 0) PERSISTED  -- pre-calculated
)

INSERT INTO #PerfmonTable WITH(TABLOCK)  -- TABLOCK = parallel insert
SELECT ... WHERE OrderQty > 2

DELETE FROM #PerfmonTable WHERE SmallApp <= 10  -- filter dùng persisted column
```

**Bước 3 — Covering index trên sort columns (→ 33s):**
```sql
-- Index key match ORDER BY direction → eliminates Sort operator + TempDB spill
CREATE NONCLUSTERED INDEX IX_Sort
ON #PerfmonTable(SortParameter, ProductID DESC)
INCLUDE (ProductNumber, Name, CarrierTrackingNumber,
         AccountNumber, CreditCardApprovalCode, Stock)
```

---

### Anti-patterns & Fixes (từ sqlshack)

**OR → UNION (1.2M reads → 750 reads):**
```sql
-- BAD: OR across columns → 1,200,000 logical reads (~2s)
SELECT DISTINCT p.ProductID, p.Name
FROM Production.Product p
INNER JOIN Sales.SalesOrderDetail d
  ON p.ProductID = d.ProductID OR p.rowguid = d.rowguid

-- GOOD: UNION → 750 logical reads (<1s)
SELECT p.ProductID, p.Name
FROM Production.Product p
INNER JOIN Sales.SalesOrderDetail d ON p.ProductID = d.ProductID
UNION
SELECT p.ProductID, p.Name
FROM Production.Product p
INNER JOIN Sales.SalesOrderDetail d ON p.rowguid = d.rowguid
```

**Function trên column (117 reads → 2 reads):**
```sql
-- BAD: LEFT() forces full index scan (117 logical reads, 19,270 rows scanned)
WHERE LEFT(Person.LastName, 3) = 'For'

-- GOOD: LIKE với prefix enables index seek (2 logical reads)
WHERE Person.LastName LIKE 'For%'
```

**Implicit conversion → table scan:**
```sql
-- BAD: numeric literal vs NVARCHAR column → CONVERT_IMPLICIT → full scan
WHERE NationalIDNumber = 658797903

-- GOOD: match data types → index seek
WHERE NationalIDNumber = '658797903'
```

**UNION vs UNION ALL:**
```sql
-- UNION: thêm Sort operator để dedup → chậm hơn
SELECT ... UNION SELECT ...

-- UNION ALL: không sort, không dedup → dùng khi kết quả trùng lặp là OK
SELECT ... UNION ALL SELECT ...
```

**12-table query → split bằng temp table:**
```sql
-- Thay vì 1 query với 12 JOINs (28 trillion possible plans cho optimizer)
-- Split thành 2 bước:

-- Step 1: materialize subset nhỏ
SELECT TOP 25 Product.ProductID, Product.Name, Product.ProductModelID, ...
INTO #Product
FROM Production.Product
INNER JOIN ... (3-4 tables)
ORDER BY Product.ModifiedDate DESC;

-- Step 2: join #Product với các bảng còn lại
SELECT ... FROM #Product
LEFT JOIN Production.ProductReview ...
LEFT JOIN Purchasing.ProductVendor ...
...

DROP TABLE #Product;
```

---

### Index Design Rules (sqlshack)

**Clustered Index Key — 4 tiêu chí bắt buộc (SNUQ):**

| Tiêu chí | Lý do |
|---------|-------|
| **S**tatic | Key thay đổi → update tất cả nonclustered indexes |
| **N**arrow | Key lớn → mọi nonclustered index đều lớn theo |
| **U**nique | Non-unique key → SQL Server thêm uniquifier ẩn |
| **S**equential | Non-sequential (GUID) → page splits, fragmentation |

> Identity column đáp ứng cả 4 tiêu chí → lựa chọn mặc định tốt nhất.

**OLTP vs OLAP indexing:**
- OLTP: ≤ 10 indexes/table (write overhead)
- OLAP: index thoải mái (read-only, transaction volume thấp)

**Filtered Index — khi nào dùng:**
```sql
-- Chỉ index những row active (bỏ qua archived rows)
CREATE NONCLUSTERED INDEX IX_Active
ON Orders(CustomerId)
WHERE Status = 'Active';
-- → Index nhỏ hơn, seek nhanh hơn, maintenance ít hơn
```

---

### Query Store & Automatic Plan Correction (SQL Server 2017+)

```sql
-- Enable Query Store
ALTER DATABASE DatabaseName SET QUERY_STORE = ON (
    OPERATION_MODE = READ_WRITE,
    CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 5),
    MAX_STORAGE_SIZE_MB = 10,
    INTERVAL_LENGTH_MINUTES = 1
);

-- Bật Automatic Plan Correction
ALTER DATABASE DatabaseName
SET AUTOMATIC_TUNING (FORCE_LAST_GOOD_PLAN = ON);

-- Kiểm tra recommendations
SELECT reason, score,
       JSON_VALUE(state, '$.currentValue') AS state,
       JSON_VALUE(details, '$.implementationDetails.script') AS fix_script
FROM sys.dm_db_tuning_recommendations
CROSS APPLY OPENJSON(details, '$.planForceDetails')
  WITH ([query_id] int '$.queryId',
        [current plan_id] int '$.regressedPlanId',
        [recommended plan_id] int '$.recommendedPlanId',
        regressedPlanCpuTimeAverage float,
        recommendedPlanCpuTimeAverage float);
```

**Recommendation lifecycle:**
```
Active → Verifying → Success (plan được force)
                  → Reverted (plan force không giúp ích)
```

---

### Covering Index — So sánh trực quan

```sql
-- Query cần tối ưu
SELECT CarrierTrackingNumber, UnitPrice
FROM Sales.SalesOrderDetail
WHERE UnitPrice BETWEEN 10 AND 10000

-- Index BẬT nhưng KHÔNG cover → Index Scan (đọc nhiều)
CREATE NONCLUSTERED INDEX IX_UnitPrice
ON Sales.SalesOrderDetail (UnitPrice)

-- Index cover → Index Seek (đọc ít, nhanh hơn nhiều)
CREATE NONCLUSTERED INDEX IX_UnitPrice_Cover
ON Sales.SalesOrderDetail (UnitPrice)
INCLUDE (CarrierTrackingNumber)
```

---

## Nguồn bổ sung — sqlshack.com (Articles 2–10)

### Execution Plan — Operators & Covering Index (Ahmad Yaseen)

**Fat arrow → thin arrow = bottleneck signal:**
```sql
-- Step 1: Naive index — still causes RID Lookup + Nested Loops
CREATE NONCLUSTERED INDEX IX_EMP_Salaries_EMP_ID
ON EMP_Salaries (EMP_ID)

-- Step 2: Covering index — eliminates RID Lookup entirely
CREATE NONCLUSTERED INDEX IX_EMP_Salaries_EMP_ID
ON EMP_Salaries (EMP_ID)
INCLUDE (EMP_HireDate, EMP_Salary)
WITH DROP_EXISTING

-- Step 3: Filter operator vì EMP_Salary không trong index → thêm index:
CREATE NONCLUSTERED INDEX IX_EMP_Salaries_EMP_Salary
ON EMP_Salaries (EMP_Salary)
```

**Bảng operators cần nhớ:**

| Operator | Ý nghĩa | Hành động |
|----------|---------|----------|
| Table Scan | Không có index | Thêm index |
| Index Scan | Có index nhưng không cover | Thêm INCLUDE columns |
| Index Seek | ✅ Tốt | Giữ nguyên |
| RID Lookup | Index trỏ đến heap → extra read/row | Chuyển thành covering index |
| Key Lookup | Index trỏ đến clustered key → extra read/row | Thêm INCLUDE |
| Hash Match | Join không có index | Thêm index trên join column |
| Filter | WHERE không thể push vào index | Index trên filtered column |

---

### Composite Index & Sort Order (Ahmad Yaseen)

**Kết quả benchmark thực tế:**

| Cấu hình | Logical Reads | CPU (ms) |
|----------|--------------|---------|
| Không có index | 310 | 16 |
| Naive single-column | ~310 (ignored) | 16 |
| Covering index `(STD_ID) INCLUDE (EV_ID, Course_ID, Grade)` | 3 (~91% giảm) | 0 |

```sql
-- 3-table JOIN — composite covering index tốt hơn 2 separate indexes
CREATE NONCLUSTERED INDEX [IX_STD_Evaluation_Course_ID]
ON dbo.STD_Evaluation (STD_ID, Course_ID)
INCLUDE (STD_Course_Grade)

-- Sort order phải match ORDER BY để tránh Sort operator:
-- ✅ Fully reversed → Backward scan (không cần Sort)
ORDER BY ST.STD_ID DESC, C.Course_ID DESC

-- ❌ Partial mismatch → Sort operator bắt buộc (expensive)
ORDER BY ST.STD_ID ASC, C.Course_ID DESC
```

---

### Tips & Tricks thực chiến (Ed Pollack — sqlshack)

**Batch large writes:**
```sql
-- Thay vì UPDATE 1M rows trong 1 transaction:
DECLARE @BatchSize INT = 5000;
DECLARE @Rows INT = 1;
WHILE @Rows > 0
BEGIN
    UPDATE TOP (@BatchSize) dbo.Orders
    SET Status = 'Archived'
    WHERE Status = 'Old' AND OrderDate < '2020-01-01';
    SET @Rows = @@ROWCOUNT;
END
-- → Giảm lock duration, cho phép concurrent transactions chạy xen kẽ
```

**JOIN hints — chỉ dùng khi thực sự cần:**
```sql
-- Force merge join (yêu cầu sorted inputs)
SELECT ... FROM TableA INNER MERGE JOIN TableB ON ...

-- Force hash join (cho large unsorted datasets)
SELECT ... FROM TableA INNER HASH JOIN TableB ON ...

-- ⚠️ Hints mã hóa assumptions có thể stale → dùng như last resort
```

---

### Getting Started Tips (Esat Erkec — sqlshack)

```sql
-- ❌ Bad: SELECT * — tăng I/O và network transfer
SELECT * FROM Sales.SalesOrderDetail;

-- ✅ Good: chỉ lấy cột cần thiết
SELECT SalesOrderId, CarrierTrackingNumber FROM Sales.SalesOrderDetail;

-- ❌ Non-sargable: SUBSTRING trên column → Index Scan
WHERE SUBSTRING(ProductNumber, 1, 2) = 'AR'

-- ✅ SARGable: LIKE với prefix → Index Seek
WHERE ProductNumber LIKE 'AR%'

-- ❌ UNION: thêm Sort operator để dedup
SELECT AccountNumber, Name FROM Purchasing.Vendor
UNION
SELECT AccountNumber, Name FROM Purchasing.Vendor

-- ✅ UNION ALL: không sort, nhanh hơn khi duplicate không thành vấn đề
SELECT AccountNumber, Name FROM Purchasing.Vendor
UNION ALL
SELECT AccountNumber, Name FROM Purchasing.Vendor
```

---

### STATISTICS TIME/IO — đo lường baseline (sqlshack Tips for Newbies)

```sql
-- Đo CPU + elapsed time
SET STATISTICS TIME ON;
SELECT P.Name, SOH.OrderDate
FROM Sales.SalesOrderHeader SOH
JOIN Sales.SalesOrderDetail SOD ON SOH.SalesOrderID = SOD.SalesOrderDetailID
JOIN Production.Product P ON SOD.ProductID = P.ProductID;
SET STATISTICS TIME OFF;
-- Output: Parse/compile time + CPU time + elapsed time

-- Đo I/O per table
SET STATISTICS IO ON;
-- (chạy query)
SET STATISTICS IO OFF;
-- Output: Scan count, Logical reads, Physical reads, Read-ahead reads
```

**Giải thích output:**
- `Parse/compile time = 0` → plan cache hit (tốt)
- `Physical reads > 0` → data không nằm trong buffer pool → memory pressure
- `Logical reads` = metric chính để so sánh trước/sau tuning

**Tools nâng cao:**
- `sp_whoisactive` (Adam Machanic): blocking chains, long-running queries, high-CPU sessions — miễn phí, download từ whoisactive.com
- **Extended Events**: production-safe replacement cho Profiler; filter theo `client_app_name`
- **Query Store reports**: Regressed Queries, Top Resource Consuming, Query Wait Statistics

---

## Nguồn bổ sung — sqlservercentral.com (Articles 2–4)

### Azure SQL Performance Tuning: CCI + Partitioning (2025)

```sql
-- Covered index cho Orders queries
CREATE NONCLUSTERED INDEX IX_Orders_CustomerID
ON Orders(CustomerID)
INCLUDE (OrderDate, TotalAmount);

-- Filtered index: chỉ active products
CREATE NONCLUSTERED INDEX IX_Active_Products
ON Products(ProductName)
WHERE IsActive = 1;

-- Tìm unused indexes cần drop
SELECT OBJECT_NAME(i.object_id) AS TableName,
       i.name AS IndexName,
       user_seeks, user_scans, user_lookups,
       user_updates  -- cao + seeks thấp → net-negative, cân nhắc drop
FROM sys.dm_db_index_usage_stats us
JOIN sys.indexes i
  ON us.object_id = i.object_id AND us.index_id = i.index_id
WHERE OBJECT_NAME(i.object_id) = 'Orders';

-- Partitioning theo năm
CREATE PARTITION FUNCTION PF_OrderDateRange (DATE)
AS RANGE RIGHT FOR VALUES ('2023-01-01', '2024-01-01', '2025-01-01');

CREATE PARTITION SCHEME PS_OrderDateRange
AS PARTITION PF_OrderDateRange TO ([PRIMARY], [PRIMARY], [PRIMARY], [PRIMARY]);

CREATE TABLE Orders (
    OrderID INT, OrderDate DATE,
    CustomerID INT, TotalAmount DECIMAL(10,2)
) ON PS_OrderDateRange(OrderDate);

-- Partition elimination — chỉ scan partition 2023
SELECT * FROM Orders WHERE OrderDate BETWEEN '2023-01-01' AND '2023-12-31';

-- Clustered Columnstore Index cho analytics
CREATE CLUSTERED COLUMNSTORE INDEX CCI_Orders ON Orders;

-- Analytical query → 10-100x faster với CCI
SELECT DATEPART(YEAR, OrderDate) AS OrderYear,
       DATEPART(MONTH, OrderDate) AS OrderMonth,
       SUM(TotalAmount) AS MonthlyRevenue
FROM Orders
GROUP BY DATEPART(YEAR, OrderDate), DATEPART(MONTH, OrderDate)
ORDER BY OrderYear, OrderMonth;

-- Update statistics sau khi load data lớn
UPDATE STATISTICS Orders WITH FULLSCAN;
```

**CCI performance numbers:**
- Compression: **5-10x** vs row storage
- Analytical queries: **10-100x faster** cho SUM/AVG/COUNT trên large tables
- Đừng dùng CCI cho: OLTP với single-row updates thường xuyên, bảng < 1M rows

---

### Query Tuning — Methodical Approach (Gail Shaw — benchmark thực tế)

> **Rule số 1**: Không thay đổi 2 thứ cùng lúc. Mỗi thay đổi = 1 timing run.

**Kết quả benchmark trên WebForums DB (25M rows):**

| Thay đổi | CPU (ms) | Duration (ms) | Reads |
|----------|---------|--------------|-------|
| Baseline | 139,008 | 107,822 | 556,462 |
| + Index on Forums | 142,640 | 110,458 | 556,558 ❌ worse |
| + Index on Posts | 101,674 | 63,296 | 187,505 ✅ |
| + CI change on Threads | 119,193 | 62,840 | 154,569 |
| + Partitioning Threads | 118,918 | 62,949 | 154,561 (no change) |
| + Columnstore on Threads | **57,618** | **45,623** | 165,288 ✅ |

```sql
-- Index hiệu quả nhất: trên Posts (giảm reads 66%)
CREATE NONCLUSTERED INDEX idx_Posts_ThreadIDPostDate
ON Posts (ThreadID, PostDate)
INCLUDE (Poster)

-- Partitioning Threads (thử nhưng không cải thiện)
CREATE PARTITION FUNCTION DatePartitionPerYear (DATETIME)
AS RANGE RIGHT FOR VALUES
  ('2010-01-01','2011-01-01','2012-01-01',
   '2013-01-01','2014-01-01','2015-01-01')

CREATE PARTITION SCHEME PartitionByDateToPrimary
AS PARTITION DatePartitionPerYear ALL TO ([Primary])

-- Columnstore trên Threads — biggest win (CPU giảm 59% so với baseline)
ALTER TABLE dbo.Threads DROP CONSTRAINT Pk_Threads
DROP INDEX idx_Threads_CreatedOn ON dbo.Threads
CREATE CLUSTERED COLUMNSTORE INDEX idx_Threads_ColumnStore ON dbo.Threads
```

> ⚠️ **Partitioning ≠ performance technique** — không expect CPU/duration cải thiện từ partitioning.

---

### Index & Locking — Tại sao index quan trọng ngoài performance (Saravanan Venkatesan)

> **Key insight**: Index không chỉ tăng tốc query mà còn **giảm phạm vi lock**, ngăn blocking giữa các transactions không liên quan.

**Thí nghiệm (StocksTraded, ~3,000 rows):**

| Trạng thái | UPDATE HDFCBANK giữ lock | SELECT BSE |
|-----------|------------------------|-----------|
| Không có index | Lock **2,947 rows** (full scan) | **BỊ BLOCK** |
| Có index trên `symbol` | Lock **1 row** (index seek) | **Chạy ngay** |

```sql
-- Kiểm tra active locks
SELECT * FROM sys.dm_tran_locks
WHERE resource_database_id = DB_ID()
  AND resource_associated_entity_id = OBJECT_ID('StocksTraded');

-- Tạo index → lock scope từ 2,947 rows → 1 row
CREATE NONCLUSTERED INDEX IX_StocksTraded_Symbol
ON StocksTraded (symbol);
```

**Bài học**: Trên bảng heap (không có index), SQL Server có thể lock toàn bộ rows đã scan — dù chỉ 1 row là target thực sự của DML. SELECT trên row hoàn toàn khác cũng bị block vì cùng scan path.

---

## Nguồn bổ sung — sqlops.com (Articles 2–6)

### Advanced T-SQL Techniques

**Window Functions — thay thế self-joins:**
- `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()` — xếp hạng trong partition
- `LAG()`, `LEAD()` — truy cập row liền kề không cần self-join
- `OVER(PARTITION BY ... ORDER BY ...)` — aggregate không collapse rows

**JSON trong T-SQL:**
- `OPENJSON` — parse JSON array/object thành rows
- `FOR JSON PATH` — convert result set sang JSON
- `JSON_VALUE(col, '$.key')` — extract scalar value

**Columnstore cho analytics:**
- Dùng cho large analytical tables (> 1M rows, aggregation-heavy)
- Không dùng cho OLTP (frequent single-row updates)

---

### Security Layers — TDE, RLS, DDM (sqlops)

| Layer | Bảo vệ gì | Cơ chế |
|-------|----------|--------|
| **TDE** | Files at rest (MDF, LDF, backup) | Transparent encryption ở storage level |
| **Column Encryption** | Giá trị cụ thể trong cột nhạy cảm | App phải handle encrypt/decrypt |
| **RLS** (Row-Level Security) | Ai xem được row nào | Security policy + predicate function |
| **DDM** (Dynamic Data Masking) | Query result obfuscation | Mask trong output, không thay đổi data gốc |

> ⚠️ DDM chỉ che kết quả query — privileged users vẫn thấy raw data. Không phải encryption.

---

## Tổng kết (Coursera Course Wrap-up)

**3 trụ cột đã học:**

```
SQL Server Performance Tuning
│
├── 1. Query Tuning
│   ├── Execution Plans (Table Scan → Index Seek)
│   ├── Join strategies (Nested Loop / Hash / Merge)
│   └── Tools: SSMS, SQL Server Profiler, Tuning Advisor
│
├── 2. Indexing & Maintenance
│   ├── Rebuild (>30%) / Reorganize (5-30%)
│   ├── DBCC CHECKDB + UPDATE STATISTICS
│   ├── Table Partitioning + Partition Pruning
│   └── Backup: Full + Differential + Transaction Log
│
└── 3. Security & Monitoring
    ├── RBAC + MFA + Encryption (at rest & in transit)
    ├── Activity Monitor → Profiler → Tuning Advisor
    └── RTO / RPO → test restore định kỳ
```

> "This is just the beginning. Keep practicing, stay curious, and continue to push your skills to the next level."

---

*Cập nhật lần cuối: 2026-06-18*
