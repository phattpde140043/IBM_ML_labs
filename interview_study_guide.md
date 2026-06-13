# Tài Liệu Ôn Tập Phỏng Vấn Backend / Data Engineer

Dựa trên JD và profile của bạn (Kafka, Airflow, Databricks, FastAPI, OpenSearch, Redis), tài liệu này tập trung sâu vào **Python Core**, **Hệ thống ETL / Data Pipeline**, **Tối ưu hóa Database/SQL**, và **System Architecture**.

---

## 1. Python Core & Software Engineering (Trọng tâm)

### 1.1. Python Internals & Memory Management
*   **List vs Tuple:** List is mutable (thay đổi được), tuple is immutable (không đổi được). Tuple sử dụng ít bộ nhớ hơn và có thể dùng làm key trong dictionary.
*   **Shallow Copy vs Deep Copy:** `copy.copy()` (shallow) chỉ copy tham chiếu của các object con. `copy.deepcopy()` (deep) tạo ra bản sao hoàn toàn mới, độc lập của mọi object con.
*   **Mutable vs Immutable:** Immutable (int, float, string, tuple) khi thay đổi sẽ tạo object mới. Mutable (list, dict, set) thay đổi in-place.
*   **GIL (Global Interpreter Lock):** Mutex trong CPython ngăn nhiều thread thực thi bytecode Python cùng lúc. Làm cho multithreading trong Python không hiệu quả cho CPU-bound tasks, nhưng vẫn tốt cho I/O-bound tasks.
*   **Multiprocessing vs Multithreading:**
    *   *Multithreading:* Tốt cho I/O-bound (gọi API, đọc/ghi file, DB query). Bị giới hạn bởi GIL.
    *   *Multiprocessing:* Tốt cho CPU-bound (tính toán nặng, transform data lớn). Bypass được GIL vì mỗi process có Python interpreter riêng.
*   **Generator & Yield:** Thay vì trả về toàn bộ list (tốn RAM), `yield` trả về từng phần tử một (lazy evaluation). Rất quan trọng khi đọc file lớn.
*   **Iterator:** Bất kỳ object nào có hàm `__iter__` và `__next__`.
*   **Context Manager:** Sử dụng `with` statement để đảm bảo tài nguyên (file, DB connection) được giải phóng/đóng lại an toàn ngay cả khi có lỗi xảy ra.
*   **Decorator:** Hàm nhận vào một hàm khác và mở rộng chức năng của nó mà không thay đổi code bên trong (ví dụ: `@retry`, `@timer`, `@lru_cache`).
*   **Async/Await:** Xử lý bất đồng bộ, dùng cho I/O-bound cực cao (ví dụ: FastAPI gọi hàng trăm API đồng thời).

> **Câu hỏi thực tế:** "Khi ETL xử lý file lớn hàng GB thì làm sao tránh memory overflow?"
> **Trả lời:** Không dùng `.read()` hoặc `.readlines()`. Dùng iteration `for line in file:` hoặc `pandas.read_csv(chunksize=...)` kết hợp với **Generator** để stream data. Đẩy vào DB theo **Batching**.

### 1.2. OOP / SOLID
*   **Inheritance vs Composition:** Ưu tiên Composition (has-a) hơn Inheritance (is-a) để giảm sự phụ thuộc và lồng ghép quá sâu.
*   **Dependency Injection:** Truyền các dependency (như DB connection) từ bên ngoài vào class thay vì hardcode khởi tạo bên trong. Giúp dễ test và linh hoạt.
*   **SOLID Principles:**
    *   *S (Single Responsibility):* Một class/hàm chỉ làm 1 việc (ví dụ: hàm extract không làm luôn transform).
    *   *O (Open/Closed):* Dễ mở rộng (thêm source mới) nhưng không cần sửa code cũ.
    *   *L (Liskov Substitution):* Class con phải thay thế được class cha mà không làm hỏng app.
    *   *I (Interface Segregation):* Đừng ép client implement những interface họ không dùng.
    *   *D (Dependency Inversion):* Phụ thuộc vào Abstraction, không phụ thuộc vào Implementation cụ thể.

> **Câu hỏi thực tế:** "Nếu ETL pipeline có nhiều source khác nhau thì em design thế nào?"
> **Trả lời:** Dùng **Interface Abstraction** (vd: `BaseExtractor`) và **Factory/Strategy Pattern**.

