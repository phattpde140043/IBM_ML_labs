# Interview Prep — Forex Trading Data Pipeline Project
> Vị trí: Middle+ / Senior Python + SQL Developer  
> Mục đích: Giới thiệu dự án tâm đắc nhất trong buổi phỏng vấn

---

## 1. Elevator Pitch (30 giây)

> "Tôi đã xây dựng một **end-to-end data pipeline** cho hệ thống giao dịch Forex đa broker — từ việc thu thập dữ liệu giá real-time từ các nền tảng MT5 bằng MQL5 EA, xử lý nghiệp vụ giao dịch tại Python server, lưu trữ vào PostgreSQL, rồi streaming lên Databricks qua Debezium + Kafka và batch qua Airflow. Tại Databricks tôi thiết kế kiến trúc Medallion (Bronze → Silver → Gold) phục vụ báo cáo và chuẩn bị dữ liệu cho ML."

---

## 2. Kiến trúc tổng quan

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MT5 Trading Platforms                        │
│   [Broker A EA]        [Broker B EA]        [Broker C EA]  (MQL5)  │
└──────────┬──────────────────┬───────────────────┬───────────────────┘
           │ ZeroMQ/TCP       │ ZeroMQ/TCP         │ ZeroMQ/TCP
           ▼                  ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Python Server   │ │  Python Server   │ │  Python Server   │
│   broker-a       │ │   broker-b       │ │   broker-c       │
│  ┌────────────┐  │ │  ┌────────────┐  │ │  ┌────────────┐  │
│  │Data Intake │  │ │  │Data Intake │  │ │  │Data Intake │  │
│  │(asyncio)   │  │ │  │(asyncio)   │  │ │  │(asyncio)   │  │
│  └─────┬──────┘  │ │  └─────┬──────┘  │ │  └─────┬──────┘  │
│  ┌─────▼──────┐  │ │  ┌─────▼──────┐  │ │  ┌─────▼──────┐  │
│  │  Business  │  │ │  │  Business  │  │ │  │  Business  │  │
│  │   Logic    │  │ │  │   Logic    │  │ │  │   Logic    │  │
│  └─────┬──────┘  │ │  └─────┬──────┘  │ │  └─────┬──────┘  │
│  ┌─────▼──────┐  │ │  ┌─────▼──────┐  │ │  ┌─────▼──────┐  │
│  │ PostgreSQL │  │ │  │ PostgreSQL │  │ │  │ PostgreSQL │  │
│  │ schema:    │  │ │  │ schema:    │  │ │  │ schema:    │  │
│  │  broker_a  │  │ │  │  broker_b  │  │ │  │  broker_c  │  │
│  └─────┬──────┘  │ │  └─────┬──────┘  │ │  └─────┬──────┘  │
└────────┼─────────┘ └────────┼─────────┘ └────────┼──────────┘
         │ Debezium CDC        │ Debezium CDC        │ Debezium CDC
         ▼                    ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Kafka (shared cluster)                           │
│  topic: forex.broker_a.*   forex.broker_b.*   forex.broker_c.*     │
└─────────────────────────────────────────────────────────────────────┘
              │
      ┌───────┴──────────────────────┐
      │  Streaming                   │  Batch
      ▼                              ▼
┌───────────────┐          ┌──────────────────┐
│  Debezium     │          │  Apache Airflow   │
│  (CDC)        │          │  DAGs             │
│       │       │          │  - daily OHLCV    │
│       ▼       │          │  - account report │
│    Kafka      │          │  - signal history │
│  (Topics)     │          └────────┬─────────┘
└───────┬───────┘                   │
        │                           │
        └──────────┬────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Databricks (Delta Lake)                     │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  BRONZE — Raw ingestion                                       │ │
│  │  Partition: broker / symbol / date                            │ │
│  │  Format: Delta (append-only)                                  │ │
│  └────────────────────────┬──────────────────────────────────────┘ │
│                            │ Spark cleaning jobs                    │
│  ┌─────────────────────────▼────────────────────────────────────┐  │
│  │  SILVER — Cleaned, deduplicated, typed                       │  │
│  │  - Null / outlier handling                                    │  │
│  │  - Schema enforcement                                         │  │
│  │  - Deduplication (CDC idempotency)                            │  │
│  └─────────────────────────┬────────────────────────────────────┘  │
│                             │ Aggregation & feature engineering     │
│  ┌──────────────────────────▼───────────────────────────────────┐  │
│  │  GOLD — Business-ready                                       │  │
│  │  - OHLCV aggregates (1m/5m/1h/1d)                            │  │
│  │  - Account PnL snapshots                                      │  │
│  │  - ML feature tables (indicators, labels)                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Tech Stack

| Layer | Technology | Lý do chọn |
|-------|-----------|-----------|
| Data collection | MQL5 (MetaTrader 5) | Native platform cho MT5 brokers |
| Transport EA→Python | ZeroMQ / TCP socket | Bidirectional push, sub-ms latency, native MQL5 library — HTTP không đủ (xem ADR-002) |
| Core server | Python (asyncio) | Non-blocking I/O cho multi-broker concurrent |
| Primary storage | PostgreSQL | ACID, partitioning, hỗ trợ TimescaleDB extension |
| CDC / Streaming | Debezium + Kafka | Zero-code CDC, replayable, at-least-once delivery |
| Batch orchestration | Apache Airflow | DAG-based scheduling, retry, monitoring |
| Data platform | Databricks (Delta Lake) | ACID trên data lake, Z-Ordering, time travel |
| Processing | PySpark | Distributed processing cho large tick data |
| Serving | Delta tables → Power BI / SQL Warehouse | Business reporting |

---

## 4. Vai trò của tôi (My Contribution)

### 4.1 Layer 1 — MQL5 EA (Data Producer)
- Build EA thu thập **tick data** (bid/ask/volume) và **account state** (balance, equity, margin, open positions)
- Gửi dữ liệu về Python server qua ZeroMQ với message format chuẩn (JSON/MessagePack)
- Nhận lệnh ngược lại từ Python (open/close/modify order) và thực thi trên nền tảng

### 4.2 Layer 2 — Python Server (Core Logic)
- Deploy **một instance riêng biệt cho mỗi broker** — mỗi instance là một Docker container độc lập
- Validate và normalize dữ liệu: chuẩn hóa symbol names (EURUSD vs EUR/USD vs eurusd), timezone về UTC
- Implement **business logic layer**: tính toán signals, kiểm tra điều kiện entry/exit, risk management (SL/TP, position sizing)
- Publish lệnh giao dịch về EA sau khi xử lý nghiệp vụ
- Persist toàn bộ raw + processed data vào PostgreSQL schema riêng của broker đó
- Config per-broker qua environment variable — cùng codebase, khác `.env`

### 4.3 Layer 3 — PostgreSQL (Operational Store)
- Schema design cho time-series data (tick, OHLCV, signals, positions)
- **Table partitioning** theo `broker` và `date` cho `tick_data`
- Index strategy: B-tree trên `(symbol, timestamp)`, partial index cho open positions
- WAL tuning cho throughput cao (tick data viết liên tục)

### 4.4 Layer 4 — Streaming Pipeline (Debezium + Kafka)
- Cấu hình Debezium connector đọc PostgreSQL WAL (CDC)
- Thiết kế Kafka topics theo domain: `forex.ticks`, `forex.positions`, `forex.signals`
- Consumer group tại Databricks (Spark Structured Streaming)

### 4.5 Layer 5 — Batch Pipeline (Airflow)
- Viết DAGs cho: daily OHLCV aggregation, account performance report, signal history export
- Implement retry logic, SLA alerts, và data quality checks trong DAG tasks
- Parameterized DAGs để chạy backfill khi cần

### 4.6 Layer 6 — Databricks / Delta Lake (Analytics)
- Thiết kế **Medallion Architecture**: Bronze → Silver → Gold
- Partition strategy tại Bronze: `broker/symbol/year/month/day`
- Spark jobs: cleaning, deduplication, type casting tại Silver
- Feature engineering tại Gold: OHLCV aggregates, technical indicators, PnL metrics
- Chuẩn bị ML feature tables: labeling (entry/exit points), indicator computation

---

## 5. Data Tuning — Chi tiết kỹ thuật

### 5.1 PostgreSQL Tuning

#### Partitioning tick_data
```sql
-- Range partitioning theo ngày
CREATE TABLE tick_data (
    id          BIGSERIAL,
    broker      VARCHAR(20)  NOT NULL,
    symbol      VARCHAR(20)  NOT NULL,
    bid         NUMERIC(10,5) NOT NULL,
    ask         NUMERIC(10,5) NOT NULL,
    volume      NUMERIC(15,2),
    tick_time   TIMESTAMPTZ  NOT NULL
) PARTITION BY RANGE (tick_time);

-- Tạo partition theo tháng
CREATE TABLE tick_data_2024_01
    PARTITION OF tick_data
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Index trên mỗi partition
CREATE INDEX idx_tick_2024_01_symbol_time
    ON tick_data_2024_01 (symbol, tick_time DESC);
```

#### Index Strategy
```sql
-- Composite index cho query phổ biến nhất
CREATE INDEX idx_tick_symbol_time
    ON tick_data (symbol, tick_time DESC);

-- Partial index cho open positions (subset nhỏ, query thường xuyên)
CREATE INDEX idx_positions_open
    ON positions (broker, symbol, open_time)
    WHERE status = 'OPEN';

-- Covering index cho position lookup
CREATE INDEX idx_positions_covering
    ON positions (broker, ticket)
    INCLUDE (symbol, open_price, volume, sl, tp, status);
```

#### WAL & Write Tuning
```sql
-- postgresql.conf tuning cho high-throughput tick ingestion
-- wal_level = logical            -- bắt buộc cho Debezium CDC
-- max_wal_senders = 10
-- wal_keep_size = 1GB
-- synchronous_commit = off       -- chấp nhận mất tối đa 1 WAL chunk nếu crash
-- checkpoint_completion_target = 0.9
-- shared_buffers = 4GB           -- 25% RAM
-- effective_cache_size = 12GB    -- 75% RAM
-- work_mem = 64MB                -- per sort/hash operation
```

#### Query Optimization tại PostgreSQL
```sql
-- EXPLAIN ANALYZE trước khi deploy bất kỳ query nào lên production
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT symbol, DATE_TRUNC('minute', tick_time) AS minute,
       FIRST(bid ORDER BY tick_time) AS open,
       MAX(bid) AS high, MIN(bid) AS low,
       LAST(bid ORDER BY tick_time) AS close,
       SUM(volume) AS volume
FROM tick_data
WHERE broker = 'ICMarkets'
  AND symbol = 'EURUSD'
  AND tick_time >= NOW() - INTERVAL '1 day'
GROUP BY symbol, DATE_TRUNC('minute', tick_time)
ORDER BY minute;

-- Kiểm tra fragmentation / bloat
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

### 5.2 Kafka Tuning

| Parameter | Giá trị | Lý do |
|-----------|--------|-------|
| `num.partitions` | 12 (= broker count × 3) | Parallelism cho consumer group |
| `replication.factor` | 3 | Fault tolerance |
| `retention.ms` | 7 ngày | Replay capability khi Databricks down |
| `compression.type` | `lz4` | Low CPU cost, high throughput |
| `batch.size` | 65536 (64KB) | Tăng throughput, chấp nhận thêm latency nhỏ |
| `linger.ms` | 5 | Gom messages trước khi send |
| `max.poll.records` | 500 | Consumer batch size |

---

### 5.3 Databricks / Delta Lake Tuning

#### Partition Strategy tại Bronze
```python
# Partition by broker + symbol + date cho Bronze
df.write.format("delta") \
    .partitionBy("broker", "symbol", "year", "month", "day") \
    .mode("append") \
    .save("/mnt/bronze/tick_data")
```

#### Z-Ordering tại Silver (tối ưu cho point query)
```python
# Z-Order trên các cột hay filter nhất — sau khi OPTIMIZE
spark.sql("""
    OPTIMIZE silver.tick_data
    ZORDER BY (symbol, tick_time)
""")
```

#### Deduplication tại Silver (CDC idempotency)
```python
from delta.tables import DeltaTable

silver = DeltaTable.forName(spark, "silver.tick_data")

# MERGE để dedup — upsert dựa trên natural key
silver.alias("s").merge(
    incoming.alias("i"),
    "s.broker = i.broker AND s.symbol = i.symbol AND s.tick_time = i.tick_time"
).whenNotMatchedInsertAll() \
 .execute()
```

#### Auto Optimize & Auto Compact
```python
# Bật tại table level để tránh small files problem
spark.sql("""
    ALTER TABLE bronze.tick_data
    SET TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact'  = 'true'
    )
""")
```

#### Liquid Clustering (Databricks Runtime 13.3+)
```python
# Thay thế static partitioning khi data distribution không đều
spark.sql("""
    ALTER TABLE silver.tick_data
    CLUSTER BY (broker, symbol, tick_time)
""")
```

#### Data Skipping — Statistics Collection
```python
# Delta tự động collect min/max stats trên 32 cột đầu
# Đảm bảo filter columns ở đầu schema để tận dụng data skipping
spark.sql("""
    ALTER TABLE bronze.tick_data
    SET TBLPROPERTIES ('delta.dataSkippingNumIndexedCols' = '5')
""")
# Chỉ cần 5 cột đầu: broker, symbol, tick_time, bid, ask
```

#### Caching Hot Tables
```python
# Cache Silver tick data cho batch processing cuối ngày
spark.sql("CACHE SELECT * FROM silver.tick_data WHERE date = current_date()")
```

---

### 5.4 Airflow DAG Tuning

```python
# DAG pattern cho daily OHLCV aggregation
from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
    'execution_timeout': timedelta(hours=2),
    'sla': timedelta(hours=3),
}

with DAG(
    dag_id='forex_daily_ohlcv',
    default_args=default_args,
    schedule_interval='0 1 * * *',   # 1AM UTC daily
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['forex', 'batch', 'gold'],
) as dag:

    # Task 1: Data quality check trên Silver trước khi aggregate
    dq_check = PythonOperator(
        task_id='silver_data_quality_check',
        python_callable=check_silver_completeness,
        op_kwargs={'date': '{{ ds }}', 'min_rows_per_symbol': 1000}
    )

    # Task 2: Trigger Databricks job
    aggregate_ohlcv = DatabricksRunNowOperator(
        task_id='aggregate_to_gold_ohlcv',
        databricks_conn_id='databricks_prod',
        job_id=12345,
        notebook_params={'processing_date': '{{ ds }}'}
    )

    dq_check >> aggregate_ohlcv
```

---

## 6. Challenges & How I Solved Them

### Challenge 1: Tick data volume — PostgreSQL write throughput
**Vấn đề**: Nhận ~5,000 ticks/giây từ 3 brokers × 20 symbols. INSERT từng row không đủ nhanh.

**Giải pháp**:
- Dùng **`COPY` protocol** thay vì `INSERT` (10-50x nhanh hơn)
- **Buffer tại Python**: gom 1,000 ticks/batch, flush mỗi 100ms
- `synchronous_commit = off` cho tick table (acceptable risk: mất tối đa ~200ms data nếu crash)

```python
import psycopg2
from io import StringIO

def bulk_insert_ticks(conn, ticks: list[dict]):
    buffer = StringIO()
    for t in ticks:
        buffer.write(f"{t['broker']}\t{t['symbol']}\t{t['bid']}\t"
                     f"{t['ask']}\t{t['volume']}\t{t['tick_time']}\n")
    buffer.seek(0)
    with conn.cursor() as cur:
        cur.copy_from(buffer, 'tick_data',
                      columns=('broker','symbol','bid','ask','volume','tick_time'))
    conn.commit()