```python
from abc import ABC, abstractmethod

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self): pass

class CsvExtractor(BaseExtractor):
    def extract(self): ...

class OracleExtractor(BaseExtractor):
    def extract(self): ...
```

### 1.3. Design Patterns cho ETL
*   **Strategy Pattern:** Chuyển đổi giữa các thuật toán Transform khác nhau tại runtime mà không dùng nhiều if/else.
*   **Factory Pattern:** Khởi tạo Extractor hoặc Loader tương ứng dựa trên config (vd: `get_extractor("oracle")`).
*   **Singleton:** Dùng cho Database Connection Pool hoặc Config Manager để tránh tạo nhiều instance tốn resource.

### 1.4. Bộ Câu Hỏi Ứng Dụng Python Core (Middle Level)
*(Tập trung vào Production Scenario + Python Internals + Performance Reasoning)*

*   **Q: Cần xử lý file CSV 20GB nhưng server chỉ có 4GB RAM. Em làm sao?**
    *   *A:* Tuyệt đối không load toàn bộ vào memory. Sử dụng `pandas.read_csv(chunksize=10000)` hoặc iteration `for line in file:` kết hợp Generator để xử lý theo dạng streaming/batching.
*   **Q: Tại sao code Pandas bị memory spike rất lớn? Optimize thế nào?**
    *   *A:* Do Pandas load full dataframe vào RAM, object dtype overhead cao và thường sinh ra các bản copy ẩn. Khắc phục bằng cách dùng `chunksize`, tối ưu `dtype` (dùng category thay cho object string), hoặc chuyển sang dùng `PyArrow`/`Polars`/`Parquet`.
*   **Q: Một process Python có memory tăng liên tục dù job gần xong. Lỗi do đâu và debug bằng gì?**
    *   *A:* Thường là Memory Leak do Circular references (tham chiếu chéo), global cache phình to, hoặc quên đóng object/file. Dùng các tool như `tracemalloc`, `memory_profiler`, và module `gc` (Garbage Collector) để trace.
*   **Q: Tại sao multithreading không tăng performance cho CPU-heavy tasks? Multiprocessing đôi khi lại chậm hơn, vì sao?**
    *   *A:* Multithreading vướng GIL (Global Interpreter Lock), chỉ 1 thread chạy Python bytecode tại một thời điểm. Multiprocessing bypass được GIL, nhưng nếu task quá nhỏ, chi phí khởi tạo process (Startup overhead) và Serialize dữ liệu (IPC cost) sẽ lớn hơn cả thời gian xử lý, làm nó chậm hơn single-thread.
*   **Q: FastAPI chạy Async nhưng app vẫn bị block. Nguyên nhân và cách xử lý?**
    *   *A:* Do trong hàm async gọi Blocking code (như thư viện DB đồng bộ `psycopg2` thay vì `asyncpg`) hoặc tính toán CPU-heavy bên trong event loop. Cần bọc code đó trong `run_in_executor()` hoặc đẩy sang Celery/Background Worker.
*   **Q: Tại sao Mutable object cực kỳ nguy hiểm khi dùng làm function default arguments (VD: `def func(arr=[])`)?**
    *   *A:* Vì default argument chỉ được evaluate (khởi tạo) đúng 1 lần khi compile hàm. Các lần gọi hàm sau nó sẽ dùng chung list memory đó, dẫn tới dữ liệu bị dính/tích lũy sai lệch qua các lần gọi.
*   **Q: Tại sao Generator/Iterator lại tốt cho ETL? Generator "exhausted" nghĩa là gì?**
    *   *A:* Giúp Lazy Evaluation (tính đến đâu dùng đến đó, không lưu full vào RAM), rất lý tưởng cho Streaming pipelines. Generator bị "exhausted" nghĩa là nó chỉ duyệt qua 1 lần duy nhất, duyệt xong là cạn, muốn duyệt lại phải khởi tạo mới.
*   **Q: Quên close DB connection thì hệ lụy là gì? Dùng gì để giải quyết triệt để?**
    *   *A:* Gây ra Connection Leak và Pool Exhaustion (cạn kiệt kết nối DB). Luôn phải dùng **Context Manager** (`with ... as conn:`) để đảm bảo resource cleanup an toàn dù có Exception xảy ra.
*   **Q: ETL đột nhiên chậm đi 10 lần khi data volume tăng mạnh. Flow debug của em là gì?**
    *   *A:* Check tuần tự: Memory (có tràn và bị swap xuống disk không) -> CPU (có 100% do serialize không) -> Network/Disk I/O -> DB bottleneck (quá tải write). Sau đó điều chỉnh lại Batch Size hoặc Parallelism.
*   **Q: Insert từng row vào DB bằng Python có vấn đề gì? Khắc phục thế nào?**
    *   *A:* Gây Network roundtrip khổng lồ và Transaction overhead. Phải dùng `executemany` (Batch Insert) để gom hàng nghìn row vào một lần write.
*   **Q: JSON parsing quá chậm thì xử lý thế nào?**
    *   *A:* Thay thư viện mặc định bằng `orjson` hoặc `ujson`. Nếu file JSON khổng lồ, dùng Streaming parser (ví dụ `ijson`) để đọc từng phần.

> **Keywords ăn điểm cho Python Middle:** *Memory overhead, Lazy loading, Batching, Event loop, Blocking I/O, Serialization cost, CPU-bound vs I/O-bound, Resource cleanup, Throughput, Backpressure.*

---

## 2. ETL / Data Pipeline (Cực kỳ quan trọng)

### 2.1. ETL Flow & Architecture
*   **Extract:** Đọc từ file CSV, gọi API, query từ DB (Oracle). Cần lưu ý việc đọc incremental (chỉ lấy data mới).
*   **Transform:** Clean data, join, map types, filter duplicates. Nên làm in-memory bằng chunks.
*   **Load:** Insert/Upsert vào Data Warehouse. Dùng bulk insert/batching.

### 2.2. Xử lý Lỗi & Resilience
*   **Idempotency (Tính lũy đẳng):** Chạy lại pipeline nhiều lần với cùng 1 input vẫn cho ra cùng 1 kết quả (không bị duplicate data). Cần cơ chế Upsert/Merge.
*   **Retry:** Dùng decorator hoặc Airflow task retries cho các lỗi tạm thời (network timeout).
*   **Checkpoint & Incremental Load:** Lưu lại `last_processed_id` hoặc `last_updated_time` (Watermark) để lần sau chạy tiếp từ đó.
*   **Dead Letter Queue (DLQ):** Nếu row nào bị lỗi schema/type, không làm tịt cả batch mà đẩy row đó vào file/bảng riêng (DLQ) để xử lý sau.

### 2.3. Batch Processing & Performance Optimization
*   **Xử lý hàng triệu rows:** Đọc theo Chunk, transform, sau đó **Bulk Insert/ExecuteMany** vào DB (mỗi batch 1000 - 10,000 rows). Không bao giờ commit từng row.
*   **Memory Optimization:** Xoá biến không cần thiết, dùng `gc.collect()`, thay `list` bằng `generator` ở những bước trung gian.
*   **Parallel Processing:** Dùng `multiprocessing.Pool` hoặc ThreadPoolExecutor để xử lý nhiều file hoặc nhiều partition dữ liệu đồng thời.

---

## 3. Oracle / SQL / Database

### 3.1. SQL Optimization
*   **Index:** Dùng B-Tree cho cột có độ phân tán cao (ID, email), Bitmap cho độ phân tán thấp (Gender, Status). Nhớ đánh index cho các cột trong `WHERE`, `JOIN`.
*   **Execution Plan:** Kiểm tra xem query có bị *Full Table Scan* không, hay đang dùng *Index Scan/Seek*.
*   **Join Optimization:** Tránh `CROSS JOIN`, cẩn thận với `OUTER JOIN` nếu không cần thiết. Đảm bảo cột Join có cùng kiểu dữ liệu.
*   **Partitioning:** Chia bảng lớn thành các vách ngăn (theo ngày/tháng). Quét theo ngày sẽ nhanh hơn rất nhiều (Partition Pruning).

### 3.2. Migration & Stored Procedure
*   *Migration DB to Python:* Họ muốn dời logic xử lý từ SQL Stored Procedure (khó maintain, khó test, tải DB cao) ra Python Backend (dễ scale, testable).
*   **Data Consistency:** Khi migrate, cần check count, sum, hash data giữa source và target để đảm bảo đúng dữ liệu.

---

## 4. System / Large-scale Processing

### 4.1. Concurrency & Throughput
*   Làm sao tăng throughput?
    1.  **Scale up (Vertical):** Tối ưu code Python (Batching, Generator, Vectorization với Pandas/Numpy).
    2.  **Scale out (Horizontal):** Chia nhỏ task ra Kafka, dùng nhiều worker đọc (Consumer Group). Hoặc dùng Spark/Databricks cho phân tán.