```

### Challenge 2: Debezium CDC lag khi PostgreSQL load cao
**Vấn đề**: WAL accumulation khi Debezium consumer chậm hơn producer.

**Giải pháp**:
- Tăng `max.queue.size` trong Debezium connector config
- Separate replication slot cho mỗi table nhóm (ticks / positions / signals)
- Monitor `pg_replication_slots` để detect lag:

```sql
SELECT slot_name, 
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS lag_size
FROM pg_replication_slots;
```

### Challenge 3: Small files problem tại Databricks Bronze
**Vấn đề**: Spark Structured Streaming tạo hàng trăm file nhỏ (micro-batch 30s) → read performance kém.

**Giải pháp**:
- Bật `autoCompact` tại table level
- Scheduled `OPTIMIZE` job chạy mỗi đêm sau khi streaming tạm dừng
- Tăng trigger interval của streaming job từ 30s → 5 phút để giảm số lượng files

### Challenge 4: Deduplication — CDC at-least-once delivery
**Vấn đề**: Kafka at-least-once → duplicate events tại Databricks.

**Giải pháp**:
- **MERGE (upsert)** tại Silver dựa trên natural key `(broker, symbol, tick_time)`
- Enable `delta.enableChangeDataFeed` để tracking downstream

### Challenge 5: Schema evolution khi broker thay đổi message format
**Vấn đề**: Broker cập nhật EA protocol → fields mới / đổi tên.

**Giải pháp**:
- Pydantic models tại Python layer cho validation + schema enforcement
- Delta Lake schema evolution: `mergeSchema = true` tại Bronze (accept new columns)
- Silver và Gold: strict schema với explicit mapping

---

## 7. Metrics & Impact (để trích dẫn trong phỏng vấn)

| Metric | Giá trị |
|--------|--------|
| Tick throughput | ~5,000 ticks/giây (peak) |
| End-to-end latency (EA → PostgreSQL) | < 50ms |
| CDC lag (PostgreSQL → Kafka) | < 500ms thông thường |
| Bronze ingestion latency | < 5 phút (streaming) |
| Daily data volume | ~50M tick records / ngày |
| OHLCV aggregation job duration | < 10 phút cho 1 ngày data |
| Data freshness tại Gold | Cập nhật mỗi 1 giờ (near-real-time) |

---

## 8. Câu hỏi phỏng vấn thường gặp & gợi ý trả lời

### "Tại sao chọn Kafka thay vì gửi thẳng từ PostgreSQL lên Databricks?"
> Kafka là **decoupling layer** — PostgreSQL không cần biết Databricks tồn tại. Nếu Databricks down, Kafka giữ message trong retention window (7 ngày), không mất data. Debezium đọc WAL → không tạo load trên PostgreSQL queries. Ngoài ra Kafka cho phép nhiều consumer (Databricks, monitoring, alerting) đọc cùng 1 topic.

### "Tại sao dùng Medallion Architecture thay vì load thẳng lên 1 layer?"
> Raw data từ EA có thể chứa lỗi (duplicate ticks, timezone offset, outlier prices do spread giật). Bronze giữ nguyên raw để có thể reprocess. Silver chỉ làm clean/deduplicate, không transform business logic. Gold là single source of truth cho báo cáo và ML. Mỗi layer có SLA và ownership riêng.

### "Làm sao handle khi một broker disconnect?"
> Python server có **health check loop** per broker connection. Khi detect disconnect: (1) log alert, (2) buffer pending orders, (3) attempt reconnect với exponential backoff, (4) khi reconnect: replay buffered state từ PostgreSQL. Kafka consumer tiếp tục nhận từ các broker còn online.

### "Partition strategy của bạn tại Databricks như thế nào?"
> Bronze: `broker/symbol/year/month/day` — align với query pattern thông thường (filter theo broker + symbol + ngày). Silver: Z-Order trên `(symbol, tick_time)` cho point queries. Gold OHLCV: partition theo `timeframe/symbol` vì báo cáo thường query theo timeframe.

### "Bạn đảm bảo data quality như thế nào?"
> 3 lớp kiểm tra: (1) **Pydantic validation** tại Python ingestion (type, range, required fields), (2) **Great Expectations** tại Silver (null rate, uniqueness, range checks), (3) **Airflow SLA + data quality tasks** trước khi push lên Gold.

### "Điều gì bạn sẽ làm khác nếu build lại?"
> Tôi sẽ dùng **Kafka Schema Registry** từ đầu để enforce schema evolution có kiểm soát. Và sẽ implement **idempotent consumer** tại Kafka layer thay vì dedup tại Silver — giảm bớt MERGE overhead. Ngoài ra sẽ tách Bronze streaming và batch sang 2 table riêng biệt trước khi merge tại Silver.

---

## 9. Diagram — Data Flow Tóm tắt

```
MQL5 EA ──(ZeroMQ)──► Python Server ──► PostgreSQL
                           │                 │
                   [Nghiệp vụ giao dịch]     │
                           │            ┌────┴─────────┐
                           │            │  Debezium    │
                           │            │  (CDC/WAL)   │
                           │            └─────┬────────┘
                           │                  ▼
                           │              Kafka Topics
                           │            [forex.ticks]
                           │            [forex.orders]
                           │            [forex.signals]
                           │                  │
                           │   Airflow DAGs   │
                           │   (batch/daily)  │
                           └──────────────────┤
                                              ▼
                                      Databricks Delta Lake
                                      ┌──────────────────┐
                                      │  Bronze (raw)    │
                                      │  partition:      │
                                      │  broker/sym/date │
                                      └────────┬─────────┘
                                               │ Spark clean
                                      ┌────────▼─────────┐
                                      │  Silver (clean)  │
                                      │  Z-Order: sym+ts │
                                      │  MERGE dedup     │
                                      └────────┬─────────┘
                                               │ Aggregation
                                      ┌────────▼─────────┐
                                      │  Gold (business) │
                                      │  OHLCV / PnL     │
                                      │  ML features     │
                                      └──────────────────┘
```

---

## 10. ADR-001 — Deploy một Python instance per broker

> **Context**: Hệ thống nhận dữ liệu real-time từ nhiều broker MT5 đồng thời. Câu hỏi thiết kế: gom tất cả broker vào một Python process hay deploy process riêng cho từng broker?

### Quyết định
Deploy **một Python instance (Docker container) riêng biệt cho mỗi broker.**

### Lý do

**1. Không có cross-broker shared state tại Python layer**
Mỗi broker xử lý nghiệp vụ hoàn toàn độc lập — signal, position, account state đều thuộc về broker đó. Không có logic nào cần đọc dữ liệu của broker khác tại thời điểm xử lý. Cross-broker analysis chỉ xảy ra tại Databricks Silver/Gold — đúng layer, đúng thời điểm.

Nếu không có shared state, gom chung process chỉ tạo ra coupling không cần thiết mà không mang lại lợi ích gì.

**2. Fault isolation thực sự**
Broker A mất kết nối, EA crash, hoặc business logic lỗi không ảnh hưởng Broker B và C. Với 1 shared process, một unhandled exception hoặc memory leak từ 1 broker worker có thể làm sập toàn bộ hệ thống.

**3. Independent deployment lifecycle**
Thêm broker mới → spin up container mới, không chạm vào instance đang chạy. Cập nhật config hoặc business logic của broker A → restart container broker-a, broker B và C tiếp tục bình thường không bị gián đoạn.

**4. Config isolation**
Mỗi broker có endpoint riêng, credentials riêng, symbol mapping riêng, risk parameter riêng. Quản lý qua `.env` per-container thay vì 1 config file lớn với conditional logic theo broker.

```
broker-a/
  .env  →  ZMQ_PORT=5550, BROKER_ID=icmarkets, MAX_SPREAD=3
broker-b/
  .env  →  ZMQ_PORT=5551, BROKER_ID=xm,        MAX_SPREAD=5
broker-c/
  .env  →  ZMQ_PORT=5552, BROKER_ID=exness,    MAX_SPREAD=2
```

**5. Observability rõ ràng**
Log, metrics, alert được tag theo `broker_id` ngay từ container level. Khi debug, biết ngay vấn đề thuộc broker nào mà không cần lọc qua shared log stream.

**6. Horizontal scaling per broker**
Nếu một broker có volume lớn hơn (nhiều symbols, high-frequency), scale container đó lên mà không ảnh hưởng broker khác.

### Trade-off chấp nhận được
- Nhiều process hơn để monitor (3 containers thay vì 1)
- Mỗi container có overhead memory riêng (~50–100MB/instance)
- Connection pool PostgreSQL tách riêng per instance

→ Các trade-off này được giải quyết bằng Docker Compose (local) hoặc k8s (production) — ops overhead không đáng kể so với lợi ích isolation.

### Alternatives rejected
- **Shared process + asyncio workers**: Phù hợp khi có cross-broker shared state. Trong trường hợp này không có, nên coupling không có lý do tồn tại.
- **Thread per broker**: GIL giới hạn true parallelism; crash isolation kém hơn process.

---

## 11. Interview Q&A — Python Middle thiên SQL/Data Processing

> 20 câu hỏi cao xác suất gặp khi giới thiệu dự án này. Trả lời bằng ngôn ngữ tự nhiên, kèm SQL/code minh họa.

---

### Q1. Tick_data có 50 triệu records/ngày, query bắt đầu chậm sau 6 tháng. Bạn xử lý thế nào?

**Trả lời**: Tôi tiếp cận theo 4 bước — đo trước, rồi mới fix.

**Bước 1 — Đo bằng EXPLAIN ANALYZE:**
```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM tick_data
WHERE symbol = 'EURUSD'
  AND tick_time >= NOW() - INTERVAL '7 days';
```
Nhìn vào: có `Seq Scan` không, `Buffers: shared hit` vs `read` tỉ lệ thế nào, `rows` estimate có lệch thực tế không (nếu lệch nhiều → stale statistics).

**Bước 2 — Kiểm tra index hit rate:**
```sql
SELECT relname,
       idx_scan, seq_scan,
       idx_scan::float / NULLIF(idx_scan + seq_scan, 0) AS index_hit_ratio
FROM pg_stat_user_tables
WHERE relname = 'tick_data';
```
Nếu `index_hit_ratio < 0.99` với bảng lớn → vấn đề.

**Bước 3 — Partition theo thời gian** (nếu chưa có):
Sau 6 tháng × 50M rows/ngày = ~9 tỷ rows. Planner phải scan toàn bộ bảng kể cả khi filter theo ngày. Tách partition theo tháng → planner chỉ scan partition liên quan (**partition pruning**).

**Bước 4 — Archive dữ liệu cũ:**
Tick data > 3 tháng hầu như không query ngoài báo cáo định kỳ. Move sang cold storage (tablespace chậm hơn hoặc Databricks Bronze) để working set của PostgreSQL nhỏ lại, buffer cache hiệu quả hơn.

**Bước 5 — Materialized View cho báo cáo:**
```sql
CREATE MATERIALIZED VIEW mv_ohlcv_1m AS
SELECT symbol,
       DATE_TRUNC('minute', tick_time) AS ts,
       FIRST(bid ORDER BY tick_time)   AS open,
       MAX(bid) AS high, MIN(bid) AS low,
       LAST(bid ORDER BY tick_time)    AS close,
       SUM(volume) AS volume
FROM tick_data
WHERE tick_time >= NOW() - INTERVAL '30 days'
GROUP BY symbol, DATE_TRUNC('minute', tick_time);

CREATE UNIQUE INDEX ON mv_ohlcv_1m (symbol, ts);

-- Refresh mỗi phút không block read
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ohlcv_1m;
```

**Follow-up: Tại sao partition lại nhanh hơn index?**
Index vẫn phải traverse B-tree rồi fetch rows từ heap — với hàng tỷ rows, heap scatter rất lớn, sinh ra nhiều random I/O. Partition pruning **loại bỏ hoàn toàn** các partition không liên quan trước khi planner bắt đầu — không scan, không I/O. Ngoài ra statistics per-partition chính xác hơn → planner estimate tốt hơn → chọn đúng join strategy.

---

### Q2. Tại sao index `(symbol, tick_time)` thay vì `(tick_time, symbol)`?

**Trả lời**: Query phổ biến nhất trong hệ thống luôn có dạng:
```sql
WHERE symbol = 'EURUSD'
  AND tick_time >= '2026-06-01'
```

PostgreSQL sử dụng **left-most prefix rule** — chỉ tận dụng được index nếu filter bắt đầu từ cột đầu tiên. Với `(symbol, tick_time)`:
- `symbol = 'EURUSD'` → seek đến đúng vị trí trong B-tree (equality, rất chọn lọc)
- `tick_time >= ...` → range scan tiếp theo trong subtree của symbol đó

Với `(tick_time, symbol)` và query trên:
- `tick_time >= ...` → range scan toàn bộ bảng theo thời gian
- `symbol = 'EURUSD'` → filter thêm sau, không benefit từ index structure

**Follow-up: `WHERE tick_time > NOW() - INTERVAL '1 day'` — index `(symbol, tick_time)` có dùng không?**

Không dùng được một cách hiệu quả, vì query không có filter trên `symbol` (cột đầu). PostgreSQL sẽ chọn `Seq Scan` hoặc `Bitmap Index Scan` kém hiệu quả. Giải pháp: tạo thêm index riêng `(tick_time DESC)` cho pattern này, hoặc dùng partition pruning thay thế.

---

### Q3. Một query chạy 30 giây. Bạn debug thế nào?

**Trả lời** — quy trình từng bước:

**B1 — EXPLAIN ANALYZE:**
```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT TEXT) <query>;
```
Đọc output từ dưới lên (inner-most node trước). Tìm node có `actual time` lớn nhất.

**B2 — Nhận diện node vấn đề:**
| Node | Dấu hiệu nguy hiểm |
|------|-------------------|
| `Seq Scan` | Trên bảng lớn — thiếu index |
| `Sort` | `Sort Method: external merge Disk` → spill ra disk, thiếu `work_mem` |
| `Hash Join` | `Batches: N > 1` → hash table tràn disk |
| `Nested Loop` | Loops > 10,000 → N+1 query ngầm |
| `rows=1 / actual rows=5000000` | Estimate lệch lớn → stale statistics |

**B3 — Kiểm tra pg_stat_statements:**
```sql
SELECT query,
       calls,
       mean_exec_time,
       total_exec_time,
       rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```
Tìm query có `mean_exec_time` cao và `calls` nhiều → đây là target ưu tiên.

**B4 — Các fix thường gặp:**
- Thêm/sửa index phù hợp với access pattern
- `ANALYZE <table>` nếu statistics stale
- Tăng `work_mem` nếu Sort/Hash spill: `SET work_mem = '256MB';`
- Rewrite query: loại bỏ function trên cột filter, tách CTE phức tạp

---

### Q4. Khi nào Index làm hệ thống chậm hơn?

**Trả lời**: Index là overhead write — mỗi `INSERT`, `UPDATE`, `DELETE` đều phải cập nhật tất cả index trên bảng đó.

Với `tick_data` nhận 5,000 ticks/giây, nếu có 10 index:
- Mỗi INSERT → 10 B-tree update
- 5,000 ticks/s × 10 index = 50,000 index page writes/s
- I/O và WAL tăng mạnh → throughput giảm, latency tăng

**Nguyên tắc cho bảng write-heavy:**
- Chỉ tạo index khi có query cụ thể cần nó
- Đo `pg_stat_user_indexes`: nếu `idx_scan = 0` sau 1 tuần → index vô dụng, drop đi
- Partial index giúp giảm kích thước index: chỉ index subset rows thực sự query
- Dùng `CONCURRENTLY` khi tạo/drop index trên production để tránh lock

```sql
-- Kiểm tra index nào không được dùng
SELECT indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE relname = 'tick_data'
  AND idx_scan = 0;
```

---

### Q5. Bạn có dùng Composite Index. Làm sao biết Index thực sự được sử dụng?

**Trả lời**: Dùng `EXPLAIN ANALYZE` và tìm keyword trong output:

```sql
EXPLAIN ANALYZE
SELECT * FROM tick_data
WHERE symbol = 'EURUSD'
  AND tick_time >= NOW() - INTERVAL '1 hour';
```

**Output tốt** (index được dùng):
```
Index Scan using idx_tick_symbol_time on tick_data
  Index Cond: ((symbol = 'EURUSD') AND (tick_time >= ...))
  Buffers: shared hit=42 read=3
```

**Output xấu** (index bị bỏ qua):
```
Seq Scan on tick_data
  Filter: ((symbol = 'EURUSD') AND (tick_time >= ...))
  Rows Removed by Filter: 49876543
```

Ngoài ra kiểm tra thống kê thực tế:
```sql
SELECT indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE relname = 'tick_data';
```
`idx_scan` tăng sau khi chạy query → index đang được dùng.

**Bitmap Index Scan** xuất hiện khi PostgreSQL dùng nhiều index kết hợp hoặc kết quả trả về nhiều rows — vẫn tốt hơn Seq Scan.

---

### Q6. Tại sao query này chậm?

```sql
SELECT * FROM tick_data WHERE DATE(tick_time) = '2026-06-01';
```

**Trả lời**: `DATE(tick_time)` là **function call trên cột index** — PostgreSQL phải tính `DATE(tick_time)` cho mỗi row trước khi so sánh. Index trên `tick_time` **không thể dùng** vì giá trị trong index là `tick_time` nguyên bản, không phải `DATE(tick_time)`.

→ Kết quả: `Seq Scan` toàn bảng 9 tỷ rows.

**Rewrite đúng (SARGable):**
```sql
SELECT * FROM tick_data
WHERE tick_time >= '2026-06-01 00:00:00'
  AND tick_time <  '2026-06-02 00:00:00';