### 4.2. Kiến Trúc (Architecture)
Liên hệ với kinh nghiệm của bạn (Kafka, FastAPI, Airflow):
*   **Pipeline 1 (Batch):** Airflow trigger Job -> Python Operator connect Oracle lấy Incremental data -> Transform chunks -> Bulk Insert vào Warehouse.
*   **Pipeline 2 (Streaming):** Change Data Capture (CDC) hoặc Kafka Producer đẩy event -> Kafka Topic -> Python Consumer xử lý real-time -> Ghi vào OpenSearch/Redis.

---

## 5. Kịch Bản Live Coding (Chuẩn Bị Sẵn)

### 5.1. Xử lý file CSV cực lớn (Streaming / Generator)
Yêu cầu: Tính tổng hoặc tìm dòng lỗi mà không load hết file vào RAM.
```python
import csv

def process_large_csv(file_path):
    # Dùng context manager và generator
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Transform or filter từng dòng
            if int(row['amount']) > 1000:
                yield row

# Sử dụng:
for valid_row in process_large_csv('10GB_data.csv'):
    # Lấy ra tới đâu, insert DB tới đó (theo batch)
    pass
```

### 5.2. Lọc Duplicate linh hoạt
Yêu cầu: Lọc duplicate dựa trên 1 tập hợp key.
```python
def remove_duplicates(data_stream, key_func):
    seen = set()
    for item in data_stream:
        key = key_func(item)
        if key not in seen:
            seen.add(key)
            yield item
```

---

## 6. Behavioral & Mindset

**Chuẩn bị các câu chuyện thực tế từ dự án của bạn (STAR method: Situation - Task - Action - Result):**

1.  **Dự án Forex / Kafka Pipeline:** Mô tả cách bạn handle throughput cao, latency thấp.
2.  **Khắc phục sự cố (Troubleshooting):** Một lần data bị sai lệch, pipeline bị nghẽn (out of memory), hoặc DB lock. Bạn đã debug thế nào (check log, profiling memory, explain SQL)?
3.  **Tối ưu hóa Performance:** Cách bạn giảm thời gian chạy ETL từ hàng giờ xuống vài phút (bằng Batching, Threading, hay Indexing).
4.  **Tự học công nghệ mới:** Ví dụ quá trình tiếp cận và áp dụng Airflow/Databricks vào dự án.

---

# PHẦN 2: ADVANCED & PRODUCTION MINDSET

Dựa trên CV khá mạnh của bạn, interviewer sẽ chuyển mindset từ "biết framework không?" sang **"em hiểu production system tới đâu?"**. Các câu hỏi dưới đây tập trung vào Trade-off, Scalability, và Debugging.

## 7. Python Deep Dive (Production-Level)
*   **Tại sao Python chậm hơn Java/C++?** Do Python là ngôn ngữ thông dịch (interpreted language), kiểu dữ liệu động (dynamic typing), có Global Interpreter Lock (GIL) hạn chế chạy đa luồng thực sự, và overhead của các Python object trong memory.
*   **Khi nào dùng Async thay vì Threading?**
    *   **Async:** Rất tốt cho High concurrent I/O (ví dụ: crawl hàng ngàn URL, gọi API đồng loạt), sử dụng Event loop, cực kỳ nhẹ.
    *   **Threading:** Phù hợp với các Blocking I/O legacy không support async. Tốn overhead OS thread hơn.
*   **Pandas có vấn đề gì với dữ liệu lớn?** Nặng về memory (thường yêu cầu RAM gấp 5-10 lần dung lượng file), chạy trên một máy duy nhất (single-machine limitation), có overhead khi copy dữ liệu.
*   **Khi nào KHÔNG nên dùng Multiprocessing?** Khi các task quá nhỏ, chi phí serialize/deserialize dữ liệu (IPC cost - Inter-Process Communication) sẽ lớn hơn cả thời gian xử lý thực tế.
*   **Memory leak trong Python có thể đến từ đâu?** Do tham chiếu chéo (circular references), các biến global/cache không bao giờ bị xóa, quên đóng resource (file, connection), hoặc các danh sách/hàng đợi (list, queue) cứ phình to liên tục.