```

Điều kiện bây giờ là range scan trực tiếp trên `tick_time` → index được dùng, planner thực hiện `Index Scan`.

**Nguyên tắc chung — SARGable predicate**: Không bao giờ đặt function/expression lên cột trong `WHERE` nếu có index. Các anti-pattern tương tự:
```sql
-- Chậm
WHERE UPPER(symbol) = 'EURUSD'
WHERE EXTRACT(YEAR FROM tick_time) = 2026
WHERE broker_id + 0 = 5

-- Đúng
WHERE symbol = 'EURUSD'          -- normalize data khi insert
WHERE tick_time >= '2026-01-01'
WHERE broker_id = 5
```

---

### Q7. Bạn chọn NUMERIC hay DOUBLE cho giá Forex?

**Trả lời**: `NUMERIC(10,5)` — không bao giờ dùng `FLOAT` hay `DOUBLE PRECISION` cho dữ liệu tài chính.

**Lý do**: `FLOAT`/`DOUBLE` là IEEE 754 binary floating point — không biểu diễn chính xác nhiều số thập phân. Ví dụ:
```python
>>> 1.1 + 2.2
3.3000000000000003   # lỗi làm tròn
```

Với giá Forex, sai lệch ở chữ số thứ 5 thập phân (pip) trực tiếp ảnh hưởng P&L calculation. Trong hệ thống trading, `0.00001` sai → tính sai SL/TP → lệnh sai.

`NUMERIC(10,5)` lưu chính xác tuyệt đối dưới dạng decimal:
- `10` digits tổng, `5` sau dấu phẩy
- Đủ cho giá như `1.12345` (EURUSD) hay `151.234` (USDJPY)
- Trade-off: chậm hơn FLOAT ~2-3x khi tính toán, nhưng với tick data chủ yếu là write và aggregate — acceptable

```sql
bid   NUMERIC(10, 5) NOT NULL,
ask   NUMERIC(10, 5) NOT NULL,
-- spread = ask - bid → chính xác tuyệt đối
```

---

### Q8. Có 2 giao dịch cùng update Position. Làm sao tránh race condition?

**Trả lời**: Có 2 pattern, chọn theo use case.

**Pattern 1 — Pessimistic Locking (SELECT FOR UPDATE):**
Dùng khi conflict xảy ra thường xuyên, hoặc khi việc retry tốn kém.
```sql
BEGIN;

SELECT position_id, volume, status
FROM positions
WHERE position_id = $1
FOR UPDATE;  -- lock row ngay khi read, transaction khác sẽ block

-- Thực hiện business logic sau khi có lock
UPDATE positions
SET volume = volume - $2,
    updated_at = NOW()
WHERE position_id = $1;

COMMIT;
```
Transaction thứ 2 gọi `SELECT FOR UPDATE` cùng row sẽ **block** cho đến khi transaction 1 commit/rollback.

**Pattern 2 — Optimistic Locking (version column):**
Dùng khi conflict hiếm, muốn tránh lock overhead.
```sql
-- Schema có thêm cột version
ALTER TABLE positions ADD COLUMN version INT DEFAULT 0;

-- Read
SELECT position_id, volume, version FROM positions WHERE position_id = $1;
-- Giả sử đọc được version = 5

-- Update kèm version check
UPDATE positions
SET volume = volume - $2,
    version = version + 1
WHERE position_id = $1
  AND version = 5;  -- chỉ update nếu chưa ai thay đổi
-- Nếu affected rows = 0 → có người update trước → retry
```

**Chọn cái nào cho dự án này?** Tôi dùng `SELECT FOR UPDATE` vì lệnh giao dịch cần đảm bảo exactly-once execution — không thể để 2 lệnh đồng thời close cùng 1 position.

---

### Q9. Bạn chọn Isolation Level nào?

**Trả lời**: Phụ thuộc vào operation.

| Operation | Isolation Level | Lý do |
|-----------|----------------|-------|
| Đọc tick data thông thường | `READ COMMITTED` (default) | Không cần consistency cao, throughput quan trọng |
| Tính toán PnL / báo cáo | `REPEATABLE READ` | Đảm bảo tất cả reads trong transaction thấy snapshot nhất quán |
| Xử lý lệnh giao dịch | `READ COMMITTED` + `SELECT FOR UPDATE` | Lock explicit tốt hơn SERIALIZABLE về performance |
| Reconciliation cuối ngày | `SERIALIZABLE` | Cần đảm bảo không có phantom read khi tính balance |

**Trade-off rõ ràng**:
- `READ UNCOMMITTED`: PostgreSQL không support (luôn dùng tối thiểu READ COMMITTED)
- `READ COMMITTED`: Phantom reads và non-repeatable reads có thể xảy ra
- `REPEATABLE READ`: Ngăn non-repeatable read, nhưng transaction bị abort nếu có conflict → cần retry logic
- `SERIALIZABLE`: An toàn nhất nhưng throughput giảm đáng kể, nhiều serialization failures

**Thực tế trong dự án**: Phần lớn dùng `READ COMMITTED` kết hợp explicit locking (`FOR UPDATE`) thay vì nâng isolation level — kiểm soát tốt hơn và predictable hơn.

---

### Q10. Khi nào dùng Materialized View?

**Trả lời**: Khi có query aggregate nặng chạy thường xuyên trên data ít thay đổi trong ngắn hạn.

**Use case trong dự án**: PnL Report tổng hợp cần `SUM`, `COUNT`, `AVG` trên hàng trăm triệu rows:
```sql
-- Query gốc: chạy trực tiếp → 20-30 giây
SELECT broker, symbol,
       DATE_TRUNC('hour', tick_time) AS hour,
       COUNT(*)           AS tick_count,
       AVG(ask - bid)     AS avg_spread,
       SUM(volume)        AS total_volume
FROM tick_data
WHERE tick_time >= NOW() - INTERVAL '7 days'
GROUP BY broker, symbol, DATE_TRUNC('hour', tick_time);

-- Materialized View: pre-compute, refresh mỗi giờ
CREATE MATERIALIZED VIEW mv_hourly_stats AS
<query trên>;

CREATE UNIQUE INDEX ON mv_hourly_stats (broker, symbol, hour);

-- Refresh không block đọc (cần unique index)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_hourly_stats;
```

**Khi KHÔNG nên dùng**:
- Data thay đổi real-time và report cần fresh data ngay lập tức
- Data volume nhỏ, query đã nhanh dưới 1 giây
- Refresh quá thường xuyên làm mất lợi thế (mỗi 30s refresh trên 9 tỷ rows thì worse than useless)

**Thay thế tốt hơn trong nhiều trường hợp**: Tổng hợp tại Databricks Gold layer — pre-aggregate ở đó, serve qua Delta table hoặc SQL Warehouse.

---

### Q11. Làm sao tìm top 5 symbol có volume lớn nhất?

**Trả lời cơ bản:**
```sql
SELECT symbol,
       SUM(volume) AS total_volume
FROM tick_data
GROUP BY symbol
ORDER BY total_volume DESC
LIMIT 5;
```

**Follow-up: 50 tỷ rows thì sao?**

Query trên sẽ Full Table Scan toàn bộ 50 tỷ rows → không thể chấp nhận trên production.

**Giải pháp 1 — Partition Pruning** (nếu chỉ cần trong khoảng thời gian):
```sql
-- Partition pruning chỉ scan partition liên quan
SELECT symbol, SUM(volume)
FROM tick_data
WHERE tick_time >= '2026-06-01'  -- prune các partition cũ
GROUP BY symbol
ORDER BY SUM(volume) DESC
LIMIT 5;
```

**Giải pháp 2 — Aggregate Table** (tốt nhất cho production):
```sql
-- Bảng tổng hợp cập nhật incremental
CREATE TABLE daily_symbol_stats (
    symbol      VARCHAR(20),
    stat_date   DATE,
    total_volume NUMERIC(20,2),
    tick_count  BIGINT,
    PRIMARY KEY (symbol, stat_date)
);

-- Airflow DAG chạy mỗi ngày aggregate ngày hôm qua
INSERT INTO daily_symbol_stats
SELECT symbol, DATE(tick_time), SUM(volume), COUNT(*)
FROM tick_data
WHERE tick_time::date = CURRENT_DATE - 1
GROUP BY symbol, DATE(tick_time)
ON CONFLICT (symbol, stat_date) DO UPDATE
SET total_volume = EXCLUDED.total_volume,
    tick_count   = EXCLUDED.tick_count;

-- Query top 5 chỉ scan bảng nhỏ
SELECT symbol, SUM(total_volume)
FROM daily_symbol_stats
GROUP BY symbol
ORDER BY SUM(total_volume) DESC
LIMIT 5;
```

**Giải pháp 3 — Đẩy sang Databricks Gold**: Aggregate tại Gold layer, serve qua SQL Warehouse — đây là pattern chính trong kiến trúc của dự án.

---

### Q12. Tại sao dùng COPY thay vì INSERT?

**Trả lời**: `INSERT` là SQL statement — mỗi lần gọi PostgreSQL phải parse SQL, plan, execute, và update index. Với 5,000 ticks/giây, đó là 5,000 round-trip SQL overhead mỗi giây.

`COPY` là **binary stream protocol** — bỏ qua SQL parser, ghi trực tiếp vào storage engine:

```
INSERT path:  SQL parse → Plan → Execute → Index update (×5000/s)
COPY path:    Stream data → Bulk load → Index update once
```

Nhanh hơn **10–50x** trong thực tế.

```python
from io import StringIO
import psycopg2

def bulk_insert_ticks(conn, ticks: list[dict]) -> None:
    buf = StringIO()
    for t in ticks:
        buf.write(
            f"{t['broker']}\t{t['symbol']}\t{t['bid']}\t"
            f"{t['ask']}\t{t['volume']}\t{t['tick_time']}\n"
        )
    buf.seek(0)
    with conn.cursor() as cur:
        cur.copy_from(
            buf, 'tick_data',
            columns=('broker', 'symbol', 'bid', 'ask', 'volume', 'tick_time')
        )
    conn.commit()
```

**Thực tế trong dự án**: Python server buffer 1,000 ticks trong 100ms, flush bằng `COPY` một lần → throughput đạt ~50,000 ticks/giây thay vì ~2,000 với INSERT.

**Lưu ý**: `COPY` không có per-row error handling — nếu 1 row lỗi, cả batch rollback. Cần validate dữ liệu trước ở Python layer (Pydantic) trước khi đưa vào COPY.

---

### Q13. WAL là gì?

**Trả lời**: WAL — **Write-Ahead Log** — là cơ chế đảm bảo durability và recovery của PostgreSQL.

**Nguyên tắc cốt lõi**: Bất kỳ thay đổi nào trên data phải được **ghi vào WAL trước**, rồi mới apply lên data pages thực sự.

```
Transaction COMMIT
     ↓
Ghi log record vào WAL (sequential write — nhanh)
     ↓
Ack success về client
     ↓
(Async) Flush dirty pages từ buffer → Disk
```

**Tại sao không ghi thẳng vào data pages?** Data pages nằm ở random locations trên disk → random I/O chậm. WAL là sequential write → nhanh hơn nhiều.

**WAL phục vụ 4 mục đích trong dự án**:
1. **Durability**: Crash xảy ra → recovery đọc WAL, replay lại các transaction chưa flush
2. **Replication**: Standby replica stream WAL từ primary → luôn đồng bộ
3. **CDC với Debezium**: Debezium đọc WAL như một logical replication client → capture mọi INSERT/UPDATE/DELETE
4. **Point-in-time recovery**: Kết hợp base backup + WAL → restore về bất kỳ thời điểm nào

**Follow-up: Debezium đọc ở đâu?**
Debezium dùng **PostgreSQL Logical Replication** — đăng ký một replication slot, PostgreSQL decode WAL records thành logical change events (row-level: INSERT/UPDATE/DELETE với before/after values), Debezium đọc events này và publish lên Kafka.

---

### Q14. Nếu Debezium bị down 3 tiếng thì mất dữ liệu không?

**Trả lời**: **Không mất** — vì PostgreSQL giữ WAL trong replication slot cho đến khi consumer đọc hết.

Cơ chế: khi Debezium tạo replication slot (`pg_create_logical_replication_slot`), PostgreSQL cam kết **không xóa WAL segments** cho đến khi slot đó confirm đã đọc. Debezium lưu offset (LSN — Log Sequence Number) của lần đọc cuối. Khi restart, Debezium resume từ LSN đó → replay đầy đủ 3 tiếng data bị miss.

**Follow-up: Khi nào mất dữ liệu?**

Mất khi **WAL bị cleanup trước khi Debezium đọc** — xảy ra nếu:
1. Replication slot bị drop thủ công
2. `wal_keep_size` quá nhỏ và slot bị force-invalidate (PostgreSQL 13+: `max_slot_wal_keep_size`)
3. Disk đầy → PostgreSQL buộc phải xóa WAL → invalidate slot

**Monitor replication lag để phát hiện sớm:**
```sql
SELECT slot_name,
       confirmed_flush_lsn,
       pg_size_pretty(
           pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)
       ) AS lag_size,
       active
FROM pg_replication_slots;
```
Nếu `lag_size` > threshold → alert ngay, trước khi disk đầy.

---

### Q15. Có bảng Positions, 90% query là `WHERE status='OPEN'`. Bạn thiết kế index gì?

**Trả lời**: **Partial Index** — index chỉ trên subset rows có `status='OPEN'`.

```sql
CREATE INDEX idx_positions_open
    ON positions (symbol, open_time)
    WHERE status = 'OPEN';
```

**Tại sao Partial Index tốt hơn full index?**
- `OPEN` positions thường chỉ chiếm 1–5% tổng rows (phần lớn là `CLOSED`)
- Full index `(symbol, open_time)` phải index 100% rows → lớn, chậm hơn khi maintain
- Partial index chỉ index 1–5% rows → nhỏ hơn 20x, fit vào RAM dễ hơn, write overhead ít hơn
- Query với `WHERE status='OPEN'` → PostgreSQL chọn partial index ngay

**Query sẽ dùng index này:**
```sql
-- ✓ Dùng partial index
SELECT * FROM positions
WHERE status = 'OPEN' AND symbol = 'EURUSD';

-- ✗ Không dùng (vì không có status='OPEN' trong WHERE)
SELECT * FROM positions WHERE symbol = 'EURUSD';
```

---

### Q16. Bạn sẽ tối ưu query này thế nào?

```sql
SELECT * FROM positions
WHERE broker='ICMarkets' AND symbol='EURUSD' AND status='OPEN';
```

**Trả lời**: Kết hợp Composite Index + Partial Index:

```sql
CREATE INDEX idx_positions_broker_symbol_open
    ON positions (broker, symbol, open_time DESC)
    WHERE status = 'OPEN';
```

**Giải thích**:
- `WHERE status='OPEN'` → partial index loại bỏ 95–99% rows ngay từ đầu
- `(broker, symbol)` → equality filter trên 2 cột đầu → B-tree seek chính xác
- `open_time DESC` → nếu query sau đó cần `ORDER BY open_time DESC`, index đã sorted sẵn → không cần Sort node

Thêm `INCLUDE` nếu muốn covering index (tránh heap fetch):
```sql
CREATE INDEX idx_positions_broker_symbol_open
    ON positions (broker, symbol, open_time DESC)
    INCLUDE (position_id, volume, open_price, sl, tp)
    WHERE status = 'OPEN';
```
Query `SELECT position_id, volume, open_price, sl, tp` không cần đọc heap nữa → `Index Only Scan`.

---

### Q17. Có 100 triệu rows. `OFFSET 10000000` bắt đầu chậm. Làm sao xử lý?

**Trả lời**: Đây là vấn đề kinh điển của **offset-based pagination**. `OFFSET N` buộc PostgreSQL phải đọc và discard N rows đầu tiên — với `OFFSET 10,000,000`, PostgreSQL đọc 10 triệu rows rồi bỏ đi, chỉ trả về 100 rows cuối.

**Giải pháp: Keyset Pagination (Cursor Pagination)**

```sql
-- Page đầu tiên
SELECT position_id, symbol, open_time, volume
FROM positions
WHERE status = 'OPEN'
ORDER BY open_time DESC, position_id DESC
LIMIT 100;

-- Page tiếp theo: dùng giá trị cuối của page trước làm cursor
-- Giả sử page trước kết thúc tại open_time='2026-06-01 10:00:00', position_id=99999
SELECT position_id, symbol, open_time, volume
FROM positions
WHERE status = 'OPEN'
  AND (open_time, position_id) < ('2026-06-01 10:00:00', 99999)
ORDER BY open_time DESC, position_id DESC
LIMIT 100;
```

**Tại sao nhanh hơn?** Index trên `(open_time DESC, position_id DESC)` + partial `WHERE status='OPEN'` → seek trực tiếp đến cursor position, không scan rows đã trả về.

**Trade-off của Keyset Pagination**:
- ✓ O(1) thay vì O(N) — performance không giảm khi page sâu
- ✗ Không nhảy đến page tùy ý (phải đi tuần tự)
- ✗ Phức tạp hơn implement phía client

---

### Q18. Bạn sẽ chọn Redis hay PostgreSQL cho giá EURUSD hiện tại cần đọc 10,000 lần/giây?

**Trả lời**: **Redis** cho current state, **PostgreSQL** cho historical data — hai use case khác nhau hoàn toàn.

**Lý do chọn Redis cho current price:**
- Redis in-memory → sub-millisecond read latency (<1ms vs ~5-10ms PostgreSQL)
- 10,000 reads/giây cho PostgreSQL là feasible nhưng tạo load không cần thiết
- Redis `GET eurusd:bid` → O(1), không có SQL parse, không có buffer pool lookup
- Python server update Redis mỗi khi nhận tick mới, clients đọc từ Redis

```python
# Python server update Redis khi nhận tick
async def on_tick_received(tick: Tick):
    await redis.hset(
        f"price:{tick.broker}:{tick.symbol}",
        mapping={"bid": str(tick.bid), "ask": str(tick.ask), "ts": tick.tick_time.isoformat()}
    )
    await redis.expire(f"price:{tick.broker}:{tick.symbol}", 300)  # TTL 5 phút

# Client đọc current price
current = await redis.hgetall("price:icmarkets:EURUSD")
```

**PostgreSQL giữ vai trò:**
- Source of truth cho historical data
- Transaction processing (order management)
- Audit trail đầy đủ
- CDC source cho Debezium

**Pattern tổng quát**: Redis là **cache/hot store** cho real-time reads, PostgreSQL là **system of record** cho persistence và queries lịch sử.

---

### Q19. Nếu PostgreSQL CPU 100%, bạn kiểm tra gì đầu tiên?

**Trả lời**: Không guess — đo ngay.

**Bước 1 — Active queries đang chạy:**
```sql
SELECT pid, now() - pg_stat_activity.query_start AS duration,
       query, state, wait_event_type, wait_event
FROM pg_stat_activity
WHERE state != 'idle'
  AND query_start < NOW() - INTERVAL '5 seconds'
ORDER BY duration DESC;
```
Tìm query nào đang chạy lâu, đang `waiting` vì gì.

**Bước 2 — Top queries theo CPU (pg_stat_statements):**
```sql
SELECT LEFT(query, 100) AS query_snippet,
       calls,
       total_exec_time / 1000 AS total_sec,
       mean_exec_time AS mean_ms,
       rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

**Bước 3 — Kiểm tra lock:**
```sql
SELECT blocked.pid,
       blocked.query AS blocked_query,
       blocking.pid AS blocking_pid,
       blocking.query AS blocking_query
FROM pg_stat_activity AS blocked
JOIN pg_stat_activity AS blocking
    ON blocking.pid = ANY(pg_blocking_pids(blocked.pid))
WHERE blocked.cardinality(pg_blocking_pids(blocked.pid)) > 0;
```

**Bước 4 — Autovacuum aggressive?**
```sql
SELECT relname, n_dead_tup, last_vacuum, last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 10;
```
Bảng write-heavy (tick_data) tích lũy nhiều dead tuples → autovacuum chạy mạnh → CPU cao.

**Nguyên nhân phổ biến nhất** trong hệ thống trading high-write: Seq Scan do thiếu index trên query mới được thêm, hoặc autovacuum không kịp với tốc độ insert.

---

### Q20. Tại sao vẫn dùng PostgreSQL thay vì ClickHouse khi có 50 triệu tick/ngày?

**Trả lời**: Đây là câu hỏi về việc chọn đúng công cụ cho đúng vai trò. PostgreSQL và ClickHouse tối ưu cho 2 workload khác nhau.

**PostgreSQL phù hợp vì đây là Operational Database (OLTP):**
- **ACID transactions**: Lệnh giao dịch (open/close/modify position) cần atomicity và isolation thực sự — không thể accept eventual consistency
- **Row-level locking**: `SELECT FOR UPDATE` cho xử lý lệnh concurrent
- **CDC (WAL)**: Debezium cần logical replication — ClickHouse không hỗ trợ
- **Mutable data**: Position có thể update nhiều lần trong vòng đời (open → modify SL/TP → close). ClickHouse tối ưu cho append-only, update/delete rất tốn kém
- **Low-latency writes**: 5,000 ticks/giây với COPY protocol — PostgreSQL xử lý tốt

**ClickHouse phù hợp hơn cho Analytics (OLAP):**
- Columnar storage → tốt cho `SELECT symbol, SUM(volume)` trên hàng tỷ rows
- Nhưng không có proper ACID, không có row-level lock, không có CDC mechanism

**Kiến trúc của dự án giải quyết cả 2:**
```
PostgreSQL (OLTP)          ClickHouse / Databricks (OLAP)
- Transaction safety    →  Kafka CDC  →  - Aggregate queries
- CDC source                            - Reporting
- Position management                   - ML features
```

Đây là pattern **CQRS** (Command Query Responsibility Segregation) ở level infrastructure — write path qua PostgreSQL, read/analytics path qua Databricks. Không cần chọn một, dùng đúng công cụ cho đúng vai trò.

---

## 12. Interview Q&A — Data Tuning & Performance Scaling

> Nhóm câu hỏi trọng tâm Middle+: "Làm sao hệ thống vẫn chạy được khi data tăng từ 10 triệu lên 10 tỷ records?"

---

### Q1. Tick_data tăng từ 50 triệu lên 500 triệu records/ngày. Điều gì sẽ bottleneck đầu tiên?

**Trả lời**: Bottleneck xuất hiện theo thứ tự sau — không phải cùng lúc:

```
1. Disk I/O         — write throughput đụng ceiling trước
2. Index Size       — index không còn fit vào shared_buffers / RAM
3. VACUUM pressure  — dead tuples tích lũy quá nhanh, autovacuum không theo kịp
4. Checkpoint       — dirty pages quá nhiều, checkpoint stall foreground writes
5. WAL volume       — disk I/O tăng, Debezium replication lag tăng
6. CPU              — query planning và sort/hash spill sau cùng mới thành bottleneck
```

**Phân tích cụ thể**:
- **INSERT throughput giảm**: 10x volume → index update 10x nhiều hơn. Nếu có 5 index trên tick_data, mỗi insert phải cập nhật 5 B-tree pages
- **Index không fit RAM**: Index `(symbol, tick_time)` trên 9 tỷ rows có thể đạt 50–100GB. Khi không fit `shared_buffers` → cache miss → random disk read mỗi index lookup
- **Partition scan nhiều hơn**: Query không filter đủ điều kiện partition key sẽ fan out sang nhiều partitions

**Follow-up: Làm sao biết bottleneck là CPU hay Disk?**
```sql
-- Disk I/O
SELECT * FROM pg_stat_io;  -- PostgreSQL 16+
-- Hoặc
SELECT * FROM pg_statio_user_tables WHERE relname = 'tick_data';

-- CPU + wait events
SELECT wait_event_type, wait_event, COUNT(*)
FROM pg_stat_activity
WHERE state = 'active'
GROUP BY wait_event_type, wait_event
ORDER BY count DESC;
```
`wait_event = 'DataFileRead'` → disk I/O bound. `wait_event IS NULL` với CPU cao → CPU bound.

---

### Q2. Tại sao query vẫn chậm dù đã có Index?

**Trả lời**: Đây là trường hợp Planner chủ động bỏ qua index — và Planner đúng.

**Kịch bản**: 70% rows trong `tick_data` có `symbol = 'EURUSD'`.
```sql
SELECT * FROM tick_data WHERE symbol = 'EURUSD';
```

Index `(symbol, tick_time)` tồn tại, nhưng PostgreSQL chọn `Seq Scan`. Tại sao?

**Lý do — selectivity thấp**: Index scan có 2 bước: (1) đọc index leaf pages → lấy row pointers, (2) fetch từng row từ heap (random I/O). Nếu 70% rows match, bước 2 tạo ra 70% × N random I/O — đắt hơn sequential scan toàn bảng.

Ngưỡng thực tế: PostgreSQL thường chọn Seq Scan khi predicate match >5–10% rows tùy data distribution và `random_page_cost`.

**Kiểm tra quyết định của Planner:**
```sql
-- Xem cost estimate
EXPLAIN (ANALYZE, COSTS)
SELECT * FROM tick_data WHERE symbol = 'EURUSD';

-- Ép dùng index (để so sánh)
SET enable_seqscan = off;
EXPLAIN ANALYZE SELECT * FROM tick_data WHERE symbol = 'EURUSD';
RESET enable_seqscan;
```

**Fix thực sự**: Không phải thêm index — mà rewrite query để filter selectivity cao hơn:
```sql
-- Kết hợp symbol + time range → selectivity tăng mạnh
WHERE symbol = 'EURUSD'
  AND tick_time >= NOW() - INTERVAL '1 hour'
-- Giờ chỉ ~0.04% rows → Index Scan có lợi
```

---

### Q3. Bạn đọc Execution Plan như thế nào?

**Trả lời**: Đọc từ **trong ra ngoài, từ dưới lên trên** — inner-most node thực thi trước.

```
Interviewer đưa plan:
  -> Sort (cost=95000..96200 rows=480000 width=64)
      -> Seq Scan on tick_data (cost=0..120000 rows=10000000 width=64)
            Filter: (symbol = 'EURUSD')
            Rows Removed by Filter: 7000000
```

**Cách đọc:**

| Field | Ý nghĩa |
|-------|---------|
| `cost=0..120000` | (startup cost)..(total cost) — đơn vị arbitrary, dùng để so sánh |
| `rows=10000000` | Planner estimate số rows |
| `actual rows=3000000` | Thực tế (chỉ có khi ANALYZE) |
| `Rows Removed by Filter: 7000000` | 7M rows bị scan rồi bỏ đi → thiếu index |

**Dấu hiệu nguy hiểm cần nhận ra ngay:**
- `Seq Scan` trên bảng > 1M rows → xem xét index
- `actual rows` >> `rows` (estimate lệch nhiều) → `ANALYZE` để cập nhật statistics
- `Sort Method: external merge Disk` → `work_mem` quá thấp, sort tràn ra disk
- `Buffers: shared read=500000` và `hit=1000` → cache miss rate cao, data không fit RAM

---

### Q4. Tại sao Composite Index không được sử dụng?

**Trả lời**: Vi phạm **Left-most Prefix Rule**.

```sql
CREATE INDEX idx1 ON tick_data (symbol, tick_time);

-- Query này KHÔNG dùng idx1
SELECT * FROM tick_data WHERE tick_time > NOW() - INTERVAL '1 day';
```

B-tree composite index được sort theo `symbol` trước, `tick_time` sau. Khi query không có filter trên `symbol` (cột đầu), database không biết tìm ở đâu trong index — phải scan toàn bộ index leaf pages, đắt tương đương Seq Scan.

**Analogy**: Index `(symbol, tick_time)` giống từ điển sắp xếp theo họ rồi mới đến tên. Tìm người họ "Nguyễn" rất nhanh. Nhưng tìm người tên "Minh" (không biết họ) → phải lật toàn bộ từ điển.

**Fix**: Tạo index riêng cho pattern này:
```sql
-- Index riêng cho time-only filter
CREATE INDEX idx_tick_time ON tick_data (tick_time DESC);
-- Hoặc kết hợp partition pruning — không cần index nếu partition đủ granular
```

---

### Q5. Query này có vấn đề gì?

```sql
SELECT * FROM tick_data WHERE DATE(tick_time) = '2026-06-01';
```

**Trả lời**: Function wrap trên cột index — **Non-SARGable predicate**.

`DATE(tick_time)` biến đổi từng giá trị `tick_time` thành `DATE` rồi mới so sánh. PostgreSQL không thể seek vào index `(tick_time)` vì index lưu giá trị gốc, không lưu `DATE(tick_time)`.

Kết quả: `Seq Scan` + `Filter: (date(tick_time) = '2026-06-01')` → scan toàn bảng.

**Rewrite SARGable:**
```sql
WHERE tick_time >= '2026-06-01 00:00:00+00'
  AND tick_time <  '2026-06-02 00:00:00+00'
```

Planner giờ có thể dùng `Index Range Scan` trực tiếp.

**Các anti-pattern tương tự thường gặp:**
```sql
-- Tất cả đều phá index
WHERE YEAR(tick_time) = 2026          -- dùng: tick_time >= '2026-01-01'
WHERE UPPER(symbol) = 'EURUSD'        -- normalize khi insert, lưu uppercase
WHERE volume * 1.1 > 1000             -- dùng: volume > 909.09
WHERE broker_id::text = '5'           -- dùng đúng type: broker_id = 5
```

---

### Q6. Khi nào Partitioning không giúp tăng tốc?

**Trả lời**: Partition chỉ có tác dụng khi query có **filter trên partition key** → Planner thực hiện partition pruning.

**Kịch bản**: Partition `tick_data` theo `tick_time` (theo tháng).
```sql
-- Query này KHÔNG benefit từ partition
SELECT SUM(volume) FROM tick_data WHERE symbol = 'EURUSD';
```
Không có filter trên `tick_time` → Planner phải đọc **tất cả partitions** → performance tương đương bảng không partition, thậm chí chậm hơn vì overhead metadata.

**Các trường hợp partition không giúp:**
| Tình huống | Lý do |
|-----------|-------|
| Query không filter partition key | Full partition scan |
| Partition quá nhỏ (>1000 partitions) | Planner overhead, planning time tăng |
| Data không đồng đều (skew) | 1 partition 90% data, 9 partition 10% còn lại |
| JOIN với bảng không partitioned | Partition pruning chỉ apply 1 phía |

**Giải pháp đúng**: Partition key phải align với access pattern phổ biến nhất. Trong dự án: partition theo `tick_time` vì 90% queries có time range filter.

---

### Q7. Partition theo Date hay Symbol?

**Trả lời**: **Date partition + Composite Index (symbol, tick_time)** — kết hợp cả hai.

| | Date Partition | Symbol Partition |
|--|---------------|-----------------|
| **Ưu điểm** | Archive dễ (drop partition cũ), query time range nhanh | Query theo symbol không cần index |
| **Nhược điểm** | Query `WHERE symbol=X` phải scan mọi date partitions nếu không có time filter | Skew nặng (EURUSD = 70% data), khó manage khi thêm symbol mới, không archive được theo thời gian |
| **Use case** | Time-series, audit logs, financial data | Lookup tables có cardinality thấp, ổn định |

**Quyết định trong dự án**: Date partition vì:
1. Deletion policy rõ ràng theo thời gian (archive data > 3 tháng)
2. Hầu hết queries đều có time range filter
3. Composite index `(symbol, tick_time)` bù đắp cho symbol-only queries

```sql
-- Kết hợp: partition prune theo date, index seek theo symbol
SELECT * FROM tick_data
WHERE symbol = 'EURUSD'                    -- index seek
  AND tick_time >= '2026-06-01'            -- partition prune
  AND tick_time <  '2026-06-08';
```

---

### Q8. Có 50 triệu insert/ngày. Tại sao không tạo 20 index?

**Trả lời**: Mỗi index là overhead write không thể tránh khỏi.

Với mỗi `INSERT` vào `tick_data`, PostgreSQL phải:
1. Insert row vào heap
2. Insert entry vào **mỗi index** trên bảng

20 index = 21 write operations per row. Với 5,000 ticks/giây:
- 1 index: 10,000 writes/giây (heap + 1 index)
- 20 index: 105,000 writes/giây

Ngoài ra: mỗi index chiếm thêm disk space + WAL volume. `VACUUM` phải clean dead entries trên mỗi index.

**Nguyên tắc thực tế**:
- Tạo index khi có query cụ thể cần nó — không tạo "phòng thủ"
- Audit định kỳ bằng `pg_stat_user_indexes`: drop index có `idx_scan = 0`
- Với bảng write-heavy: ưu tiên Partial Index (index ít rows hơn) và Covering Index (giảm số lượng index cần)

```sql
-- 1 covering index thay vì 3 index riêng lẻ
CREATE INDEX idx_tick_covering
    ON tick_data (symbol, tick_time DESC)
    INCLUDE (bid, ask, volume)
    WHERE tick_time >= NOW() - INTERVAL '30 days';
-- Partial: chỉ index 30 ngày gần nhất → nhỏ hơn 10x
```

---

### Q9. COPY nhanh hơn INSERT vì sao?

**Trả lời**: INSERT xử lý từng row riêng lẻ qua SQL pipeline đầy đủ:
```
INSERT INTO ... VALUES (...)
  → Parse SQL text
  → Plan query
  → Execute (1 row)
  → Update index (per row)
  → Commit / WAL flush
```

COPY là **binary bulk load protocol** — bỏ qua SQL parser, gửi data stream thẳng vào storage engine:
```
COPY tick_data FROM STDIN
  → Receive data stream
  → Validate types
  → Bulk load to heap
  → Batch index update
  → Single WAL flush for entire batch
```