## 8. Kafka Advanced
*   **Exactly Once Semantics (EOS) là gì?** Đảm bảo message không bị mất cũng không bị lặp. Yêu cầu Producer Idempotence (gửi lại không bị double), Transactional writes, và phối hợp chính xác với việc commit offset.
*   **At-most-once vs At-least-once vs Exactly-once:**
    *   *At-most-once:* Gửi và quên. Rủi ro mất data (data loss).
    *   *At-least-once:* Đảm bảo gửi tới, nhưng nếu lỗi mạng có thể gửi lại gây duplicate.
    *   *Exactly-once:* An toàn nhất nhưng tốn kém tài nguyên và độ trễ cao.
*   **Consumer lag là gì?** Là khoảng cách giữa thông điệp mới nhất được tạo (Latest Offset) và thông điệp cuối cùng đã được đọc (Consumer Offset). Thể hiện mức độ "nghẽn" của pipeline.
*   **Làm gì khi Consumer xử lý chậm?** Scale up số lượng consumers, tăng số partitions tương ứng trên Kafka, áp dụng batching khi đọc/ghi, tối ưu hóa code processing, hoặc áp dụng backpressure.
*   **Partition nhiều quá có vấn đề gì?** Gây overhead metadata cho Zookeeper/KRaft, chi phí rebalance cao khi có consumer chết, và tốn memory/network cho các file descriptor/buffer.

## 9. Airflow Deep Questions
*   **Khi nào Airflow KHÔNG phù hợp?** Khi bạn cần ultra-low latency streaming hoặc xử lý event theo thời gian thực (real-time event processing). Airflow là công cụ lập lịch dạng Batch.
*   **XCom là gì?** (Cross-Communication) Cơ chế giúp các Task trong cùng một DAG có thể trao đổi dữ liệu nhỏ (ví dụ metadata, ID) với nhau thông qua Backend DB.
*   **Nếu DAG fail giữa chừng?** Hệ thống cần phải cô lập lỗi (task isolation), hỗ trợ retry các task fail, lưu lại checkpoint và có khả năng resume chạy tiếp (Clear failed tasks) mà không ảnh hưởng kết quả cuối.

## 10. Databricks / Delta Lake
*   **Delta Lake giải quyết vấn đề gì?** Mang tính chất ACID (Atomicity, Consistency, Isolation, Durability) cho Data Lake, hỗ trợ Schema Enforcement (chống rác data) và Time Travel (rollback về phiên bản cũ).
*   **Parquet vs CSV:** Parquet lưu trữ dạng cột (columnar) rất tốt cho Analytics, tự nén cực tốt và lưu giữ được schema. CSV lưu theo dòng (row-based), text thuần, nặng và chỉ hợp cho transfer đơn giản.
*   **Small files problem?** Dữ liệu bị băm ra thành hàng ngàn file nhỏ làm cho driver/namenode tốn quá nhiều thời gian xử lý metadata thay vì đọc data thực tế. Cần dùng lệnh `OPTIMIZE` kết hợp `VACUUM`.
*   **Partition theo cột nào?** Các cột có Low Cardinality (số lượng giá trị độc nhất thấp như Date, Year, Country) và thường xuyên được filter. Tránh chia partition theo cột ID.

## 11. Database / SQL & System Design Advanced
*   **Isolation Levels (Mức độ cô lập giao dịch):**
    *   *Read Uncommitted:* Nhanh nhất nhưng bị lỗi đọc dữ liệu rác (Dirty Read).
    *   *Read Committed:* Chống Dirty Read (thường là mặc định).
    *   *Repeatable Read:* Đảm bảo đọc 2 lần trong 1 transaction ra cùng kết quả (chống Non-repeatable Read).
    *   *Serializable:* Mức cao nhất, giao dịch tuần tự, chống hoàn toàn Phantom Read nhưng rất chậm và dễ deadlock.
*   **N+1 Query problem:** Khi truy vấn 1 record cha lại sinh ra N truy vấn phụ cho các record con thay vì dùng JOIN ngay từ đầu.
*   **Thiết kế ETL cho 100M rows/day:** Chắc chắn phải dùng kiến trúc phân tán (Distributed workers như Spark/Databricks), Partitioning data theo time, sử dụng Message Queue (Kafka) làm buffer chống nghẽn, và Bulk/Batch processing khi write.

## 12. Redis & Caching
*   **Cache Invalidation (Làm mới cache):** Là vấn đề cực khó trong hệ thống phân tán. Làm sao để xoá hoặc cập nhật cache khi data dưới DB thay đổi mà không bị Stale Data.
*   **Redis không phù hợp khi nào?** Không phù hợp cho lưu trữ lâu dài cực lớn cần độ tin cậy tuyệt đối như OLTP DB (vì RAM đắt và Redis chủ yếu là in-memory).

## 13. System Debugging & Trade-offs
*   **Pipeline suddenly slow, check gì đầu tiên?** Flow chuẩn: CPU -> Memory -> DB latency -> Kafka lag -> Network -> Disk I/O -> Logs.
*   **Trade-off: Kafka vs RabbitMQ?** Kafka thiết kế theo dạng Append-only log phân tán, throughput khổng lồ, message có thể replay. RabbitMQ là Smart Broker / Dumb Consumer, thiên về routing phức tạp, low latency cho từng message riêng lẻ nhưng không replay được.
*   **Nếu schema source thay đổi đột ngột?** Cần cơ chế Schema Evolution (như Schema Registry của Kafka hoặc mergeSchema của Delta), đảm bảo Backward Compatibility để các consumer cũ không bị sập.

---
> **Lưu ý cực quan trọng khi đi phỏng vấn:** Đừng chỉ nêu lý thuyết. Luôn kết hợp: *Lý thuyết -> Đánh giá Trade-off (Được/Mất) -> Ứng dụng cụ thể vào dự án cũ của bạn (Forex / OpenSearch / Databricks).*

---

# PHẦN 3: PROJECT DEEP DIVE & KINH NGHIỆM THỰC TẾ

Interviewer sẽ xoáy sâu vào "Scope thực sự" và "Tại sao lại thiết kế như vậy (WHY)" đối với các dự án lớn trong CV của bạn. Hãy nắm vững các chi tiết sau:

## 14. Real-Time Forex Analytics (Dự án "đắt giá" nhất)
*   **Tại sao dùng Kafka?** Thay vì gọi trực tiếp API, Kafka giúp Decoupling (tách biệt Producer và Consumer), Buffering (chống sập hệ thống khi luồng data tăng đột biến), và hỗ trợ Event Streaming mở rộng tốt.
*   **1,000 events/sec đo bằng cách nào?** (Cần thành thật): "Đây là Approximate throughput em ghi nhận được trên Grafana/CloudWatch hoặc qua logs khi test load, không phải lúc nào cũng đạt đỉnh nhưng hệ thống hoàn toàn chịu tải được ở mức đó."
*   **Nếu Kafka bị down?** Hệ thống cần có cơ chế Retry ở Producer, Persistence (lưu tạm file local hoặc buffer memory), và khi sống lại thì Replay từ offset cuối.
*   **Partition Strategy:** Chia partition theo `Symbol` hoặc `Currency Pair` (VD: EUR/USD) để đảm bảo Ordering (dữ liệu của cùng 1 đồng tiền luôn vào cùng 1 partition và được xử lý tuần tự).
*   **Airflow - Tại sao ELT thay vì ETL?** Vì Databricks cực kỳ mạnh trong việc Compute phân tán, nên ta extract dạng thô (Raw) vào layer Bronze trước (EL), sau đó mới tận dụng cluster Databricks để Transform trong Data Lake (T).
*   **Medallion Architecture (Bronze - Silver - Gold):**
    *   *Bronze:* Raw data, immutable (không đổi), có thể lưu dạng JSON/CSV.
    *   *Silver:* Cleaned, validated (lọc null, xoá duplicate, chuẩn hóa timestamp), lưu bằng Delta Lake/Parquet.
    *   *Gold:* Business analytics (đã join, aggregate sẵn cho BI Tools).
*   **Tại sao dùng Delta Lake?** Hỗ trợ ACID transaction trên Data Lake (bình thường Data Lake không có), Schema Evolution (dễ dàng thêm cột mới), Time Travel (rollback data lỗi) và tối ưu hóa file Parquet rất tốt.