**Nhanh hơn 10–50x** vì:
- Không parse SQL mỗi row
- Batch WAL writes thay vì per-row
- Index updates được gom batch
- Ít round-trips network hơn

**Trong dự án**: Buffer 1,000 ticks tại Python, flush bằng `copy_from` mỗi 100ms. Throughput tăng từ ~2,000 ticks/s (INSERT) lên ~50,000 ticks/s (COPY).

**Lưu ý**: COPY không có per-row error recovery. Validate dữ liệu tại Python (Pydantic) trước khi đưa vào COPY. Nếu 1 row lỗi → rollback toàn batch.

---

### Q10. VACUUM là gì? Tại sao PostgreSQL cần VACUUM?

**Trả lời**: PostgreSQL dùng **MVCC (Multi-Version Concurrency Control)** — khi UPDATE hoặc DELETE, PostgreSQL không sửa/xóa row cũ mà:
- `UPDATE`: tạo row mới với giá trị mới, đánh dấu row cũ là "dead"
- `DELETE`: đánh dấu row là "dead", không xóa vật lý ngay

Row "dead" không visible với transaction mới nhưng vẫn chiếm disk space → **Table Bloat** và **Index Bloat**.

**VACUUM** là tiến trình dọn dẹp:
1. Mark dead tuples là có thể tái sử dụng (không trả disk cho OS)
2. Cập nhật **Visibility Map** → cho phép Index Only Scan
3. Update **Free Space Map** → INSERT mới dùng lại space
4. Prevent **Transaction ID Wraparound** (critical — nếu không VACUUM, PostgreSQL sẽ stop accepting writes sau ~2 tỷ transactions)

**Với tick_data 50M rows/ngày và `synchronous_commit=off`**: Table bloat tích lũy nhanh. Cần monitor:
```sql
SELECT relname, n_dead_tup, n_live_tup,
       round(n_dead_tup::numeric / NULLIF(n_live_tup,0) * 100, 2) AS dead_ratio,
       last_autovacuum
FROM pg_stat_user_tables
WHERE relname = 'tick_data';
```
`dead_ratio > 20%` → xem xét tăng `autovacuum_vacuum_scale_factor` hoặc VACUUM thủ công.

---

### Q11. VACUUM và VACUUM FULL khác nhau?

**Trả lời**:

| | `VACUUM` | `VACUUM FULL` |
|--|---------|--------------|
| **Table lock** | Không lock (ShareUpdateExclusiveLock — cho phép reads + writes) | Exclusive lock — block mọi thứ |
| **Disk reclaim** | Không — mark space reusable nhưng không trả OS | Có — rewrite table, trả disk về OS |
| **Tốc độ** | Nhanh, incremental | Chậm, full rewrite |
| **WAL generated** | Ít | Nhiều (full rewrite) |
| **Khi nào dùng** | Routine maintenance — chạy thường xuyên | Chỉ khi table bloat nghiêm trọng và có maintenance window |

**Thực tế**: Autovacuum chạy `VACUUM` tự động. `VACUUM FULL` hiếm khi cần — chỉ dùng khi table bloat > 50% và cần thu hồi disk ngay.

**Thay thế tốt hơn VACUUM FULL**: `pg_repack` extension — rewrite table không cần exclusive lock, phù hợp production.

```sql
-- Kiểm tra cần VACUUM FULL không
SELECT relname,
       pg_size_pretty(pg_total_relation_size(oid)) AS total,
       pg_size_pretty(pg_relation_size(oid)) AS table_only,
       round((pg_total_relation_size(oid) - pg_relation_size(oid))::numeric
             / pg_total_relation_size(oid) * 100, 1) AS bloat_pct
FROM pg_class
WHERE relname = 'tick_data';
```

---

### Q12. WAL lớn quá thì sao?

**Trả lời**: WAL tích lũy khi replication consumer (Debezium) đọc không kịp tốc độ write.

**Hậu quả theo mức độ:**
1. **Disk tăng nhanh**: WAL segments không thể xóa vì replication slot giữ lại
2. **Replication lag tăng**: Debezium → Kafka → Databricks nhận data trễ hơn
3. **Disk đầy**: Nếu không monitor, disk đầy → PostgreSQL **dừng nhận writes** (không thể write WAL)
4. **Slot invalidation**: PostgreSQL 13+ có `max_slot_wal_keep_size` — nếu WAL lag vượt ngưỡng, slot bị invalidate → **mất CDC continuity**

**Monitor và alert:**
```sql
-- Kiểm tra lag per replication slot
SELECT slot_name,
       active,
       pg_size_pretty(
           pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)
       ) AS lag_size,
       confirmed_flush_lsn
FROM pg_replication_slots;
```

**Phòng ngừa trong dự án**:
- Alert khi `lag_size > 10GB`
- `max_slot_wal_keep_size = 50GB` trong `postgresql.conf`
- Separate replication slot per topic group (ticks / positions / signals) để dễ track

---

### Q13. Tại sao `synchronous_commit = off`?

**Trả lời**: Đây là trade-off có chủ đích — tăng throughput, chấp nhận mất tối đa vài ms data trong trường hợp crash.

**Cơ chế bình thường (`synchronous_commit = on`)**:
```
Transaction COMMIT
  → Ghi WAL vào disk (fsync)
  → Ack về client
```
`fsync` là blocking operation — throughput bị giới hạn bởi disk IOPS.

**Với `synchronous_commit = off`**:
```
Transaction COMMIT
  → Ghi WAL vào OS buffer
  → Ack về client ngay (không chờ fsync)
  → (Async) OS flush WAL xuống disk sau ~200ms
```

**Risk**: Nếu server crash trong 200ms window đó → mất tối đa 200ms data cuối cùng. Nhưng **không có data corruption** — WAL đảm bảo consistency khi restart.

**Tại sao acceptable cho tick_data?**
- Tick data là time-series market data — mất 200ms ticks trong sự kiện crash hiếm gặp là acceptable (có thể fill gap từ market data provider sau)
- Throughput tăng 2–5x — quan trọng hơn khi nhận 5,000 ticks/giây

**Không bao giờ dùng cho**: Bảng `positions`, `orders` — mất data tài chính là không thể chấp nhận. Chỉ apply per-table hoặc per-session:
```sql
-- Per-session (cho session tick ingestion)
SET synchronous_commit = off;
```

---

### Q14. Nếu query JOIN 2 bảng 100 triệu records thì làm gì?

**Trả lời**: Không JOIN trực tiếp 2 bảng lớn — filter trước, join sau.

```sql
-- Anti-pattern: JOIN full tables
SELECT t.*, p.open_price
FROM tick_data t
JOIN positions p ON t.symbol = p.symbol;
-- → Hash Join 100M × 100M → không thể chạy

-- Đúng: filter mạnh trước khi JOIN
SELECT t.bid, t.ask, p.open_price
FROM tick_data t
JOIN positions p ON t.symbol = p.symbol
                 AND p.status = 'OPEN'      -- filter positions: chỉ còn ~1%
WHERE t.tick_time >= NOW() - INTERVAL '5 minutes'  -- filter ticks: chỉ còn ~0.01%
  AND t.symbol = p.symbol;
```

**Checklist khi có slow JOIN:**
1. `EXPLAIN ANALYZE` — xem Join algorithm nào được chọn (Hash/Nested Loop/Merge)
2. Join key có index trên cả 2 bảng không?
3. Filter selectivity: đẩy `WHERE` điều kiện chọn lọc nhất vào sớm nhất
4. Partition pruning: nếu bảng partitioned, đảm bảo partition key nằm trong filter
5. Xem xét pre-aggregate trước JOIN thay vì JOIN raw data

---

### Q15. Hash Join vs Nested Loop — khi nào dùng cái nào?

**Trả lời**: Planner chọn tự động dựa trên cardinality estimate, nhưng hiểu cơ chế giúp debug.

**Nested Loop Join:**
```
For each row in outer table:
    Seek matching rows in inner table (via index)
```
- Tốt khi: outer table nhỏ (vài trăm rows) + inner table có index trên join key
- O(N × log M)
- Ví dụ: `positions (100 rows OPEN) JOIN tick_data (50M rows)` — Nested Loop hiệu quả nếu `tick_data.symbol` có index

**Hash Join:**
```
Build hash table from smaller table
Scan larger table, probe hash table
```
- Tốt khi: cả 2 bảng lớn, không có index hữu ích trên join key
- O(N + M) nhưng tốn RAM (hash table phải fit `work_mem`)
- Ví dụ: `tick_data (50M) JOIN daily_stats (100K)` — Hash Join build hash trên daily_stats (nhỏ hơn)

**Khi Hash Join spill ra disk** (`Batches: N > 1` trong EXPLAIN):
```sql
-- Tăng work_mem cho session
SET work_mem = '512MB';
EXPLAIN ANALYZE <query>;
```

**Merge Join**: ít gặp hơn — cả 2 bảng đã sorted trên join key, scan song song.

---

### Q16. Có 100 triệu rows. `ORDER BY tick_time DESC LIMIT 100` làm sao tối ưu?

**Trả lời**: Nếu có index match thứ tự sort, PostgreSQL dùng **Index Scan** và dừng ngay sau 100 rows — không cần sort toàn bộ table.

```sql
-- Index phù hợp
CREATE INDEX idx_tick_time_desc ON tick_data (tick_time DESC);
-- Hoặc kết hợp với symbol
CREATE INDEX idx_tick_symbol_time_desc ON tick_data (symbol, tick_time DESC);

-- Query dùng index → LIMIT pushdown
SELECT bid, ask, volume FROM tick_data
WHERE symbol = 'EURUSD'
ORDER BY tick_time DESC
LIMIT 100;
```

**EXPLAIN output tốt:**
```
Limit (rows=100)
  -> Index Scan Backward using idx_tick_symbol_time_desc
       Index Cond: (symbol = 'EURUSD')
```
Không có `Sort` node → PostgreSQL đọc 100 rows đầu từ index rồi dừng, không scan toàn bảng.

**EXPLAIN output xấu:**
```
Limit (rows=100)
  -> Sort (cost=... rows=50000000)
       -> Seq Scan on tick_data
```
`Sort` xuất hiện → đang sort 100M rows rồi lấy 100 → cực kỳ chậm. Cần index trên sort column.

---

### Q17. Tại sao `OFFSET` rất chậm với bảng lớn?

**Trả lời**: `OFFSET N` không phải "nhảy đến row N" — PostgreSQL phải **đọc và discard N rows đầu tiên**.

```sql
-- OFFSET 10,000,000 → đọc 10M rows, bỏ đi, trả 100 rows
SELECT * FROM tick_data ORDER BY tick_time DESC LIMIT 100 OFFSET 10000000;
```
Chi phí tăng tuyến tính theo OFFSET — page 100,000 chậm hơn page 1 đúng 100,000 lần.

**Giải pháp: Keyset Pagination**
```sql
-- Page 1
SELECT tick_time, symbol, bid, ask
FROM tick_data
ORDER BY tick_time DESC, tick_id DESC
LIMIT 100;
-- → Trả về ..., tick_time='2026-06-18 10:00:00', tick_id=9999900

-- Page 2: dùng cursor thay vì OFFSET
SELECT tick_time, symbol, bid, ask
FROM tick_data
WHERE (tick_time, tick_id) < ('2026-06-18 10:00:00', 9999900)
ORDER BY tick_time DESC, tick_id DESC
LIMIT 100;
```

**Tại sao nhanh hơn?** Với index trên `(tick_time DESC, tick_id DESC)` → seek trực tiếp đến cursor position → O(log N) thay vì O(N).

**Trade-off**: Không nhảy đến page tùy ý. Phù hợp cho "load more" / infinite scroll, không phù hợp cho "jump to page 500".

---

### Q18. Databricks có 1 triệu file nhỏ. Điều gì xảy ra?

**Trả lời**: **Small files problem** — metadata overhead vượt qua data overhead.

Spark phải thực hiện cho mỗi file:
1. List file từ object storage (S3/ADLS) — expensive API call
2. Open file handle
3. Read Parquet/Delta footer (metadata, statistics)
4. Parse row groups

Với 1M files, bước 1–3 có thể chiếm 80% job time dù data thực tế nhỏ. Spark driver bị OOM khi build file list quá lớn.

**Nguồn gốc trong dự án**: Spark Structured Streaming với trigger interval 30 giây → mỗi micro-batch tạo vài file nhỏ → sau 1 ngày = 2,880 batches × N files.

**Giải pháp:**
```python
# 1. Auto Compact (tự động merge files khi write)
spark.sql("""
    ALTER TABLE bronze.tick_data
    SET TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact'  = 'true'
    )
""")

# 2. Scheduled OPTIMIZE (gom file thủ công, chạy đêm)
spark.sql("OPTIMIZE bronze.tick_data WHERE date = current_date() - 1")

# 3. Tăng trigger interval (ít files hơn per ngày)
query = df.writeStream.trigger(processingTime='5 minutes')...
```

**Target**: Mỗi file ~128MB–1GB — số lượng files giảm từ 1M xuống còn vài nghìn.

---

### Q19. ZORDER khác Partition như thế nào?

**Trả lời**: Hai cơ chế tối ưu ở 2 level khác nhau.

**Partition — Physical directory separation:**
```
bronze/tick_data/
  broker=icmarkets/symbol=EURUSD/date=2026-06-01/
    file_001.parquet
  broker=icmarkets/symbol=EURUSD/date=2026-06-02/
    file_002.parquet
```
Partition pruning loại bỏ toàn bộ thư mục — không đọc file nào trong partition không match.

**Z-Order — Data co-location trong file:**
Trong một Delta file (128MB+), Z-Order sắp xếp lại rows theo multi-dimensional space-filling curve sao cho rows có `(symbol, tick_time)` gần nhau được lưu gần nhau trong file.

```python
OPTIMIZE silver.tick_data ZORDER BY (symbol, tick_time)
```

Khi query `WHERE symbol='EURUSD' AND tick_time >= '...'` → Delta data skipping đọc statistics từ file footer, skip file không có rows match → ít data scan hơn.

**Dùng khi nào:**
| | Partition | Z-Order |
|--|-----------|---------|
| **Cột cardinality** | Thấp (broker, symbol, date) | Cao (timestamp, price) |
| **Filter pattern** | Equality (`broker='ICM'`) | Range + equality kết hợp |
| **Số columns** | 2–4 | 2–4 (Z-Order > 4 cols hiệu quả giảm) |
| **Kết hợp** | ✓ Partition prune trước → Z-Order trong partition | ✓ |

---

### Q20. Nếu được thiết kế lại toàn bộ thì tối ưu gì nhất?

**Trả lời**:

Với volume hiện tại (~50M tick/ngày), kiến trúc hiện tại phù hợp. Nhưng nếu scale lên vài trăm triệu đến hàng tỷ ticks/ngày, tôi sẽ thay đổi theo thứ tự ưu tiên:

**1. Tách rõ OLTP và tick storage:**
Tick data là append-only time-series — không cần full ACID của PostgreSQL. Dùng **TimescaleDB** (extension của Postgres) hoặc chuyển tick ingestion thẳng vào Kafka → Databricks Bronze, PostgreSQL chỉ giữ `positions`, `orders`, `signals`.

**2. Schema Registry cho Kafka:**
Deploy từ đầu thay vì add-on sau. Quản lý schema evolution có kiểm soát, tránh breaking changes silently.

**3. Idempotent write tại Bronze:**
Thay vì dedup tại Silver (MERGE tốn kém), implement idempotent producer tại Kafka và upsert tại Bronze — giảm bớt một lớp MERGE overhead.

**4. Tách Bronze streaming và batch:**
Hiện tại cả streaming (Debezium) và batch (Airflow) đều write vào cùng Bronze table → có thể gây conflict và làm phức tạp schema evolution. Tách thành `bronze_streaming` và `bronze_batch`, merge tại Silver.

**5. ClickHouse cho tick analytics (nếu volume > 1 tỷ/ngày):**
ClickHouse columnar storage tối ưu cho time-series aggregation (OHLCV, spread analysis). Nhưng giữ PostgreSQL cho OLTP — không thay thế, bổ sung.

**Kiến trúc end-state:**
```
PostgreSQL     → Kafka →  Databricks (Bronze/Silver/Gold) → Reporting
(OLTP only)    CDC          Streaming + Batch merge

TimescaleDB    → Kafka →  ClickHouse
(tick storage)             (tick analytics)
```

Điều này cho thấy hiểu rõ ranh giới OLTP / Streaming / Analytics — đây là điểm phân biệt Middle và Senior.

---

## 13. PostgreSQL Deep Dive — Internals, Planner, Bloat, Pooling, Design

> 50 câu hỏi cho vòng phỏng vấn thiên **Database Performance / SQL Heavy**. Chia thành 10 nhóm chủ đề.