## 15. Financial News Intelligence (Crawler & NLP Pipeline)
*   **Crawler Flow:** Source -> Fetch -> Parse -> Clean -> Store.
*   **Dùng BeautifulSoup có limitation gì?** Khó xử lý Dynamic Javascript rendering (cần Selenium/Playwright), dễ gãy khi cấu trúc DOM HTML thay đổi, và dễ bị chặn (Anti-bot).
*   **Xử lý hàng triệu bài báo:** Phải dùng Async crawling (Aiohttp/Asyncio), chia Queue cho các Distributed Workers xử lý, batching insert vào DB, và Deduplication (loại bỏ bài trùng lặp qua URL hoặc Hash nội dung).
*   **Preprocessing Data:** Chuẩn hóa Text (Normalization), Token Cleanup, xóa Null/Duplicate.

## 16. AI Slide Generation Platform (Workflow Orchestration)
*   **Multi-agent Workflow:** Luồng phối hợp tuần tự: Research Agent -> Content Agent -> QA Agent -> Slide Formatter.
*   **Tại sao cần Async Workflow?** AI processing (đặc biệt LLM) mất rất nhiều thời gian (Long-running tasks). Không thể dùng Blocking Request vì sẽ timeout ngay. Phải dùng Async để giải phóng worker phục vụ request khác.
*   **Ưu điểm của FastAPI:** Hỗ trợ Async native, tốc độ cực nhanh, auto-generate Swagger docs, và Validate dữ liệu xịn bằng Pydantic.

## 17. OpenSearch Banking Plugin & Microservices
*   **OpenSearch khác DB SQL ở search thế nào?** OpenSearch sử dụng cấu trúc Inverted Index (chỉ mục ngược), cực kỳ tối ưu cho Full-text search, Ranking (chấm điểm độ tương quan) thay vì chỉ Exact Match (LIKE) như SQL.
*   **Tại sao gõ sai chính tả vẫn ra kết quả?** Nhờ Fuzzy Search dựa trên thuật toán Levenshtein (Khoảng cách chỉnh sửa - Edit Distance).
*   **Microservice Communication:** Các service giao tiếp với nhau qua REST/gRPC (Sync) hoặc Kafka/RabbitMQ (Async Event-Driven). Cần có Resilience như Retry hoặc Circuit Breaker.

## 18. Các câu hỏi xác thực kinh nghiệm (Honesty Check)
Interviewer sẽ hỏi những câu cực kỳ thực tế để xem bạn "Tự làm" hay "Leader làm sẵn, chỉ code task":
*   *"Khó khăn lớn nhất khi dùng Kafka là gì?"* (Ví dụ: rebalance liên tục, xử lý duplicate).
*   *"Em tự design system hay team lead design?"* -> Trả lời trung thực: "Team Lead vẽ High-level Architecture, em phụ trách implement luồng ETL chi tiết, design DB schema cho phần module của em và tuning performance."
*   *"Bug production nghiêm trọng nhất em từng gặp?"* -> (Dùng mô hình STAR để kể: Nguyên nhân -> Quá trình trace log -> Fix -> Bài học).

---
**TỔNG KẾT:** Khung CV của bạn hiện tại trông giống một Senior/Middle cứng cựa. Hãy hạn chế nói "cách làm" (HOW) mà hãy tập trung giải thích "tại sao lại chọn làm như vậy" (WHY) và "hệ thống có giới hạn gì" (TRADE-OFF).

---

# PHẦN 4: HƯỚNG DẪN TRẢ LỜI CHI TIẾT (Q&A MỞ RỘNG)

Phần này cung cấp câu trả lời mẫu cho các câu hỏi đào sâu về kỹ thuật và xác thực kinh nghiệm (Honesty Check) dựa trên các phần bạn đã yêu cầu.

## 19. Dự án VNPT Spring Boot (Xác thực nền tảng Backend)
Interviewer biết bạn code dựa trên tài liệu BA nên sẽ hỏi sâu về luồng xử lý thực tế:
*   **Một API flow em từng làm chạy như thế nào?** -> *"Luồng chuẩn là: Request đi vào `Controller` (nhận DTO) -> chuyển xuống `Service` (chứa Business Logic, gọi nhiều Repositories nếu cần) -> `Repository` (giao tiếp với Database qua JPA/Hibernate) -> trả kết quả ngược lại cho Client."*
*   **Validation xử lý ở đâu?** -> *"Xử lý ngay tại Controller bằng các annotation như `@Valid`, `@NotNull`, `@Size` trên DTO. Tránh để request sai lọt xuống Service làm tốn tài nguyên."*
*   **Transaction là gì? Em dùng ở đâu?** -> *"Transaction đảm bảo tính toàn vẹn dữ liệu (hoặc thành công tất cả, hoặc rollback tất cả). Em gắn `@Transactional` ở tầng Service khi một hàm phải insert/update dữ liệu vào nhiều bảng cùng lúc."*
*   **Bug khó nhất từng fix trong dự án này?** -> *"Ví dụ tình trạng N+1 query khi dùng JPA Fetch Type EAGER. Khi query 1 bảng cha nó kéo theo hàng chục câu query phụ. Em đã fix bằng cách dùng `@EntityGraph` hoặc viết lại câu `JOIN FETCH` trong Repository."*