---

### PART A — PostgreSQL Memory Architecture

#### A1. `shared_buffers = 4GB` — tại sao chọn con số đó?

`shared_buffers` là **buffer cache của PostgreSQL** — pool RAM nơi PostgreSQL lưu data pages đọc từ disk. Khi query cần 1 page, PostgreSQL kiểm tra shared_buffers trước; nếu có (cache hit) → không cần disk I/O.

**Tại sao 4GB (= 25% RAM)?**
- Rule of thumb: `shared_buffers = 25% tổng RAM`. Server 16GB RAM → 4GB
- Tăng hơn 25% ít lợi thêm vì PostgreSQL còn nhờ vào OS page cache (double buffering)
- OS page cache tự quản lý phần RAM còn lại hiệu quả hơn

**Tại sao không phải 8GB hay 12GB?**
- PostgreSQL dùng shared memory segment — lớn quá tốn overhead management
- OS đã cache disk I/O rất tốt. Bộ nhớ còn lại để OS cache tốt hơn là nhét hết vào shared_buffers

```sql
-- Kiểm tra buffer hit rate (>99% là tốt)
SELECT sum(blks_hit) * 100.0 / (sum(blks_hit) + sum(blks_read)) AS cache_hit_ratio
FROM pg_stat_database;
```

---

#### A2. `effective_cache_size = 12GB` — dùng để làm gì?

`effective_cache_size` **không cấp phát RAM** — đây chỉ là **hint cho Query Planner** về tổng RAM cache khả dụng (shared_buffers + OS page cache).

Planner dùng giá trị này để tính **cost của Index Scan**:
- `effective_cache_size` lớn → Planner giả định data có khả năng cao đã nằm trong cache → random I/O rẻ hơn → ưu tiên Index Scan hơn
- `effective_cache_size` nhỏ → Planner cho rằng mọi I/O đều phải đọc disk → ưu tiên Seq Scan

**Công thức thực tế**:
```
effective_cache_size = shared_buffers + (RAM - shared_buffers) × 0.75
= 4GB + (16GB - 4GB) × 0.75
= 4GB + 9GB = 13GB ≈ 12GB
```

**Hậu quả nếu set sai**:
- Set quá thấp → Planner underestimate cache → chọn Seq Scan thay vì Index Scan → query chậm
- Set quá cao → Planner overestimate → chọn Index Scan khi data không fit cache → nhiều random I/O

---

#### A3. `work_mem = 64MB` — nếu có 10 query đồng thời thì RAM dùng bao nhiêu?

`work_mem` là RAM cấp phát **per sort/hash operation, per query**. Không phải per connection.

**Tính toán**:
- 1 query phức tạp có thể có nhiều Sort/Hash nodes (ví dụ: 3 nodes)
- 10 connections đồng thời × 3 nodes × 64MB = **1,920MB ~ 2GB** chỉ riêng work_mem

Công thức an toàn:
```
work_mem_total ≤ (RAM - shared_buffers) / max_connections / avg_nodes_per_query
= (16GB - 4GB) / 100 connections / 3 nodes
= 40MB → set work_mem = 32–64MB
```

**Khi nào tăng work_mem?**
- EXPLAIN ANALYZE thấy `Sort Method: external merge Disk` → sort tràn disk
- Session-level: `SET work_mem = '256MB'` cho query nặng cụ thể — không set global

```sql
-- Phát hiện sort/hash spill
SELECT query, sort_space_type, sort_space_used
FROM pg_stat_statements
JOIN ... -- check log files cho "temporary file" messages

-- Kiểm tra temp file usage
SELECT temp_files, temp_bytes
FROM pg_stat_database
WHERE datname = current_database();
```

---

#### A4. `wal_buffers` và `checkpoint_completion_target` ảnh hưởng gì?

**`wal_buffers = 16MB`** (default `-1` = auto ~1/32 shared_buffers):
- Buffer trong RAM cho WAL writes trước khi flush xuống disk
- Với write-heavy workload (5,000 ticks/s): set `wal_buffers = 64MB` để giảm WAL flush frequency

**`checkpoint_completion_target = 0.9`**:
- PostgreSQL cần flush dirty pages xuống disk tại mỗi checkpoint
- `0.9` → spread việc flush ra 90% của checkpoint interval, tránh I/O spike tại thời điểm checkpoint
- `0.5` (default) → flush nhanh hơn → I/O spike cao → foreground queries bị stall

```
checkpoint_timeout = 5min
checkpoint_completion_target = 0.9
→ PostgreSQL có 4.5 phút để flush dirty pages của 1 checkpoint
→ Smooth I/O thay vì burst
```

---

#### A5. Làm sao kiểm tra Buffer Cache hit ratio và cần quan tâm gì?

```sql
-- Database-level hit ratio
SELECT datname,
       blks_hit,
       blks_read,
       round(blks_hit * 100.0 / NULLIF(blks_hit + blks_read, 0), 2) AS hit_ratio
FROM pg_stat_database
WHERE datname = current_database();

-- Table-level (tìm bảng đang gây nhiều cache miss)
SELECT relname,
       heap_blks_hit,
       heap_blks_read,
       round(heap_blks_hit * 100.0 / NULLIF(heap_blks_hit + heap_blks_read, 0), 2) AS hit_ratio
FROM pg_statio_user_tables
ORDER BY heap_blks_read DESC
LIMIT 10;
```

**Ngưỡng**:
- `hit_ratio > 99%` → tốt, working set fit trong RAM
- `hit_ratio 95–99%` → có thể tăng shared_buffers hoặc archive data cũ
- `hit_ratio < 95%` → working set lớn hơn buffer pool → cần thêm RAM hoặc giảm working set (partition + archive)

---

### PART B — Statistics & Query Planner

#### B1. `ANALYZE` làm gì? Tại sao cần chạy sau khi import data lớn?

`ANALYZE` thu thập **column-level statistics** và lưu vào `pg_statistic`. Planner dùng statistics để estimate số rows mỗi query trả về → chọn execution plan phù hợp.

Statistics được thu thập:
- `most_common_vals` / `most_common_freqs`: giá trị phổ biến nhất và tần suất
- `histogram_bounds`: phân phối giá trị (equi-depth histogram)
- `n_distinct`: số giá trị unique ước tính
- `correlation`: mức độ physical order của cột so với logical order

```sql
-- Chạy ANALYZE sau bulk import
ANALYZE tick_data;

-- Hoặc chi tiết hơn
ANALYZE VERBOSE tick_data;

-- Xem statistics hiện tại
SELECT * FROM pg_stats
WHERE tablename = 'tick_data'
  AND attname = 'symbol';
```

Autovacuum chạy `ANALYZE` tự động khi bảng thay đổi > ngưỡng (`autovacuum_analyze_scale_factor = 0.2` = 20% rows changed). Nhưng sau bulk import hàng triệu rows, nên chạy thủ công ngay.

---

#### B2. Statistics bị stale — Planner chọn sai plan thế nào?

**Kịch bản**: 6 tháng trước, `EURUSD` chiếm 5% rows → Planner biết, ưu tiên Index Scan.

Sau 6 tháng, `EURUSD` tăng lên 70% do một broker chỉ trade cặp này. Statistics chưa được cập nhật → Planner vẫn nghĩ `EURUSD = 5%` → estimate rows = 250,000 thay vì 3,500,000 → chọn `Index Scan` → phải fetch 3.5M rows từ heap via index → random I/O cực kỳ chậm (nhiều hơn Seq Scan).

```sql
-- Phát hiện lệch: estimate vs actual rows
EXPLAIN ANALYZE
SELECT * FROM tick_data WHERE symbol = 'EURUSD';

-- Output tệ:
-- Seq Scan (hoặc Index Scan)
-- (estimated rows=250000) (actual rows=3500000)
-- → Lệch 14x → statistics stale

-- Fix
ANALYZE tick_data;
-- Sau đó kiểm tra lại plan
```

**Tăng statistics target cho cột có cardinality cao**:
```sql
-- Default statistics target = 100 (số buckets histogram)
-- Tăng lên 500 cho cột symbol để Planner có thêm thông tin
ALTER TABLE tick_data ALTER COLUMN symbol SET STATISTICS 500;
ANALYZE tick_data;
```

---

#### B3. Planner cost model — `seq_page_cost` và `random_page_cost`

Planner tính cost dựa trên:
- `seq_page_cost = 1.0` (baseline): chi phí đọc 1 page theo sequential order
- `random_page_cost = 4.0` (default): đọc random page tốn gấp 4 lần sequential

**Ý nghĩa thực tế**:
- Trên HDD: random I/O thực sự chậm hơn 4–10x → `random_page_cost = 4.0` đúng
- Trên SSD: gap chỉ còn ~1.1–1.5x → set `random_page_cost = 1.1` để Planner ưu tiên Index Scan hơn

```sql
-- Cho SSD storage
ALTER SYSTEM SET random_page_cost = 1.1;
SELECT pg_reload_conf();
```

**Tác động**: Với `random_page_cost` cao, Planner cần index selectivity rất cao mới chọn Index Scan. Giảm `random_page_cost` → Planner chọn Index Scan sớm hơn → tốt cho SSD.

---

#### B4. Khi nào dùng `pg_hint_plan` hoặc `SET enable_seqscan = off`?

**Không nên dùng thường xuyên** — đây là workaround, không phải fix thật sự.

`SET enable_seqscan = off`: tắt Seq Scan để ép Planner dùng index, dùng để **debug** xem query nếu dùng index thì chạy nhanh hơn không. Không dùng trong production.

**Trường hợp hợp lệ duy nhất**: Planner chọn sai plan do statistics không kịp update (ví dụ: production emergency). Dùng `pg_hint_plan` để fix tạm, đồng thời fix gốc rễ (chạy ANALYZE, tăng statistics target, điều chỉnh cost parameters).

```sql
-- Debug: ép index để so sánh
SET enable_seqscan = off;
EXPLAIN ANALYZE SELECT * FROM tick_data WHERE symbol = 'EURUSD';
RESET enable_seqscan;

-- Production hint (cần extension pg_hint_plan)
SELECT /*+ IndexScan(tick_data idx_tick_symbol_time) */
       * FROM tick_data WHERE symbol = 'EURUSD';
```

---

### PART C — Join Algorithms Deep Dive

#### C1. Hash Join spill to disk — khi nào và hậu quả gì?

Hash Join build phase: PostgreSQL đọc inner table, tạo hash table trong RAM (`work_mem`). Nếu hash table lớn hơn `work_mem` → **spill ra temp files trên disk**.

```
EXPLAIN ANALYZE output khi spill:
Hash  (cost=... rows=...)
  Batches: 8   (← >1 = có spill, 8 = 8 passes qua disk)
  Memory Usage: 64kB   (← chỉ chunk nhỏ fit RAM)
```

**Hậu quả**: Mỗi batch cần đọc/ghi temp file → throughput giảm 10–100x. `Batches: 8` nghĩa là data phải xử lý 8 lần thay vì 1.

**Fix**:
```sql
-- Option 1: Tăng work_mem session-level cho query nặng
SET work_mem = '512MB';

-- Option 2: Rewrite query — filter trước khi join để reduce inner table size
-- Thay vì join full tables, join sau khi đã filter
SELECT t.*, p.open_price
FROM (SELECT * FROM tick_data WHERE tick_time >= NOW() - INTERVAL '1 hour') t
JOIN (SELECT * FROM positions WHERE status = 'OPEN') p
    ON t.symbol = p.symbol;

-- Option 3: Nếu inner table nhỏ → Nested Loop + index
```

---

#### C2. Merge Join — khi nào tốt hơn Hash Join?

Merge Join yêu cầu cả 2 input **đã được sort** trên join key. Sau đó merge song song như merge sort.

```
MergeJoin
  ← Index Scan on tick_data (symbol) — đã sorted
  ← Index Scan on positions (symbol) — đã sorted
```

**Tốt hơn Hash Join khi**:
- Cả 2 bảng có index trên join key → đã sorted miễn phí
- Memory bị giới hạn (Hash Join cần RAM cho hash table, Merge Join không cần)
- Output cần sorted theo join key (tránh Sort node thêm)

**Kém hơn Hash Join khi**:
- Data chưa sorted → cần Sort nodes thêm → tốn RAM và CPU
- Join key có nhiều duplicates → Merge Join phải expand cartesian product

```sql
-- Kiểm tra Merge Join đang được dùng
EXPLAIN SELECT t.bid, p.volume
FROM tick_data t
JOIN positions p ON t.symbol = p.symbol
WHERE t.tick_time >= NOW() - INTERVAL '1 hour';
-- Nếu cả 2 có Index Scan trên symbol → Planner có thể chọn Merge Join
```

---

#### C3. Tại sao Planner chọn Nested Loop thay vì Hash Join?

Nested Loop tốt khi **outer table nhỏ** và **inner table có index** trên join key:

```
For each row in outer (small table):
    Index Seek on inner table → O(log N)
Total: outer_rows × log(inner_rows) vs Hash Join: O(N + M)
```

Planner chọn Nested Loop khi:
1. Outer table sau filter có ít rows (< vài nghìn)
2. Inner table có index phù hợp trên join key
3. `random_page_cost` thấp (SSD) → index lookup rẻ

**Vấn đề — Nested Loop ẩn N+1**:
```sql
-- Planner estimate outer = 100 rows → chọn Nested Loop
-- Thực tế outer = 100,000 rows → 100,000 index seeks → cực chậm
-- Phát hiện qua:
EXPLAIN ANALYZE ...
-- Tìm: "loops=100000" trong Nested Loop node
-- actual time >> estimated time
```

Fix: Chạy `ANALYZE` để update estimate. Hoặc set `enable_nestloop = off` để debug.

---

### PART D — Table Bloat & Index Bloat

#### D1. Làm sao đo Table Bloat và Index Bloat?

**Table Bloat**: % không gian trong table bị dead tuples chiếm.
```sql
-- Cách đơn giản: so sánh n_dead_tup với n_live_tup
SELECT relname,
       n_live_tup,
       n_dead_tup,
       round(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS bloat_pct,
       last_autovacuum,
       last_autoanalyze
FROM pg_stat_user_tables
WHERE relname IN ('tick_data', 'positions', 'orders')
ORDER BY n_dead_tup DESC;

-- Cách chính xác hơn: dùng pgstattuple extension
CREATE EXTENSION IF NOT EXISTS pgstattuple;
SELECT * FROM pgstattuple('tick_data');
-- → dead_tuple_percent: % physical space bị bloat
```

**Index Bloat**:
```sql
-- Dùng pgstattuple cho index
SELECT * FROM pgstatindex('idx_tick_symbol_time');
-- → avg_leaf_density: nên > 70%, nếu < 50% → index bloat nặng
-- → leaf_fragmentation: % pages bị fragmented
```

**Dấu hiệu cần action**:
- Table bloat > 20% → tăng autovacuum frequency
- Index `avg_leaf_density` < 50% → REINDEX
- `pg_total_relation_size` tăng mà rowcount không tăng → bloat

---

#### D2. `REINDEX` dùng khi nào? REINDEX CONCURRENTLY?

**REINDEX** rebuild index từ đầu — xóa bỏ fragmentation và wasted space.

Dùng khi:
- Index bị corrupt (hiếm nhưng xảy ra sau crash)
- `avg_leaf_density` < 50% — index quá fragmented, query chậm bất thường
- Sau khi xóa lượng lớn rows, index size không giảm

```sql
-- Blocking (lock toàn bộ table, không dùng production)
REINDEX TABLE tick_data;
REINDEX INDEX idx_tick_symbol_time;

-- Non-blocking (PostgreSQL 12+) — dùng production
REINDEX TABLE CONCURRENTLY tick_data;
-- Tạo index mới song song với traffic, swap khi xong
```

**REINDEX vs DROP + CREATE INDEX CONCURRENTLY**:
- `REINDEX CONCURRENTLY`: đơn giản hơn, 1 lệnh
- `DROP + CREATE`: kiểm soát được storage parameter và fillfactor

**`fillfactor` để giảm fragmentation**:
```sql
-- Giảm fill factor cho bảng có UPDATE nhiều → để trống 20% mỗi page
-- → UPDATE có thể update tại chỗ (HOT update) thay vì tạo dead tuple
CREATE INDEX idx_tick_symbol_time ON tick_data (symbol, tick_time)
    WITH (fillfactor = 80);
```

---

#### D3. Index Fragmentation trong PostgreSQL

Khác với SQL Server, PostgreSQL không có "fill factor per page" per-insert. Fragmentation xảy ra do:

1. **DELETE** để lại empty slots trong index leaf pages
2. **INSERT** vào các page đã đầy → page split → nửa page bị empty → `avg_leaf_density` giảm
3. **UPDATE** (không HOT) tạo dead index entry + new entry → index bloat