## 20. Honesty Check - Xác thực kinh nghiệm thực tế
Những câu này dùng để kiểm tra xem bạn "có từng đụng tay vào hệ thống thật không":
*   **Em tự tay config Kafka chưa hay có sẵn?** -> *"Em từng config phần tạo Topic, set số lượng Partitions, Replica Factor. Còn setup cluster Zookeeper/KRaft thường do team DevOps làm."*
*   **Airflow DAG structure viết thế nào?** -> *"DAG của em thường bắt đầu bằng DummyOperator, sau đó phân nhánh qua PythonOperator/BashOperator. Em thiết kế các Task phải độc lập (Idempotent) để nếu fail thì Clear task và chạy lại an toàn."*
*   **Databricks dùng Notebook hay Jobs?** -> *"Trong lúc dev và explore data thì em dùng Notebook. Nhưng khi đưa lên Production thì em đóng gói thành các Databricks Workflow Jobs, trigger tự động theo lịch từ Airflow."*
*   **Consumer lag monitor thế nào?** -> *"Em không ngồi canh log mà dùng tool như **Kafka UI** hoặc **Burrow** / Grafana + Prometheus exporter để bắn Alert (Slack/Email) nếu lag vượt quá ngưỡng (ví dụ: > 10,000 messages chưa được đọc)."*
*   **Redis cache invalidation làm sao?** -> *"Đây là bài toán khó nhất. Bọn em dùng chiến lược kết hợp: set Time-To-Live (TTL) cho data tự động hết hạn, và chủ động xóa/cập nhật cache (Cache-Aside pattern) mỗi khi có lệnh Update/Delete thành công xuống Database."*
*   **OpenSearch Mapping là gì?** -> *"Giống như Schema của SQL. Nó định nghĩa các field (text, keyword, date). Em đặc biệt chú ý định nghĩa `Analyzer` cho các trường text để nó biết cách cắt từ (tokenize) phục vụ tìm kiếm Full-text."*

## 21. Behavioral Questions (Giải quyết tình huống)
Sử dụng công thức **STAR (Situation - Task - Action - Result)** để trả lời:
*   **Issue production khó nhất em từng gặp?**
    *   *Situation:* Hệ thống đột ngột phản hồi rất chậm, Kafka lag tăng đột biến.
    *   *Task:* Phải tìm ra nút thắt (bottleneck) trong 30 phút.
    *   *Action:* Em check tuần tự: Grafana xem CPU/RAM bình thường -> Check DB latency thấy tăng vọt -> Check log DB thấy có câu query full-table scan do thiếu index. Em đã kill session đang treo và add thêm Composite Index.
    *   *Result:* Hệ thống hết nghẽn, lag Kafka giảm về 0, tốc độ API tăng gấp 10 lần.
*   **Có conflict với team member bao giờ chưa?** -> *"Có, thường là khi chốt kiến trúc (VD: chọn REST hay Kafka). Giải pháp của em là không tranh cãi suông, em lên mạng tìm các bài Benchmark thực tế, liệt kê rõ Trade-off của cả 2, trình bày với số liệu cụ thể để team cùng vote."*
*   **Deadline quá gấp xử lý sao?** -> *"Em sẽ ngồi lại với PM/BA để thương lượng cắt giảm Scope (Phạm vi). Chốt lại các tính năng 'Must-have' để release đúng hẹn, các tính năng 'Nice-to-have' sẽ đưa vào Sprint sau, thay vì cố làm tất cả rồi lỗi."*
*   **Khó khăn lớn nhất khi dùng Kafka?** -> *"Là vấn đề xử lý Message lặp (Duplicate Message) do lỗi mạng (At-least-once). Em giải quyết bằng cách thiết kế hệ thống xử lý phía sau (Consumer DB) luôn có tính chất Idempotent (Dùng UPSERT dựa trên Unique Key thay vì INSERT thông thường)."*