**Phát hiện và đo**:
```sql
SELECT * FROM pgstatindex('idx_tick_symbol_time');
-- leaf_fragmentation: % leaf pages có wasted space > 20%
-- avg_leaf_density: trung bình % space dùng trong leaf pages
```

**Phòng ngừa tốt hơn fix**:
- Tick data là append-only (không UPDATE/DELETE) → fragmentation thấp tự nhiên
- Positions/Orders có UPDATE nhiều → set `fillfactor = 70–80` trên index

---

### PART E — Connection Pooling

#### E1. PostgreSQL chịu được bao nhiêu connection? Tại sao không nên tăng `max_connections = 5000`?

Mỗi PostgreSQL connection là 1 **OS process** (không phải thread) tốn:
- ~5–10MB RAM per idle connection (stack, shared memory mapping)
- Context switch overhead khi nhiều processes
- Semaphore/lock contention khi > 200–300 connections

```
max_connections = 5000
→ 5000 × 10MB = 50GB RAM chỉ riêng connection overhead
→ Planner không đủ shared memory → query chậm
→ Lock contention cực kỳ cao
```

**Ngưỡng thực tế**:
- `max_connections = 100–200` cho application connections
- Connection pool (pgBouncer/PgPool) đứng trước, multiplexes nhiều app connections → vài PostgreSQL connections

```sql
-- Kiểm tra connections đang dùng
SELECT state, count(*)
FROM pg_stat_activity
GROUP BY state;

-- state = 'idle' nhiều → lãng phí, nên dùng connection pool
```

---

#### E2. pgBouncer — 3 chế độ hoạt động và khi nào dùng cái nào?

| Mode | Cơ chế | Use case |
|------|--------|---------|
| **Session** | 1 client → giữ 1 server connection suốt session | Apps dùng session-level state (`SET`, `PREPARE`, temp tables) |
| **Transaction** | 1 client → server connection chỉ trong 1 transaction | Hầu hết web apps — connection released ngay sau COMMIT/ROLLBACK |
| **Statement** | 1 client → server connection chỉ trong 1 statement | Hiếm dùng — không hỗ trợ multi-statement transactions |

**Transaction mode** là lựa chọn mặc định tốt nhất cho Python server:
```
App: 1000 concurrent "connections" tới pgBouncer
pgBouncer: 20 real PostgreSQL connections
→ 50x reduction, không cần thay đổi app code
```

**Caveat**: Transaction mode không hỗ trợ:
- `SET` per-session (cần `SET LOCAL` trong transaction)
- Advisory locks
- `LISTEN/NOTIFY`
- Prepared statements (cần `server_reset_query`)

---

#### E3. asyncpg Pool trong Python — cấu hình đúng?

```python
import asyncpg
import asyncio

# Khởi tạo pool một lần khi startup
async def create_pool() -> asyncpg.Pool:
    return await asyncpg.create_pool(
        dsn="postgresql://user:pass@localhost/forex",
        min_size=5,           # min connections luôn sẵn
        max_size=20,          # max connections per instance
        max_queries=50_000,   # recycle connection sau 50k queries
        max_inactive_connection_lifetime=300,  # close idle conn sau 5 phút
        command_timeout=30,   # timeout per query
    )

# Usage
async def insert_ticks(pool: asyncpg.Pool, ticks: list[dict]):
    async with pool.acquire() as conn:
        await conn.copy_records_to_table(
            'tick_data',
            records=[(t['broker'], t['symbol'], t['bid'],
                      t['ask'], t['volume'], t['tick_time']) for t in ticks],
            columns=['broker', 'symbol', 'bid', 'ask', 'volume', 'tick_time']
        )
```

**Sizing per-broker instance**:
- 1 broker instance: `max_size = 10–20` connections đủ
- Tổng: 3 broker instances × 20 = 60 connections → PostgreSQL `max_connections = 100` an toàn

---

#### E4. Connection pool sizing formula

```
pool_size = (core_count × 2) + effective_spindle_count

Ví dụ:
- Server 4 core, SSD (1 spindle)
- pool_size = (4 × 2) + 1 = 9 ≈ 10 connections

Rule: nhiều hơn 10-20 connections hiếm khi giúp ích cho PostgreSQL
vì CPU bound queries sẽ queue anyway, I/O bound queries cũng vậy
```

Nguồn: **HikariCP "About Pool Sizing"** — empirically validated.

---

### PART F — Caching Strategy

#### F1. Multi-layer cache — nên cache ở đâu?

```
Request
  ↓
[L1] Application Memory (Python dict/LRU)  ← 0ms, limited size
  ↓ miss
[L2] Redis                                  ← <1ms, shared across instances
  ↓ miss
[L3] Materialized View (PostgreSQL)         ← 1–5ms, pre-aggregated
  ↓ miss
[L4] PostgreSQL query (with index)          ← 5–50ms
  ↓ miss
[L5] Databricks Gold (analytics)            ← seconds, batch data
```

**Trong dự án**:
- **Current tick price** (EURUSD latest bid/ask): L1 + L2 Redis — cập nhật mỗi tick, TTL 5 phút
- **Symbol metadata** (pip size, contract size): L1 Python dict — static, load once at startup
- **OHLCV 1m last 24h**: L3 Materialized View + Redis — refresh mỗi phút
- **Account balance**: L2 Redis — update sau mỗi trade, TTL 30 giây
- **Historical analysis**: L5 Databricks Gold — batch query

---

#### F2. Cache invalidation — chiến lược cho từng loại data?

**TTL-based (đơn giản, phù hợp tick data)**:
```python
# Redis set với TTL
await redis.setex(f"price:{symbol}", 30, json.dumps(price_data))
# Sau 30s tự expire, client miss → refetch từ PostgreSQL
```

**Write-through (strong consistency)**:
```python
# Update PostgreSQL và Redis trong cùng 1 operation
async def update_account_balance(conn, redis, account_id, new_balance):
    async with conn.transaction():
        await conn.execute(
            "UPDATE accounts SET balance=$1 WHERE id=$2",
            new_balance, account_id
        )
        await redis.setex(f"account:{account_id}:balance",
                          60, str(new_balance))
```

**Event-driven invalidation (Debezium)**:
```python
# Debezium CDC event → Python consumer → invalidate Redis key
async def on_position_update(event: dict):
    position_id = event['after']['position_id']
    await redis.delete(f"position:{position_id}")
    # Next read sẽ miss → fetch fresh từ PostgreSQL
```

**Materialized View refresh**:
```sql
-- Concurrent refresh (không block reads)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ohlcv_1m;
-- Chạy mỗi phút qua pg_cron hoặc Airflow
```

---

#### F3. Làm sao đo cache effectiveness?

```python
# Track hit/miss ratio trong app
class CacheMetrics:
    hits = 0
    misses = 0

    @property
    def hit_ratio(self):
        total = self.hits + self.misses
        return self.hits / total if total else 0
```

```sql
-- Redis INFO stats
-- keyspace_hits / (keyspace_hits + keyspace_misses)

-- PostgreSQL buffer hit
SELECT sum(blks_hit) * 100.0 / (sum(blks_hit) + sum(blks_read))
FROM pg_stat_database;
```

---

### PART G — Database Design

#### G1. `BIGSERIAL` hay `UUID` cho primary key?

| | `BIGSERIAL` | `UUID (v4)` |
|--|------------|------------|
| **Size** | 8 bytes | 16 bytes |
| **Index size** | Nhỏ hơn | 2x lớn hơn |
| **INSERT performance** | Tốt — sequential, append-only B-tree | Kém — random UUID gây page splits, index fragmentation |
| **Readability** | `12345` | `550e8400-e29b-41d4-...` |
| **Merge từ nhiều nguồn** | Collision risk cao | Globally unique, safe |
| **Expose internal ID** | Có thể enumerate | Không thể đoán |

**Quyết định trong dự án**:
- `tick_data`, `orders`: dùng `BIGSERIAL` — append-only, không merge từ nhiều source, performance quan trọng
- `positions`: dùng `UUID` — có thể generate tại EA/Python trước khi ghi, cần globally unique để trace across systems
- Nếu cần UUID nhưng muốn performance: `UUID v7` (time-ordered) — random trong 1ms window → ít page splits hơn v4

```sql
CREATE TABLE tick_data (
    tick_id   BIGSERIAL PRIMARY KEY,  -- auto-increment, append-friendly
    ...
);

CREATE TABLE positions (
    position_id  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    ...
);
```

---

#### G2. Normalization — đến mức nào là đủ?

**1NF → 2NF → 3NF** là chuẩn cho OLTP. Nhưng không phải lúc nào cũng normalize hết.

**Schema hiện tại**:
```sql
tick_data (broker, symbol, bid, ask, volume, tick_time)
```
- `broker` và `symbol` là foreign key candidates, nhưng không normalize thành bảng riêng.
- **Lý do hợp lý**: tick_data là append-only time-series, JOIN với bảng brokers/symbols mỗi query tạo overhead không cần thiết. Denormalize có chủ đích → read performance tốt hơn.

**Khi nào normalize?**
- `positions` table: normalize `broker_id`, `symbol_id` → tránh update anomaly (nếu broker đổi tên)
- `orders` table: normalize → referential integrity với `positions`

**Khi nào denormalize?**
- Read-heavy tables với aggregation thường xuyên
- Time-series data không bao giờ update
- Reporting tables (Gold layer) — đây là use case điển hình

```sql
-- Normalized (OLTP)
positions (position_id, broker_id FK, symbol_id FK, ...)
brokers   (broker_id, broker_name, ...)
symbols   (symbol_id, symbol_name, pip_value, ...)

-- Denormalized (OLAP / tick_data)
tick_data (broker VARCHAR, symbol VARCHAR, ...) -- embed string trực tiếp
-- Lý do: JOIN broker và symbol table 50M lần/ngày không worth it
```

---

#### G3. Khi nào dùng denormalization có chủ đích?

```sql
-- Normalized positions (3NF) — cập nhật đúng, đọc chậm hơn
SELECT p.*, b.broker_name, s.pip_value
FROM positions p
JOIN brokers b ON p.broker_id = b.id
JOIN symbols s ON p.symbol_id = s.id
WHERE p.status = 'OPEN';

-- Denormalized reporting snapshot — pre-computed, đọc nhanh
CREATE TABLE position_snapshots AS
SELECT p.position_id, b.broker_name, s.symbol_name, s.pip_value,
       p.open_price, p.volume, p.status, p.open_time
FROM positions p
JOIN brokers b ON p.broker_id = b.id
JOIN symbols s ON p.symbol_id = s.id;
-- Refresh theo scheduled job, không join runtime
```

**Rule**: Normalize tại OLTP (đúng, consistent), denormalize tại OLAP/reporting layer (fast, pre-computed).

---

### PART H — Capacity Planning

#### H1. 50M rows/ngày, 1 row = 100 bytes — 1 năm tốn bao nhiêu disk?

```
Daily storage:
  50,000,000 rows × 100 bytes = 5,000,000,000 bytes = ~5GB raw data

Overhead factors:
  × 1.2 (page headers, alignment padding)     = 6GB
  × 1.3 (TOAST, null bitmaps, tuple headers) = 7.8GB

Yearly data:
  7.8GB/day × 365 = ~2.85TB/năm

Indexes (2 indexes, each ~30% data size):
  7.8GB × 2 × 0.30 = ~4.7GB/day index
  = ~1.7TB/năm indexes

WAL (assuming 2× data churn):
  7.8GB × 2 = ~15.6GB/day WAL
  (WAL recycled sau checkpoint, không tích lũy nếu không có replication lag)

Total disk per year:
  ~2.85TB (data) + ~1.7TB (indexes) = ~4.5TB

Planning buffer (2× for safety, VACUUM bloat, temp files):
  ~10TB SSD per year
```

---

#### H2. Index size estimation

```sql
-- Kích thước index thực tế
SELECT indexname,
       pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE relname = 'tick_data'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Ước tính trước khi tạo:
-- B-tree leaf entry = key columns size + 8 bytes (heap pointer)
-- (symbol VARCHAR(20) avg 8 bytes) + (tick_time 8 bytes) + 8 bytes overhead = 24 bytes/entry
-- 50M rows × 24 bytes = 1.2GB/ngày cho 1 index
-- × 365 = ~440GB/năm cho 1 index
```

---

#### H3. Tính số partitions cần cho 3 năm data — và partition nào nên drop khi nào?

```
3 năm × 12 tháng = 36 monthly partitions

Partition size per month:
  2.85TB/năm ÷ 12 = ~240GB/partition (data + index)

Tổng: 36 × 240GB = ~8.6TB

Retention policy:
  - Hot (0–3 tháng): SSD, fully indexed
  - Warm (3–12 tháng): SSD, partial index (drop some indexes)
  - Cold (1–3 năm): HDD tablespace hoặc archive sang Databricks Bronze
  - Archive (>3 năm): S3/Azure Blob, query qua Databricks only
```

```sql
-- Kiểm tra partition sizes
SELECT child.relname,
       pg_size_pretty(pg_relation_size(child.oid)) AS size
FROM pg_inherits
JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
JOIN pg_class child  ON pg_inherits.inhrelid  = child.oid
WHERE parent.relname = 'tick_data'
ORDER BY child.relname;

-- Drop partition cũ (instantaneous — không scan data)
DROP TABLE tick_data_2023_01;
```

---

### PART I — Hot Partition Problem

#### I1. Hot Partition là gì? Tại sao xảy ra?

**Hot Partition**: Tất cả writes tập trung vào 1 partition tại một thời điểm.

Với date-range partitioning: **mọi INSERT hôm nay đều vào partition `tick_data_2026_06`**. Partition đó:
- Chịu 100% write load
- Autovacuum chạy liên tục trên đó
- Buffer contention cao cho partition đó
- Các partitions cũ hoàn toàn idle

Với date-partitioned time-series data, đây là **expected và acceptable** — đặc trưng của time-series append workload.

**Khi nào hot partition thực sự thành vấn đề?**
- Bảng không phải time-series (ví dụ: user_events partitioned by user_id range → users mới đổ vào cuối range)
- Cần horizontal scaling (sharding) thật sự

---

#### I2. Giải pháp cho hot partition tùy use case

**1. Sub-partitioning** (vừa archive theo date, vừa distribute write):
```sql
-- Partition theo date, sub-partition theo broker (hash)
CREATE TABLE tick_data_2026_06
    PARTITION OF tick_data
    FOR VALUES FROM ('2026-06-01') TO ('2026-07-01')
    PARTITION BY HASH (broker);

CREATE TABLE tick_data_2026_06_broker_0
    PARTITION OF tick_data_2026_06
    FOR VALUES WITH (MODULUS 3, REMAINDER 0);
-- → 3 broker hash sub-partitions → writes distributed
```

**2. Hash Partitioning** (cho non-time-series):
```sql
-- Phân phối đều theo hash(symbol) — không archive được theo time
-- Chỉ dùng khi access pattern không có time dimension
CREATE TABLE tick_data PARTITION BY HASH (symbol);
CREATE TABLE tick_data_0 PARTITION OF tick_data FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE tick_data_1 PARTITION OF tick_data FOR VALUES WITH (MODULUS 4, REMAINDER 1);
-- ...
```

**3. Sharding** (khi 1 PostgreSQL instance không đủ):
- Mỗi broker instance ghi vào PostgreSQL riêng (đã thực hiện trong ADR-001)
- Databricks là convergence layer — không cần join tại PostgreSQL level

**Kết luận cho dự án**: Hot partition với date partitioning là **acceptable và expected** — per-broker isolation (ADR-001) đã distribute write load across 3 PostgreSQL instances. Không cần sub-partition thêm ở volume hiện tại.

---

### PART J — Full Debug Workflow (The Boss Question)

#### J1. Tick_data có 10 tỷ records. Query `WHERE symbol='EURUSD' AND tick_time BETWEEN ...` chạy 15 giây. Debug từ đầu đến cuối.

**Quy trình 10 bước — không bỏ bước nào:**

**Bước 1 — Capture execution plan đầy đủ:**
```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT TEXT)
SELECT * FROM tick_data
WHERE symbol = 'EURUSD'
  AND tick_time BETWEEN '2026-06-01' AND '2026-06-07';
```
In ra file, đọc từ **inner node → outer node**. Ghi lại: node có `actual time` cao nhất là suspect.

**Bước 2 — Kiểm tra Partition Pruning:**
```sql
-- EXPLAIN phải thấy:
-- "Partitions selected: 1 out of 36" → pruning hoạt động
-- Nếu "Partitions selected: 36 out of 36" → không prune → kiểm tra WHERE clause

-- Bug phổ biến: timezone mismatch
-- tick_time TIMESTAMPTZ, literal không có timezone → implicit cast → disable pruning
-- Fix:
AND tick_time BETWEEN '2026-06-01 00:00:00+00' AND '2026-06-07 23:59:59+00'
```

**Bước 3 — Kiểm tra Statistics accuracy:**
```sql
-- So sánh estimate vs actual rows trong EXPLAIN output
-- (estimated rows=50000) vs (actual rows=3500000) → lệch 70x → statistics stale

SELECT n_distinct, most_common_vals, most_common_freqs
FROM pg_stats
WHERE tablename = 'tick_data' AND attname = 'symbol';

-- Fix:
ANALYZE tick_data;
-- Nếu vẫn lệch → tăng statistics target:
ALTER TABLE tick_data ALTER COLUMN symbol SET STATISTICS 500;
ANALYZE tick_data;
```

**Bước 4 — Xác nhận Seq Scan hay Index Scan:**
- `Seq Scan` trên partition sau bước 2: thiếu index hoặc selectivity thấp
- `Index Scan` nhưng vẫn chậm: index có thể không fit RAM (xem bước 8)

```sql
-- Kiểm tra index tồn tại trên partition hiện tại
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename LIKE 'tick_data_2026_06%';
-- Lỗi phổ biến: tạo index trên parent table nhưng partition mới không inherit
```

**Bước 5 — Kiểm tra Buffers (cache hit):**
```
Từ EXPLAIN output:
Buffers: shared hit=1000 read=500000
→ 500,000 disk reads → index không fit RAM hoặc cold start
→ hit ratio = 1000/(1000+500000) = 0.2% → rất tệ

Buffers: shared hit=498000 read=2000
→ 99.6% cache hit → data đang trong RAM → bottleneck không phải I/O
```

**Bước 6 — Kiểm tra Index Selectivity:**
```sql
-- EURUSD chiếm bao nhiêu % trong time range đang query?
SELECT symbol, count(*) * 100.0 / sum(count(*)) OVER () AS pct
FROM tick_data
WHERE tick_time BETWEEN '2026-06-01' AND '2026-06-07'
GROUP BY symbol;

-- Nếu EURUSD = 60% → Planner đúng khi chọn Seq Scan
-- Index không giúp ích, cần giải pháp khác (MV, aggregate table)
```

**Bước 7 — Kiểm tra Table & Index Bloat:**
```sql
SELECT n_dead_tup,
       round(n_dead_tup * 100.0 / NULLIF(n_live_tup,0), 2) AS dead_ratio
FROM pg_stat_user_tables
WHERE relname LIKE 'tick_data%';

-- dead_ratio > 20% trên partition → VACUUM
VACUUM ANALYZE tick_data_2026_06;

SELECT * FROM pgstatindex('idx_tick_2026_06_symbol_time');
-- avg_leaf_density < 60% → REINDEX CONCURRENTLY
```

**Bước 8 — Kiểm tra work_mem (Sort/Hash spill):**
```sql
-- Tìm trong EXPLAIN:
-- "Sort Method: external merge Disk" → tăng work_mem
-- "Hash  Batches: 8" → Hash Join spill

-- Thử tăng work_mem session-level
SET work_mem = '512MB';
EXPLAIN ANALYZE <query>;
-- Nếu nhanh hơn đáng kể → đây là bottleneck
```

**Bước 9 — Kiểm tra Cache Hit Ratio toàn database:**
```sql
SELECT sum(blks_hit) * 100.0 / (sum(blks_hit) + sum(blks_read)) AS global_hit_ratio,
       sum(blks_read) AS total_disk_reads
FROM pg_stat_database
WHERE datname = current_database();

-- < 95% → shared_buffers quá nhỏ hoặc working set quá lớn
-- Solution: archive data cũ sang Databricks, giảm working set PostgreSQL
```

**Bước 10 — Benchmark và document kết quả:**
```sql
-- Trước fix:
\timing on
SELECT ... ; -- 15 giây

-- Sau mỗi fix, measure lại:
ANALYZE tick_data;
SELECT ... ; -- 8 giây

REINDEX CONCURRENTLY idx_tick_symbol_time;
SELECT ... ; -- 3 giây

-- Nếu vẫn > 1 giây → cân nhắc Materialized View / aggregate table
CREATE MATERIALIZED VIEW mv_tick_eurusd_daily AS
SELECT DATE_TRUNC('day', tick_time), COUNT(*), AVG(ask-bid), SUM(volume)
FROM tick_data WHERE symbol='EURUSD'
GROUP BY 1;
-- Query từ MV: < 100ms
```

**Kết luận cho interviewer**: Vấn đề 15 giây thường có 2–3 nguyên nhân cộng hưởng, không phải 1. Bước 1 (EXPLAIN ANALYZE + BUFFERS) luôn là điểm bắt đầu — không đoán, không fix blind.

---

## 14. Ba chủ đề còn thiếu chiều sâu

---

### 14.1 PostgreSQL MVCC — Cơ chế hoạt động

#### Vấn đề MVCC giải quyết

Không có MVCC: reader phải chờ writer, writer phải chờ reader → lock contention cao.

MVCC giải quyết: **reader không bao giờ block writer, writer không bao giờ block reader** — mỗi transaction thấy một **snapshot nhất quán** của data tại thời điểm nó bắt đầu.

#### Cơ chế xmin / xmax

Mỗi row trong PostgreSQL có 2 hidden columns:

| Column | Ý nghĩa |
|--------|---------|
| `xmin` | Transaction ID (XID) đã INSERT row này |
| `xmax` | XID đã DELETE hoặc UPDATE row này (0 nếu chưa bị xóa) |

```
Bảng positions (simplified):
┌─────────────┬───────────┬──────────────────────────────┐
│    xmin     │   xmax    │         data                 │
├─────────────┼───────────┼──────────────────────────────┤
│    100      │     0     │ position_id=1, status='OPEN' │  ← live row
│    100      │    205    │ position_id=2, status='OPEN' │  ← dead (updated by tx 205)
│    205      │     0     │ position_id=2, status='CLOSE'│  ← new version from tx 205
└─────────────┴───────────┴──────────────────────────────┘
```

Khi transaction 205 UPDATE position_id=2:
- Row cũ: `xmax = 205` (đánh dấu "deleted by tx 205")
- Row mới được INSERT: `xmin = 205`, `xmax = 0`
- Cả 2 row tồn tại **vật lý trên disk** — không xóa row cũ ngay

#### Transaction Snapshot và Visibility Rule

Khi transaction bắt đầu, nó nhận một **snapshot**: danh sách các XID đang active (chưa commit) tại thời điểm đó.

**Visibility rule** — row version visible với transaction T nếu:
```
xmin đã COMMIT  AND  xmin < T's snapshot horizon
AND
(xmax = 0  OR  xmax chưa commit  OR  xmax > T's snapshot horizon)
```

**Ví dụ thực tế**:
```
Timeline:
  TX 100: INSERT position (xmin=100)       → commit
  TX 200: BEGIN                            ← snapshot: {không có active TX}
  TX 205: UPDATE position (xmax=205 cũ, xmin=205 mới) → commit
  TX 200: SELECT * FROM positions          ← thấy row nào?
```

TX 200 thấy row với `xmin=100, xmax=205`:
- `xmin=100` đã commit trước snapshot của TX 200 → visible
- `xmax=205` commit **sau** khi TX 200 bắt đầu → TX 200 **không** thấy xmax này
- → TX 200 thấy row cũ (`status='OPEN'`) dù TX 205 đã update

Đây là **Repeatable Read** behavior của MVCC — đọc nhất quán trong suốt transaction.

#### Hậu quả: Dead Tuples và VACUUM

Row cũ (`xmin=100, xmax=205`) trở thành **dead tuple** khi không còn transaction nào cần nó (snapshot cũ nhất đã qua `xmin=100`).

Dead tuples không tự biến mất — chúng chiếm disk space cho đến khi **VACUUM** chạy và reclaim.

```
Tick_data: 50M inserts/ngày
Positions: 10K updates/ngày (SL/TP adjustments)

Dead tuples/ngày từ positions: 10K rows
Sau 30 ngày không VACUUM: 300K dead tuples
Mỗi row ~200 bytes → ~60MB table bloat chỉ từ positions
```

#### Transaction ID Wraparound — nguy hiểm thực sự

XID là 32-bit integer → max ~2.1 tỷ transactions. Khi XID gần wrap around (~200M transactions còn lại), PostgreSQL cảnh báo. Khi wrap around **mà không VACUUM**: PostgreSQL **không nhận writes mới** để bảo vệ data.

```sql
-- Kiểm tra XID age
SELECT relname,
       age(relfrozenxid) AS xid_age,
       2100000000 - age(relfrozenxid) AS txns_remaining
FROM pg_class
WHERE relkind = 'r'
ORDER BY age(relfrozenxid) DESC
LIMIT 5;
-- age > 1.5 tỷ → cần VACUUM FREEZE ngay
```

#### Tóm tắt MVCC trong 1 câu (để nói với interviewer)

> "PostgreSQL MVCC lưu nhiều version của cùng 1 row — mỗi row có xmin (ai tạo) và xmax (ai xóa). Transaction thấy snapshot tại thời điểm bắt đầu, không thấy thay đổi của transaction đồng thời. Row cũ trở thành dead tuple, VACUUM dọn dẹp chúng. Đây là lý do VACUUM bắt buộc trên bảng write-heavy như tick_data."

---

### 14.2 Hash Join vs Merge Join vs Nested Loop — So sánh tại một chỗ

#### Bảng so sánh nhanh

| | Nested Loop | Hash Join | Merge Join |
|--|-------------|-----------|-----------|
| **Điều kiện tốt** | Outer nhỏ + inner có index | Cả 2 bảng lớn, không có index join key | Cả 2 đã sorted trên join key |
| **Điều kiện tệ** | Outer lớn → N×M operations | Hash table > work_mem → spill disk | Cần Sort node nếu chưa sorted → RAM + CPU |
| **Memory** | Gần như không dùng | work_mem cho hash table | work_mem cho sort (nếu cần) |
| **Complexity** | O(N × log M) với index | O(N + M) build+probe | O(N + M) sau sort |
| **Index required** | Có (trên inner) | Không | Không (nhưng có thì tốt) |
| **Output sorted** | Không | Không | Có (theo join key) |

#### Nested Loop — khi nào Planner chọn?

```
positions (100 OPEN rows)  JOIN  tick_data (50M rows, index on symbol)

For each of 100 positions:
    Index Seek tick_data WHERE symbol = position.symbol
    → 100 × O(log 50M) = 100 × 26 steps = 2,600 operations
```

Planner chọn Nested Loop khi **outer cardinality nhỏ** (sau filter) và **inner có index**. Vấn đề xảy ra khi Planner estimate sai outer cardinality:

```sql
-- EXPLAIN output cảnh báo:
Nested Loop (actual rows=50000 loops=100000)
--                                   ↑ 100K vòng lặp → N+1 ẩn
-- actual time >> estimated time → statistics stale
```

#### Hash Join — khi nào spill?

```
Hash Join build phase:
  Inner table (daily_symbol_stats, 5M rows × 100 bytes = 500MB)
  work_mem = 64MB
  → 500MB / 64MB ≈ 8 batches cần thiết

EXPLAIN output:
  Hash  (Batches: 8  Memory Usage: 64kB)
  --     ↑ 8 > 1 = spill xảy ra, performance giảm 10×+
```

Fix cho session cụ thể:
```sql
SET work_mem = '512MB';
-- Kiểm tra lại
EXPLAIN ANALYZE <query>;
-- Batches: 1 → không còn spill
```

#### Merge Join — khi nào tốt hơn Hash Join?

```sql
-- Cả 2 bảng có Index Scan trên join key → đã sorted miễn phí
SELECT t.bid, p.volume
FROM tick_data t
JOIN positions p ON t.symbol = p.symbol
WHERE t.tick_time >= NOW() - INTERVAL '1 hour';

-- Nếu cả 2 có index trên symbol:
-- Merge Join dùng output sorted của 2 Index Scan → không cần hash table
-- Memory = 0, không spill risk
```

Merge Join tốt hơn Hash Join khi: data đã sorted sẵn qua index + memory bị giới hạn.

#### Quyết định của Planner theo từng scenario trong dự án

| Scenario | Join được chọn | Lý do |
|----------|---------------|-------|
| `positions (50 OPEN) JOIN tick_data` | **Nested Loop** | Outer rất nhỏ, inner có index trên symbol |
| `tick_data (1h) JOIN daily_stats (all)` | **Hash Join** | daily_stats nhỏ → build hash table, probe tick_data |
| `tick_data JOIN orders` (cả 2 có Index Scan trên symbol) | **Merge Join** | Cả 2 đã sorted → merge miễn phí |
| `tick_data (full) JOIN positions (full)` | **Hash Join** | Không có filter đủ chọn lọc, không có index hữu ích |

---

### 14.3 Bloat — Định nghĩa rõ ràng và số cụ thể

#### Bloat là gì?

**Table Bloat**: Không gian vật lý trên disk bị chiếm bởi dead tuples — rows đã bị UPDATE hoặc DELETE nhưng chưa được VACUUM reclaim.

**Index Bloat**: Không gian lãng phí trong B-tree index do dead entries (pointer đến dead tuples) và page splits làm leaf pages chỉ 50–60% đầy thay vì 90%+.

#### Số cụ thể để nói trong phỏng vấn

**Kịch bản trong dự án**:
```
positions: 500K total rows, 10K updates/ngày (SL/TP adjustments)
Mỗi UPDATE tạo 1 dead tuple (row cũ bị đánh dấu xmax)

Nếu autovacuum bị disable hoặc quá chậm:
  Sau 7 ngày:   70K dead tuples  × 200 bytes = ~14MB bloat
  Sau 30 ngày:  300K dead tuples × 200 bytes = ~60MB table bloat
  Sau 1 năm:    3.6M dead tuples              = ~720MB table bloat

Index trên (broker, symbol, open_time):
  Mỗi UPDATE → 1 dead index entry
  Sau 1 năm: index leaf pages trung bình 55% đầy thay vì 90%
  Index size bloat: 1.6× → index 160MB thay vì 100MB
  avg_leaf_density 55% → random I/O tăng vì phải đọc nhiều pages hơn
```

#### Đo bloat thực tế

```sql
-- Đo nhanh qua pg_stat_user_tables
SELECT relname,
       n_live_tup,
       n_dead_tup,
       round(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 1) AS dead_pct,
       pg_size_pretty(pg_total_relation_size(oid)) AS total_size,
       last_autovacuum
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_dead_tup DESC;

-- dead_pct > 10% trên bảng write-heavy → cần attention
-- dead_pct > 30% → VACUUM thủ công hoặc tăng autovacuum frequency

-- Đo index bloat (cần extension)
CREATE EXTENSION IF NOT EXISTS pgstattuple;
SELECT * FROM pgstatindex('idx_positions_open');
-- avg_leaf_density < 60% → xem xét REINDEX CONCURRENTLY
```

#### 3 mức severity và hành động

| dead_pct / avg_leaf_density | Mức | Hành động |
|----------------------------|-----|-----------|
| < 10% / > 80% | Bình thường | Autovacuum tự xử lý |
| 10–30% / 60–80% | Cảnh báo | Tăng `autovacuum_vacuum_scale_factor`, monitor |
| > 30% / < 60% | Nghiêm trọng | `VACUUM ANALYZE` thủ công; `REINDEX CONCURRENTLY` cho index |

#### Tại sao VACUUM không reclaim disk về OS?

```
Trước VACUUM:  [live][dead][dead][live][dead]  = 5 pages trên disk
Sau VACUUM:    [live][    ][    ][live][    ]  = 5 pages (vẫn 5 pages!)
               ↑ pages được mark "reusable" nhưng OS không lấy lại
```

`VACUUM` chỉ mark không gian là reusable cho INSERT mới — file vật lý không shrink. Chỉ `VACUUM FULL` mới rewrite và trả disk về OS (nhưng cần exclusive lock).

**Trong thực tế**: Không cần disk shrink nếu data tiếp tục grow. VACUUM đủ vì INSERT mới sẽ tái dùng space đó.

#### Cách nói trong phỏng vấn (1 đoạn)

> "Bloat xảy ra vì MVCC — khi UPDATE row, PostgreSQL không sửa tại chỗ mà tạo row mới và đánh dấu row cũ là dead. Dead tuples tích lũy thành table bloat và index bloat. Với positions table nhận 10K updates/ngày, sau 1 tháng không VACUUM có thể tích 60MB bloat — index leaf density giảm từ 90% xuống 55%, random I/O tăng. VACUUM dọn dead tuples nhưng không trả disk về OS, chỉ mark space reusable. Tôi monitor bằng `pg_stat_user_tables.n_dead_tup` và alert khi dead_pct > 20%."

---

*Cập nhật: 2026-06-18 | Dùng cho phỏng vấn Middle+ / Senior Python + SQL Dev*
