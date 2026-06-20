# I. Về dự án NSCM
Là dự án quản lý các nhà máy của SS electrolic. Mục đích tăng performance cho hệ thống -> chuyển đổi từ java sang python+oracle -> Dự án tìm các nhân sự có kinh nghiệm SQL, về python chỉ cần python core.

# II. Thông tin cần chuẩn bị khi tham gia pv dự án:
Phần giới thiệu bản thân yêu cầu phải nêu rõ những dự án nổi bật đã tham gia.

KH sẽ hỏi để đánh giá nhân sự có thực sự hiểu những dự án đã làm -> anh em xem chuẩn bị 1, 2 dự án để nói (vai trò trong dự án, khó khăn gặp phải -> cách vượt qua nó....)

KH mong muốn nhân sự cầu tiến.

# Python & Frameworks:
**1. Tại sao từ khóa `global` được sử dụng?**
Từ khóa `global` dùng để cho phép một hàm thay đổi giá trị của một biến toàn cục (đã khai báo ở ngoài hàm). Nếu không có `global`, Python sẽ hiểu bạn đang tạo ra một biến cục bộ mới.
*Ví dụ:* `count = 0`. Trong hàm: `global count; count += 1`.

**2. Threading và Multiprocessing?**
Python hỗ trợ cả hai. **Threading** dùng chung bộ nhớ nhưng bị khóa bởi GIL (chỉ 1 luồng chạy tại 1 thời điểm), hợp với I/O Bound (gọi mạng, đọc file). **Multiprocessing** tạo các tiến trình độc lập với bộ nhớ riêng, lách được GIL, hợp với tính toán nặng (CPU Bound).

**3. Làm việc với file? Ví dụ ngắn.**
Thường dùng hàm `open()` kết hợp với từ khoá `with` để tự động đóng file sau khi xử lý xong (tránh kẹt tài nguyên).
*Ví dụ đọc file:* `with open('data.txt', 'r') as f: content = f.read()`

**4. Xử lý ngoại lệ (Exception handling)?**
Dùng khối lệnh `try...except...finally` để bắt lỗi mà không làm sập app. Code có rủi ro để trong `try`, cách xử lý lỗi nằm ở `except`, và `finally` để dọn dẹp tài nguyên (như đóng DB) bất kể có lỗi hay không.

**5. Lớp, đối tượng, và kế thừa trong OOP?**
**Lớp (Class)** là bản thiết kế chung (vd: bản vẽ xe). **Đối tượng (Object)** là một thực thể cụ thể tạo ra từ bản vẽ đó (vd: chiếc xe thật). **Kế thừa (Inheritance)** là việc Class con nhận lại toàn bộ thuộc tính và hàm của Class cha mà không cần viết lại.

**6. Sự kế thừa và tính đa hình?**
*Kế thừa* giúp tái sử dụng code (Chó kế thừa Động vật). *Đa hình (Polymorphism)* là khả năng các Class khác nhau có cùng một phương thức nhưng cách chạy lại khác nhau (Động vật có hàm `speak()`, nhưng Chó kêu Gâu, Mèo kêu Meo).

**7. Virtual Environments (Môi trường ảo)?**
Nó tạo ra các không gian cô lập để cài đặt thư viện riêng cho từng dự án (vd: `venv`, `conda`). Nó cực kỳ quan trọng để tránh xung đột phiên bản, ví dụ: Dự án A cần dùng Django 2, nhưng dự án B lại bắt buộc dùng Django 3.

**8. Đọc và ghi file?**
Dùng `with open()` với mode `'r'` để đọc, mode `'w'` để ghi đè (hoặc `'a'` để ghi tiếp vào cuối file).
*Ví dụ ghi file:* `with open('log.txt', 'w') as f: f.write('Hello World')`

**9. Dự án Python và thách thức? (Gợi ý cách trả lời thực chiến)**
*Đáp án mẫu:* "Tôi từng xử lý file dữ liệu lớn bị lỗi cạn kiệt bộ nhớ (MemoryError). Tôi đã giải quyết bằng cách thay vì đọc toàn bộ, tôi dùng **Generator** đọc từng chunk nhỏ, kết hợp **Multiprocessing** để xử lý song song, giúp giảm thời gian chạy đi một nửa."

**10. Tích hợp API vào ứng dụng?**
Tôi thường xuyên làm việc với REST API. Tôi sử dụng thư viện `requests` để gọi API ngoài (GET, POST) và xử lý dữ liệu trả về dạng JSON. Nếu phải tự xây API Backend, tôi sẽ dùng FastAPI hoặc Flask.
*(**Giải thích thêm:** RESTful API là tiêu chuẩn thiết kế web service dựa trên giao thức HTTP. Nó quản lý dữ liệu như các tài nguyên (resources) thông qua URL, sử dụng các phương thức chuẩn (GET để đọc, POST để tạo, PUT/PATCH để sửa, DELETE để xóa), giao tiếp thường bằng định dạng JSON và đặc biệt có tính phi trạng thái - stateless).*

**11. CSDL và tối ưu hóa truy vấn?**
Tôi dùng Oracle/PostgreSQL. Để tối ưu, tôi đánh **Index** ở các cột hay dùng trong `WHERE`/`JOIN`, hạn chế Select `*`, dùng phân trang `LIMIT` thay vì lấy hết, và dùng lệnh `EXPLAIN` để xem CSDL thực thi query có bị Full Table Scan không.

**12. Đã từng tối ưu hóa ứng dụng Python chưa? (Gợi ý)**
*Đáp án mẫu:* "Có, một tính năng phải gọi API tới 5 dịch vụ khác nhau theo kiểu tuần tự (chờ xong cái này mới gọi cái kia) rất chậm. Tôi đã dùng thư viện `asyncio` / `aiohttp` để gọi bất đồng bộ cùng lúc, giảm thời gian từ 10s xuống 2s."

*(**Mở rộng: Các câu hỏi phỏng vấn chuyên sâu về AsyncIO / Asynchronous**)*
* **Q1: Lập trình đồng bộ (Synchronous) và bất đồng bộ (Asynchronous) khác nhau thế nào?**
  * *Trả lời:* Đồng bộ (Synchronous) thực thi code tuần tự từng dòng, dòng này chạy xong mới tới dòng kia (hay bị block khi gặp độ trễ). Bất đồng bộ (Asynchronous) cho phép gửi yêu cầu đi và không cần chờ kết quả trả về ngay. Trong lúc rảnh (như chờ API/Database phản hồi), luồng xử lý sẽ làm việc khác, không bị block. Rất hữu ích cho các tác vụ nặng về I/O.
* **Q2: `async` và `await` trong Python dùng để làm gì?**
  * *Trả lời:* `async` (cụ thể là `async def`) dùng để khai báo một hàm bất đồng bộ (gọi là coroutine). `await` dùng để nhường quyền kiểm soát (yield control) lại cho Event Loop trong lúc chờ một tác vụ nào đó hoàn thành.
* **Q3: Tại sao không dùng luôn `requests` trong hàm `async` mà phải dùng `aiohttp`?**
  * *Trả lời:* Thư viện `requests` là thư viện đồng bộ (blocking IO). Nếu đặt `requests.get()` vào hàm `async`, nó sẽ "block" toàn bộ Event Loop, khiến tất cả các hàm async khác phải đứng chờ nó. Để chạy bất đồng bộ thực sự trên mạng, ta phải dùng thư viện được thiết kế dạng non-blocking như `aiohttp` hoặc `httpx` (cùng các driver DB bất đồng bộ như `asyncpg`).
* **Q4: `asyncio` có giúp Python chạy song song trên nhiều nhân (multi-core CPU) không?**
  * *Trả lời:* **Không**. `asyncio` mặc định vẫn chạy trên **một luồng duy nhất (Single-thread)** và một nhân CPU do giới hạn của GIL (Global Interpreter Lock). Tác dụng của nó là tối ưu thời gian chờ **I/O Bound** nhờ luân chuyển task. Để tận dụng nhiều nhân CPU cho các tác vụ nặng về tính toán (**CPU Bound**), ta bắt buộc phải dùng thư viện **Multiprocessing**.

**13. Kiểm tra hiệu suất (Performance testing)?**
Ở mức code, tôi dùng thư viện `time` hoặc `timeit` để đo thời gian chạy của hàm, dùng `cProfile` để xem hàm nào ngốn CPU nhất. Ở mức hệ thống, tôi theo dõi RAM/CPU qua các tool monitor cấp server.

**14. Python có biến nguyên thủy (Primitive types) không?**
**Không**. Trong Python, "vạn vật đều là Object (Đối tượng)". Kể cả các số cơ bản như `int`, `float`, `bool` hay `str` thực chất đều là các đối tượng được sinh ra từ các Class tương ứng trong Python.

**15. Tuple và List khác gì nhau?**
`List` dùng ngoặc vuông `[]` và **có thể thay đổi** (Mutable - thêm, sửa, xóa phần tử). `Tuple` dùng ngoặc tròn `()` và **không thể thay đổi** (Immutable). Do cố định, Tuple truy xuất nhanh hơn và tốn ít RAM hơn List.

**16. Xử lý Logging và Monitoring?**
Trong code, tôi dùng thư viện `logging` của Python để ghi log (INFO, ERROR) ra file. Với hệ thống lớn, tôi đẩy log lên ELK Stack (Elasticsearch, Kibana) để dễ tìm kiếm, và dùng Prometheus/Grafana để báo động (alert) khi API chạy quá chậm.

**17. Deep copy và Shallow copy?**
**Shallow copy** (Sao chép nông) tạo vỏ ngoài mới, nhưng các object lồng bên trong vẫn dùng chung vùng nhớ với bản gốc. **Deep copy** (Sao chép sâu `copy.deepcopy()`) sao chép đệ quy tạo ra vùng nhớ mới hoàn toàn cho cả lớp ngoài lẫn mọi lớp trong.

**18. Flask là gì? (Giải thích chi tiết)**
Flask là một **Micro-Framework** của Python dùng để làm Web và API. 
* **Đặc điểm:** Triết lý của Flask là "giữ mọi thứ đơn giản và cốt lõi nhất". Nó cực kỳ nhẹ, không nhồi nhét sẵn công cụ thao tác CSDL (ORM), không có sẵn hệ thống xác thực (Auth) hay cấu trúc thư mục gò bó. 
* **Ưu điểm:** Độ linh hoạt tối đa. Lập trình viên có toàn quyền quyết định lắp ráp thêm thư viện nào mình thích (ví dụ: dùng SQLAlchemy cho DB, JWT cho Auth).
* **Ứng dụng:** Rất thích hợp để xây dựng các **Microservices** độc lập, các API nhanh gọn, hoặc các dự án AI/Machine Learning chỉ cần một API bọc bên ngoài mô hình dự đoán.

**19. Django là gì? (Giải thích chi tiết)**
Django là một **Full-stack Web Framework** đồ sộ theo triết lý "Batteries-included" (có sẵn mọi thứ).
* **Đặc điểm:** Nó cung cấp sẵn mọi tính năng ngay khi vừa cài đặt: Django ORM cực mạnh, hệ thống Authentication (đăng nhập/phân quyền), bảo mật chống CSRF/SQL Injection, và tính năng "ăn tiền" nhất là **tự động sinh ra một trang Admin quản trị nội dung** ngay lập tức.
* **Ưu điểm:** Giúp team phát triển các dự án phức tạp với tốc độ chóng mặt, tuân thủ chặt chẽ cấu trúc chuẩn MVT (Model - View - Template).
* **Ứng dụng:** Phù hợp cho các dự án Web quy mô lớn, hệ thống CMS, nền tảng thương mại điện tử, hoặc hệ thống cần quản lý cơ sở dữ liệu/người dùng phức tạp.

*(**Câu hỏi phụ: Khi nào chọn Flask, khi nào chọn Django?**)*
* Chọn **Flask** khi: Bạn cần làm một API siêu nhanh, microservices, dự án nhỏ nhắn, hoặc bạn muốn tự do tối đa trong việc thiết kế kiến trúc hệ thống.
* Chọn **Django** khi: Bạn muốn xây dựng một hệ thống Web Monolithic (khối thống nhất) hoàn chỉnh, cần gấp một trang Admin CMS, và muốn code được chuẩn hóa sẵn cho cả một team lớn dễ làm việc chung.

*(**Ví dụ code minh họa xây dựng API cơ bản**)*

**Ví dụ 1: API với Flask (Rất ngắn gọn, chạy ngay trong 1 file)**
```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/hello', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello from Flask!", "status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```
*Nhận xét:* Chỉ với vài dòng code, bạn đã có ngay một API hoạt động. Rất phù hợp để bọc các hàm xử lý Data/AI nhanh.

**Ví dụ 2: API với Django (Sử dụng Django REST Framework - Cần cấu trúc rõ ràng)**
Để làm được API tương tự, trong Django bạn không thể viết chung trong 1 file mà phải setup cấu trúc project rõ ràng (tách biệt logic và routing).

*File `views.py` (Xử lý logic)*:
```python
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello from Django!", "status": "success"})
```

*File `urls.py` (Định tuyến/Routing)*:
```python
from django.urls import path
from .views import hello_world

urlpatterns = [
    path('api/hello/', hello_world),
]
```
*Nhận xét:* Django đòi hỏi setup cấu trúc bài bản hơn từ đầu (nhiều file, nhiều cấu hình), nhưng bù lại khi dự án "phình to" với hàng chục tính năng, cách tổ chức này sẽ giúp code rất gọn gàng và dễ bảo trì.

## 20. Các Design Pattern (Mẫu thiết kế) phổ biến trong Python?
Design Pattern là các giải pháp mẫu đã được chứng minh hiệu quả để giải quyết các vấn đề thiết kế phần mềm. Do tính linh hoạt của Python (hàm cũng là object), một số pattern rất dễ cài đặt. Dưới đây là 3 mẫu hay bị hỏi nhất:

**1. Singleton Pattern (Độc bản)**
* **Mục đích:** Đảm bảo một Class chỉ sinh ra **duy nhất 1 object** trong suốt vòng đời ứng dụng. Thường dùng để quản lý kết nối Database (tránh mở quá nhiều connection), cấu hình hệ thống, hoặc Logging.
* **Ví dụ (bằng cách ghi đè `__new__`):**
  ```python
  class DatabaseConnection:
      _instance = None
      
      def __new__(cls):
          if cls._instance is None:
              cls._instance = super(DatabaseConnection, cls).__new__(cls)
          return cls._instance

  # Cả db1 và db2 đều trỏ chung về 1 địa chỉ bộ nhớ (1 connection)
  db1 = DatabaseConnection()
  db2 = DatabaseConnection()
  print(db1 is db2)  # Trả về True
  ```

**2. Factory Pattern (Nhà máy)**
* **Mục đích:** Giao việc khởi tạo Object cho một "nhà máy" xử lý thay vì gọi trực tiếp Class. Rất tiện lợi khi bạn cần tạo ra nhiều loại đối tượng khác nhau dựa trên tham số đầu vào mà không muốn để lộ logic If-Else rườm rà ra bên ngoài.
* **Ví dụ:**
  ```python
  class Dog: pass
  class Cat: pass

  class AnimalFactory:
      @staticmethod
      def create_animal(animal_type):
          if animal_type == "dog": return Dog()
          elif animal_type == "cat": return Cat()

  # Chỉ cần ra lệnh cho Factory
  pet = AnimalFactory.create_animal("dog")
  ```

**3. Decorator Pattern (Trang trí)**
* **Mục đích:** Bổ sung thêm tính năng mới cho một hàm/class mà **không cần sửa đổi code bên trong hàm đó**. Đây là một "đặc sản" của Python (sử dụng cú pháp `@`).
* **Ứng dụng:** Thường dùng để viết các logic chạy trước/chạy sau hàm chính như: Kiểm tra quyền đăng nhập (Auth), Ghi Log, hoặc Đo thời gian chạy của hàm.
* **Ví dụ (Đo thời gian):**
  ```python
  import time

  def timer_decorator(func):
      def wrapper(*args, **kwargs):
          start = time.time()
          result = func(*args, **kwargs)
          print(f"Thời gian chạy: {time.time() - start}s")
          return result
      return wrapper

  @timer_decorator
  def slow_task():
      time.sleep(1) # Giả lập hàm chạy chậm
      
  slow_task() # Khi gọi, wrapper sẽ tự động tính giờ
  ```

> **Mẹo phỏng vấn:** Đừng cố nhồi nhét thuộc lòng 23 mẫu Design Pattern của GoF (vốn phù hợp với Java/C++ hơn). Khi phỏng vấn Python, hãy nắm thật chắc **Singleton**, **Factory**, và đặc biệt là **Decorator**.

## 21. Double Underscore (Dunder) hay Magic Methods trong Python là gì?
Trong Python, các hàm có hai dấu gạch dưới ở đầu và cuối (ví dụ: `__init__`, `__str__`, `__len__`) được gọi là **Dunder methods** (Double UNDERscore) hoặc **Magic methods**.

* **Mục đích:** Chúng hầu như không bao giờ được gọi trực tiếp bởi lập trình viên (rất hiếm khi bạn viết `obj.__str__()`), mà được Python **tự động gọi ngầm** ở phía sau khi bạn sử dụng các toán tử hoặc hàm có sẵn của Python. Tính năng này giúp các object do bạn tự định nghĩa có thể hoạt động tự nhiên giống hệt như các kiểu dữ liệu gốc (int, list, dict...).

* **Các Dunder methods hay bị hỏi phỏng vấn nhất:**
  1. `__init__(self, ...)`: Hàm khởi tạo (Constructor). Tự động chạy ngay khi bạn tạo một Object mới.
  2. `__str__(self)`: Tự động chạy khi bạn dùng lệnh `print(obj)` hoặc ép kiểu `str(obj)`. Dùng để trả về chuỗi mô tả thân thiện, dễ đọc cho người dùng (End-user).
  3. `__repr__(self)`: Giống `__str__` nhưng trả về chuỗi chi tiết, mang tính kỹ thuật cao dành cho Lập trình viên debug. Nếu Class không có hàm `__str__`, Python sẽ tự động lấy `__repr__` để thay thế khi in ra màn hình.
  4. `__len__(self)`: Tự động chạy khi bạn gọi hàm `len(obj)`.
  5. `__getitem__(self, key)`: Trả về phần tử. Cho phép Object của bạn truy xuất dữ liệu bằng ngoặc vuông giống hệt List hoặc Dict (ví dụ: `obj[0]` hoặc `obj['key']`).
  6. `__call__(self, ...)`: Biến một Object trở thành một hàm (callable). Nếu bạn gọi trực tiếp object như một hàm (ví dụ: `obj()`), Python sẽ nhảy vào chạy hàm `__call__` này.

* **Ví dụ minh họa:**
  ```python
  class Team:
      def __init__(self, name):
          self.name = name
          self.members = ["Alice", "Bob", "Charlie"]

      # Khi gọi print(team)
      def __str__(self):
          return f"Team {self.name} hiện có {len(self.members)} người."

      # Khi gọi len(team)
      def __len__(self):
          return len(self.members)
          
      # Khi truy xuất ngoặc vuông team[0]
      def __getitem__(self, index):
          return self.members[index]

  # Cách hoạt động:
  t = Team("Backend")
  print(t)      # Gọi ngầm __str__ -> "Team Backend hiện có 3 người."
  print(len(t)) # Gọi ngầm __len__ -> 3
  print(t[1])   # Gọi ngầm __getitem__ -> "Bob"
  ```

# Xử lý Dataframe (Pandas & Polars)
Yêu cầu của dự án NSCM là tối ưu hóa hiệu suất, do đó việc hiểu rõ sự khác biệt và cách tối ưu Dataframe là **bắt buộc**.

### 1. So sánh cốt lõi (Pandas vs Polars)
- **Pandas:** Hoạt động theo cơ chế **Eager Evaluation** (thực thi ngay lập tức), chạy trên **đơn luồng (Single-thread)**, dựa trên thư viện NumPy. Nó phổ biến nhưng tiêu tốn rất nhiều RAM (thường cần RAM gấp 5-10 lần kích thước file thực tế).
- **Polars:** Viết bằng ngôn ngữ **Rust**, sử dụng kiến trúc bộ nhớ Apache Arrow. Hỗ trợ **đa luồng (Multi-threading)** tự động và **Xử lý lười (Lazy Evaluation)**. Polars nhanh hơn Pandas gấp nhiều lần và xử lý được dữ liệu lớn hơn RAM hệ thống (out-of-core).

### 2. Các câu hỏi phỏng vấn thường gặp
**Câu 1: Lazy Evaluation (Đánh giá lười) trong Polars là gì? Tại sao nó làm Polars nhanh hơn Pandas?**
*Đáp án:* Trong khi Pandas chạy code tuần tự từng dòng (Eager), Polars dùng Lazy evaluation (`pl.LazyFrame`). Nó không chạy code ngay mà gom các câu lệnh lại thành một bản kế hoạch (Query Plan). Bộ tối ưu hóa của Polars sẽ tự động viết lại kế hoạch này (ví dụ: gộp các bước `filter`, loại bỏ các cột không dùng tới) rồi mới thực thi song song toàn bộ khi ta gọi lệnh `.collect()`. Điều này tiết kiệm cực nhiều tài nguyên.

**Câu 2: Nếu phải dùng Pandas đọc một file CSV 10GB nhưng RAM máy chỉ có 8GB, bạn xử lý thế nào?**
*Đáp án mẫu:* 
1. Đọc file theo từng khối nhỏ (chunk) bằng tham số `chunksize` và xử lý từng phần một.
2. Tối ưu hóa kiểu dữ liệu (`dtype`) ngay khi đọc: ép kiểu `float64` thành `float32`, chuyển chuỗi lặp lại (ví dụ giới tính Nam/Nữ) thành kiểu `category`.
3. Chỉ `usecols` những cột thực sự cần thiết.
4. Nếu được phép, tôi sẽ đề xuất đổi sang dùng Polars (`pl.scan_csv()`) để đọc file lớn hơn RAM dễ dàng.

**Câu 3: Làm sao để tối ưu hoá vòng lặp trong Pandas? (Tại sao `.apply()` lại chậm?)**
*Đáp án:* Dùng vòng lặp `for` hay hàm `.apply()` trong Pandas cực kỳ chậm vì nó duyệt qua từng hàng một (row-by-row) giống hệt vòng lặp Python thuần, phải chịu toàn bộ chi phí (overhead) khởi tạo object của Python cho mỗi lần lặp. 
Cách tối ưu nhất là **Vectorization (Vector hóa)**. 

*(**Giải thích sâu hơn để trả lời phỏng vấn:**)*
* **Tại sao Vectorization siêu nhanh?** Thay vì đưa từng phần tử lên cho Python xử lý, Vectorization cho phép đẩy thẳng cả cột dữ liệu (dạng mảng NumPy) xuống tầng lõi ngôn ngữ C bên dưới. C sẽ dùng tập lệnh xử lý ma trận (SIMD của CPU) để tính toán đồng loạt một lúc.
* **Quy tắc "Vàng" về thứ tự ưu tiên khi xử lý cột trong Pandas:**
  1. **Tuyệt đối tránh** dùng `for index, row in df.iterrows():` (Chậm nhất, hiệu năng thảm họa).
  2. **Hạn chế tối đa** dùng `df.apply(lambda x: ...)` (Thực chất chỉ là một vòng lặp `for` ngầm, tốc độ vẫn cực kỳ chậm).
  3. **Ưu tiên dùng Vectorization cơ bản:** Các phép toán `+`, `-`, `*`, `/` hoặc các hàm chuỗi `df['col'].str...` trực tiếp trên cột (rất nhanh).
  4. **Khi cần xử lý logic phân nhánh If-Else:**
     - Nếu có 2 trường hợp (If/Else): Bắt buộc dùng `np.where(điều_kiện, kết_quả_đúng, kết_quả_sai)`. Nó tận dụng được Vectorization và nhanh gấp hàng trăm lần so với `.apply()`.
     - Nếu có nhiều trường hợp (If/Elif/Else): Sử dụng `np.select(danh_sách_điều_kiện, danh_sách_kết_quả, default)`.

**Câu 4: Có thể dùng chung Pandas và Polars trong 1 project không?**
*Đáp án:* Có, và việc chuyển đổi diễn ra cực kỳ nhanh (zero-copy) vì cả hai đều hỗ trợ định dạng Apache Arrow.
- Chuyển thành Polars: `pl_df = pl.from_pandas(pd_df)`
- Chuyển thành Pandas: `pd_df = pl_df.to_pandas()`

### 3. Bộ câu hỏi phỏng vấn chi tiết (Middle Python / Data Engineer)

**1. Pandas và Polars khác nhau như thế nào?**
**Trả lời:**
* Pandas được xây dựng trên NumPy, xử lý chủ yếu single-thread.
* Polars được viết bằng Rust, hỗ trợ multi-threading mặc định.
* Polars tối ưu cho dữ liệu lớn hơn và nhanh hơn trong nhiều tác vụ ETL.

**2. Khi nào nên dùng Pandas?**
**Trả lời:**
* Dataset nhỏ đến trung bình (< vài GB).
* Cần hệ sinh thái lớn (Scikit-learn, Statsmodels, Matplotlib).
* Team đã quen Pandas.

**3. Khi nào nên dùng Polars?**
**Trả lời:**
* Dataset lớn.
* ETL pipeline.
* Transform dữ liệu phức tạp.
* Muốn tận dụng nhiều CPU cores.

**4. Vì sao Polars thường nhanh hơn Pandas?**
**Trả lời:**
Polars có:
* Multi-threading.
* Query optimization.
* Lazy execution.
* Apache Arrow memory format.
Trong khi Pandas chủ yếu chạy single-thread.

**5. Lazy Execution là gì?**
**Trả lời:**
Polars không thực thi ngay.
Ví dụ:
```python
(
    df.lazy()
      .filter(...)
      .group_by(...)
      .agg(...)
)
```
Chỉ khi:
```python
.collect()
```
mới thực sự chạy. Điều này cho phép optimizer tối ưu toàn bộ query.

**6. Eager Execution là gì?**
**Trả lời:**
Pandas thực hiện ngay khi gọi lệnh:
```python
df = df[df["price"] > 100]
```
Mỗi bước sẽ được thực thi ngay lập tức.

**7. Predicate Pushdown là gì?**
**Trả lời:**
Polars đẩy điều kiện filter xuống sát nguồn dữ liệu.
Ví dụ:
```python
scan_parquet()
.filter(pl.col("date") > ...)
```
Chỉ đọc dữ liệu cần thiết thay vì toàn bộ file.

**8. Projection Pushdown là gì?**
**Trả lời:**
Chỉ load các cột được sử dụng.
Ví dụ:
```python
.select(["id", "price"])
```
Polars chỉ đọc 2 cột đó từ Parquet.

**9. Apache Arrow là gì?**
**Trả lời:**
Là chuẩn lưu trữ dữ liệu dạng columnar trong bộ nhớ.
Ưu điểm:
* Zero-copy.
* Tốc độ cao.
* Chia sẻ dữ liệu giữa Spark, Pandas, Polars dễ dàng.

**10. Polars có sử dụng Arrow không?**
**Trả lời:**
Có. Polars lưu dữ liệu theo Arrow format nên giảm copy dữ liệu và tối ưu cache CPU.

**11. Tại sao columnar storage nhanh hơn row storage cho analytics?**
**Trả lời:**
Analytics thường chỉ đọc vài cột.
Columnar format:
```text
id
price
quantity
```
chỉ đọc cột cần thiết thay vì toàn bộ row.

**12. Polars có xử lý song song như thế nào?**
**Trả lời:**
Polars sử dụng Rust thread pool.
Các operation như: `filter`, `join`, `groupby`, `aggregation` được tự động chia nhiều thread.

**13. Pandas có multi-thread không?**
**Trả lời:**
Hầu hết operation của Pandas là single-thread. Một số hàm NumPy bên dưới có thể dùng nhiều core nhưng Pandas không tối ưu toàn diện như Polars.

**14. Polars có bị GIL không?**
**Trả lời:**
Không đáng kể. Logic xử lý nằm trong Rust. Rust code chạy ngoài Python GIL.

**15. Memory footprint của Polars và Pandas?**
**Trả lời:**
Polars thường dùng ít RAM hơn.
Nguyên nhân: Arrow format, Rust memory management, Query optimization.

**16. Sự khác nhau giữa read_parquet của Pandas và scan_parquet của Polars?**
**Trả lời:**
Pandas: `pd.read_parquet()` (Load toàn bộ file vào RAM).
Polars: `pl.scan_parquet()` (Tạo LazyFrame, chỉ đọc dữ liệu khi collect).

**17. LazyFrame và DataFrame khác nhau thế nào?**
**Trả lời:**
DataFrame: `pl.read_parquet()` (Dữ liệu đã được load).
LazyFrame: `pl.scan_parquet()` (Chỉ chứa execution plan).

**18. Trong ETL lớn bạn sẽ chọn Pandas hay Polars?**
**Trả lời:**
Nếu dữ liệu vài chục GB, nhiều join, nhiều aggregation => Polars.
Nếu phân tích ad-hoc, Notebook, Tích hợp ML => Pandas.

**19. Polars có thay thế được Spark không?**
**Trả lời:**
Không hoàn toàn. Polars (Single machine), Spark (Distributed cluster).
Polars nhanh hơn Spark trên dữ liệu vừa phải nhưng không scale ngang như Spark.

**20. Polars hay Spark khi xử lý 500GB dữ liệu?**
**Trả lời:**
Polars nếu một máy đủ RAM. Spark nếu cần cluster.
500GB thường chọn Spark hoặc Databricks.

**21. So sánh Pandas, Polars và Spark**
| Tiêu chí       | Pandas  | Polars     | Spark   |
| -------------- | ------- | ---------- | ------- |
| Engine         | NumPy   | Rust       | JVM     |
| Parallel       | Hạn chế | Có         | Có      |
| Lazy           | Không   | Có         | Có      |
| Distributed    | Không   | Không      | Có      |
| Dữ liệu lớn    | Kém     | Tốt        | Rất tốt |
| Learning Curve | Dễ      | Trung bình | Khó     |

**22. Tình huống phỏng vấn thực tế**
> Pipeline hiện tại dùng Pandas xử lý file CSV 20GB mất 30 phút. Bạn cải thiện thế nào?

**Trả lời mong đợi:**
1. Chuyển CSV → Parquet.
2. Dùng Polars thay Pandas.
3. Dùng LazyFrame.
4. Projection Pushdown.
5. Predicate Pushdown.
6. Nếu vẫn chậm thì Spark/Databricks.

**23. Câu hỏi nâng cao cho Middle+**
> Vì sao `scan_parquet()` nhanh hơn `read_parquet()`?

**Đáp án:**
`scan_parquet()` tạo execution plan và cho phép Predicate pushdown, Projection pushdown, Query optimization nên ít đọc dữ liệu hơn và ít sử dụng RAM hơn.

**24. Câu hỏi rất hay gặp trong Data Engineer**
> Tại sao Parquet + Polars thường nhanh hơn CSV + Pandas?

**Đáp án:**
CSV là Text format, phải parse toàn bộ. Parquet là Columnar format, có metadata, hỗ trợ column pruning và predicate pushdown.
Kết hợp với Polars sẽ giảm đáng kể IO và CPU.

## Phần mở rộng: Database & Data Engineering (Nâng cao cho Middle/Senior)

### 1. Window Function (Rất hay hỏi)

**ROW_NUMBER vs RANK vs DENSE_RANK**

Cho dữ liệu:
| Student | Score |
| ------- | ----- |
| A       | 100   |
| B       | 95    |
| C       | 95    |
| D       | 90    |

**ROW_NUMBER**
```sql
ROW_NUMBER() OVER (ORDER BY score DESC)
```
| Student | Rank |
| ------- | ---- |
| A       | 1    |
| B       | 2    |
| C       | 3    |
| D       | 4    |

**RANK**
```sql
RANK() OVER (ORDER BY score DESC)
```
| Student | Rank |
| ------- | ---- |
| A       | 1    |
| B       | 2    |
| C       | 2    |
| D       | 4    |

**DENSE_RANK**
```sql
DENSE_RANK() OVER (ORDER BY score DESC)
```
| Student | Rank |
| ------- | ---- |
| A       | 1    |
| B       | 2    |
| C       | 2    |
| D       | 3    |

**Top N mỗi nhóm**
Ví dụ: Lấy 3 giao dịch lớn nhất của mỗi khách hàng
```sql
WITH t AS (
   SELECT *,
          ROW_NUMBER() OVER(
             PARTITION BY customer_id
             ORDER BY amount DESC
          ) rn
   FROM transactions
)
SELECT *
FROM t
WHERE rn <= 3;
```

### 2. CTE (Common Table Expression)

**CTE là gì?**
```sql
WITH sales AS (
   SELECT *
   FROM orders
)
SELECT *
FROM sales;
```

**CTE vs Subquery**
* **CTE:** Dễ đọc, Tái sử dụng, Hỗ trợ Recursive.
* **Subquery:** Phù hợp logic đơn giản.

**Recursive CTE:** Oracle/Postgres đều hỗ trợ. Dùng để xử lý dữ liệu dạng cây (ví dụ cây nhân viên: CEO -> Manager -> Staff).

### 3. EXISTS vs IN (Hỏi cực nhiều)

**IN**
```sql
SELECT *
FROM employee
WHERE dept_id IN (
   SELECT dept_id
   FROM department
);
```

**EXISTS**
```sql
SELECT *
FROM employee e
WHERE EXISTS (
   SELECT 1
   FROM department d
   WHERE d.dept_id=e.dept_id
);
```
**Khi nào dùng EXISTS:** Dataset lớn. EXISTS dừng ngay khi tìm thấy bản ghi đầu tiên, do đó thường chạy nhanh hơn IN.

### 4. Correlated Subquery

Ví dụ:
```sql
SELECT *
FROM employee e
WHERE salary >
(
   SELECT AVG(salary)
   FROM employee
   WHERE department_id=e.department_id
);
```
**Vì sao correlated subquery thường chậm?** Do subquery được thực hiện nhiều lần (chạy tương ứng cho mỗi dòng của bảng ngoài).

### 5. ACID (Rất hay hỏi)
* **A – Atomicity:** (Tính nguyên tử) Tất cả thao tác thành công hoặc rollback toàn bộ.
* **C – Consistency:** (Tính nhất quán) Data luôn hợp lệ trước và sau transaction.
* **I – Isolation:** (Tính cô lập) Các transaction chạy đồng thời không ảnh hưởng nhau.
* **D – Durability:** (Tính bền vững) Commit xong thì mất điện vẫn không mất dữ liệu.

### 6. Isolation Level (Middle Data Engineer rất hay bị hỏi)
* **Read Uncommitted:** Có nguy cơ Dirty Read.
* **Read Committed:** Mức độ mặc định của Oracle.
* **Repeatable Read:** Ngăn tình trạng Non-repeatable Read.
* **Serializable:** Mức độ bảo vệ mạnh nhất, nhưng chạy chậm nhất.

### 7. Deadlock
**Deadlock là gì?**
Transaction A lock row 1, wait row 2. Transaction B lock row 2, wait row 1. => Dẫn đến Deadlock.
**Cách xử lý:** Thực hiện lock theo cùng thứ tự, giữ transaction ngắn nhất có thể, cài đặt cơ chế Retry mechanism.

### 8. Normalization (Chuẩn hoá dữ liệu)
* **1NF:** Không có giá trị lặp (các giá trị mang tính nguyên tử).
* **2NF:** Đạt 1NF và không có thuộc tính nào phụ thuộc một phần vào khóa chính.
* **3NF:** Đạt 2NF và không có phụ thuộc bắc cầu.
* **Khi nào Denormalization (Phi chuẩn hoá)?** Thường áp dụng trong Data Warehouse, mô hình Star Schema, bảng Fact/Dimension.

### 9. Data Warehouse (Chắc chắn hỏi Data Engineer)
**OLTP vs OLAP**
| | OLTP | OLAP |
|---|---|---|
| Đặc trưng | Transaction | Analytics |
| Thao tác | Insert/Update nhiều | Read nhiều |
| Cấu trúc | Chuẩn hóa cao | Phi chuẩn hóa |

* **Fact Table:** Bảng chứa các con số đo lường thực tế (VD: `sales_fact`).
* **Dimension:** Bảng chứa thông tin mô tả chi tiết (VD: `customer_dim`, `product_dim`, `date_dim`).
* **Star Schema:** Bảng Fact nằm ở giữa, liên kết trực tiếp với các bảng Dimension xung quanh.

### 10. ETL vs ELT
* **ETL:** Source -> Transform -> Warehouse
* **ELT:** Source -> Warehouse -> Transform (Các nền tảng như Databricks sử dụng ELT rất nhiều).

### 11. Incremental Load
* **Full Load:** Load lại toàn bộ (ví dụ 100 triệu records).
* **Incremental:** Chỉ load phần dữ liệu mới thay đổi (VD: `WHERE updated_at > :last_run_time`).

### 12. CDC (Change Data Capture)
**CDC là gì?** Là kỹ thuật theo dõi các sự kiện INSERT, UPDATE, DELETE trực tiếp từ transaction log.
* **Oracle:** Sử dụng LogMiner, GoldenGate.
* **PostgreSQL:** Sử dụng WAL, Debezium.

### 13. Index nâng cao
* **Clustered Index:** Dữ liệu vật lý được sắp xếp theo index. Mỗi bảng chỉ có tối đa 1 (VD: SQL Server).
* **Non Clustered:** Index lưu trữ cấu trúc riêng biệt. Một bảng có thể có nhiều cái.
* **Covering Index:** Index chứa đủ tất cả các cột cần cho truy vấn, do đó không cần tra ngược lại bảng chính (VD: select name, email -> index trên (id, name, email)).

### 14. Partition Pruning (Data Engineer cực thích hỏi)
Ví dụ: Bảng Partition theo tháng.
Khi chạy query `WHERE order_date='2026-06-01'`, Database chỉ đọc duy nhất partition của tháng 6, thay vì quét toàn bộ bảng.

### 15. Thực chiến Tuning
> **Câu hỏi:** Query chạy 30 giây. Em xử lý thế nào?

**Trả lời chuẩn:**
* **B1:** Xem Execution Plan.
* **B2:** Tìm các yếu tố gây chậm: Full Table Scan, Sort, Hash Join, Nested Loop.
* **B3:** Kiểm tra các nguyên nhân: Missing Index, Wrong Join, Data Skew (Lệch dữ liệu).
* **B4:** Rewrite lại cấu trúc câu SQL.
* **B5:** Đề xuất đánh Partition nếu dữ liệu quá lớn.
* **B6:** Cân nhắc tạo Materialized View.

### 16. Nhóm câu hỏi rất hay gặp với CV có Kafka/Airflow/Databricks/PostgreSQL
Do tính chất tech stack, bạn có thể được hỏi thêm:
1. WAL (Write-Ahead Logging) là gì?
2. CDC hoạt động thế nào?
3. Kafka offset commit khi nào?
4. So sánh At-most-once / At-least-once / Exactly-once?
5. Delta Lake MERGE INTO hoạt động thế nào?
6. SCD (Slowly Changing Dimension) Type 1/2 khác nhau ra sao?
7. Cấu trúc dữ liệu Bronze-Silver-Gold (Medallion Architecture)?
8. Đề xuất Partition strategy cho bảng 500 triệu records?
9. Vì sao query đã có index nhưng không dùng index?
10. Explain Plan đọc như thế nào?
11. Phân biệt Hash Join vs Nested Loop Join?
12. Nếu PostgreSQL CPU lên 100% thì các bước debug ra sao?

# Database (Oracle & Tối ưu SQL)
Phần này là trọng tâm của dự án, nhà tuyển dụng sẽ xoáy rất sâu vào khả năng Tối ưu (Tuning) của bạn.

**1. Các thành phần cơ bản của Oracle Database**
- **Instance**: Cấu trúc bộ nhớ (SGA - System Global Area) và các tiến trình chạy ngầm (Background processes) quản lý database.
- **Database**: Các file vật lý lưu trữ dữ liệu ổ cứng (Data files, Control files, Redo log files).
- *Điểm nhấn:* Oracle nổi tiếng với ngôn ngữ PL/SQL cực mạnh và kiến trúc Multi-tenant (quản lý nhiều DB con trong 1 DB lớn).

**2. Khái niệm Index, Ưu/Nhược điểm và Các loại Index**
- **Khái niệm**: Index giống như phần "Mục lục" của cuốn sách. Nó là một cấu trúc dữ liệu (thường là B-Tree) giúp Database tìm kiếm các dòng dữ liệu cực nhanh mà không phải quét toàn bộ bảng (Full Table Scan).
- **Ưu điểm**: Tăng tốc độ truy vấn `SELECT` (đặc biệt các mệnh đề `WHERE`, `JOIN`, `ORDER BY`). Giảm thiểu I/O đọc ổ cứng.
- **Nhược điểm**: Tốn dung lượng ổ cứng để lưu trữ cấu trúc Index. Làm chậm tốc độ Ghi (`INSERT`, `UPDATE`, `DELETE`) vì CSDL phải tốn công cập nhật lại "mục lục" mỗi khi dữ liệu thay đổi.
- **Các loại Index hay bị hỏi trong Oracle**:
  - *B-Tree Index*: Mặc định, dùng cho cột có độ phân tán cao (nhiều giá trị khác nhau, vd: ID, Email).
  - *Bitmap Index*: Đặc sản của Oracle, dùng cho cột có ít giá trị phân biệt (vd: Giới tính, Trạng thái). Rất nhanh cho việc Filter nhưng nhược điểm chí mạng là dễ gây khóa (Lock) nhiều dòng khi Update.
  - *Function-based Index*: Đánh index dựa trên kết quả của một hàm (vd: `UPPER(name)`).

**3. So sánh 2 loại Join phổ biến nhất (INNER JOIN vs LEFT JOIN)**
- **INNER JOIN**: Trả về các dòng **khớp nhau hoàn toàn** ở cả 2 bảng. Nếu không khớp, dòng đó bị loại bỏ. Dùng khi bạn cần dữ liệu hợp lệ ở cả 2 phía.
- **LEFT JOIN**: Giữ lại **toàn bộ** các dòng ở bảng bên Trái, nếu bảng bên Phải không có dữ liệu khớp, nó sẽ điền `NULL`. Dùng khi bạn không muốn bị mất dữ liệu của bảng gốc.

**4. Sự khác biệt giữa Stored Procedure và Function**
- **Giống nhau**: Đều là các đoạn code (PL/SQL) được biên dịch sẵn và lưu trong Database để tái sử dụng, giúp giảm tải băng thông mạng.
- **Khác nhau cốt lõi**:
  - *Function*: **Bắt buộc** phải có `RETURN` trả về 1 giá trị. Có thể gọi trực tiếp bên trong câu lệnh `SELECT` (vd: `SELECT get_total() FROM DUAL;`).
  - *Procedure*: Không bắt buộc trả về (thường dùng tham số `OUT`). Không thể gọi trong câu `SELECT`, mà thường được kích hoạt bởi Backend hoặc lệnh `EXECUTE`. Dùng để thực thi logic phức tạp (Update hàng loạt, Batch Job).

**5. Kỹ thuật Tuning (Tối ưu hóa Database)**
Khi hệ thống bị chậm, tôi thường tiếp cận theo các bước sau:
- **Phân tích bằng Execution Plan**: Dùng lệnh `EXPLAIN PLAN` để xem CSDL đang chạy câu query bằng đường nào (Đang xài Index hay bị lỗi quét toàn bộ bảng - Full Table Scan).
- **Tối ưu hóa ở mức viết SQL (Viết query chuẩn)**:
  - Bỏ ngay thói quen `SELECT *`, chỉ Select các cột thực sự cần dùng.
  - Tránh dùng Hàm (Function) lên cột được đánh Index trong mệnh đề `WHERE`. (Vd: `WHERE YEAR(created_at) = 2023` sẽ vô hiệu hóa Index của cột `created_at`).
  - Không dùng `%` ở đầu câu `LIKE` (`LIKE '%abc'`), vì Index không thể dò từ ngược lên.
  - Ưu tiên dùng `EXISTS` thay vì `IN` khi làm việc với subquery có tập dữ liệu khổng lồ.
- **Tối ưu hóa ở mức Cấu trúc**: Kiểm tra xem Index đã đánh đúng cột hay tìm kiếm chưa. Nếu bảng quá khổng lồ (vài chục triệu dòng), tôi sẽ đề xuất phân vùng bảng (**Partitioning**) theo thời gian (Tháng/Năm) để cô lập phạm vi tìm kiếm.

# SQL
**1. Group By & Having**
- **Group By**: Dùng để nhóm các giá trị giống nhau, thường dùng với count, sum, avg, min, max. Khi group by, tất cả các cột trong select phải có trong group by.
- **Having**: lọc các giá trị của group by.
- **Where và having khác gì nhau?**
  - Where: lọc các row trong bảng gốc, thực hiện **trước** khi group.
  - Having: lọc các nhóm, thực hiện **sau** khi group.

**2. Union / Intersect / Except**
- **Dùng để làm gì?** Để kết hợp kết quả của 2 hoặc nhiều câu truy vấn SELECT. Điều kiện: Số lượng cột và kiểu dữ liệu của các bảng phải giống nhau.
- **Các loại:**
  - `UNION`: Kết hợp các kết quả từ nhiều truy vấn, **loại bỏ** các bản ghi trùng lặp.
  - `UNION ALL`: Tương tự union, nhưng **không bỏ** các bản ghi trùng lặp.
  - `INTERSECT`: Trả về các bản ghi giống nhau trong cả 2 bảng.
  - `EXCEPT` (hoặc `MINUS` trong Oracle): Trả về các bản ghi có trong truy vấn đầu tiên mà không có trong truy vấn thứ 2.

**3. View (Bảng ảo)**
- **Dùng để làm gì?** Để tạo 1 bảng ảo, nó lưu trữ câu truy vấn chứ không lưu dữ liệu thực tế.
- **Khi update vào bảng gốc, query từ view ra có dữ liệu mới không?** => **Có**, vì view lưu câu truy vấn chứ không lưu dữ liệu thực tế.
- **Vì sao phải dùng View?**
  - Đơn giản hoá truy vấn (Tạo 1 view gom các câu select, join, where phức tạp...).
  - Giới hạn truy cập (Cho phép truy cập vào 1 view chứa các cột an toàn thay vì bảng gốc chứa dữ liệu nhạy cảm).
  - Cải thiện hiệu suất (Một số CSDL có thể tạo *Materialized views* để lưu kết quả truy vấn).
- **Có update, delete được dữ liệu của bảng gốc thông qua View không?** => **Có**, nếu view đó dựa trên 1 bảng duy nhất và không chứa các toán tử phức tạp như join, group by.

**4. Procedure (Thủ tục)**
- **Dùng để làm gì?** Để thực hiện 1 loạt các câu SQL một cách có tổ chức và hiệu quả. Nó được lưu trữ trong CSDL, khi cần sử dụng thì chỉ cần gọi procedure mà không cần viết lại tất cả các câu SQL.
- **Ví dụ:** Lệnh tự động tính toán và Update lương của tất cả nhân viên có thâm niên hơn 1 năm.


# Các câu hỏi phỏng vấn nâng cao (Oracle & PL/SQL)

**1. Execution Plan trong PL/SQL là gì? Giải thích nó? Có làm được không?**
- **Giải thích:** Execution Plan là "bản đồ" cho thấy cách Oracle Engine thực thi một câu lệnh SQL. Nó phân tích đường đi của dữ liệu (quét toàn bộ bảng hay quét qua Index), cách các bảng được Join với nhau (Hash Join, Nested Loops), và chi phí (Cost) của từng bước.
- **Cách làm:** Hoàn toàn làm được. Trong Oracle, tôi sử dụng lệnh `EXPLAIN PLAN FOR <câu_sql>;` sau đó chạy `SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);` để xem kế hoạch chi tiết.

**2. Điều quan trọng nhất để duy trì tốc độ trong PL/SQL là gì?**
- **Sử dụng BULK COLLECT và FORALL:** Thay vì lặp qua từng dòng (Context Switch giữa SQL và PL/SQL engine gây chậm), hãy gom dữ liệu thành từng mảng lớn để xử lý một lần.
- Giảm thiểu gọi các Function tự viết trong mệnh đề `SELECT` hay `WHERE` của các vòng lặp.

**3. Có các loại Join nào, giải thích khác nhau?**
- **INNER JOIN**: Lấy các dòng chung của 2 bảng.
- **LEFT / RIGHT JOIN**: Giữ lại toàn bộ bảng trái/phải, bảng còn lại không có thì điền NULL.
- **FULL OUTER JOIN**: Giữ lại toàn bộ dữ liệu của cả 2 bảng.
- **CROSS JOIN**: Tích Đề-các, ghép mọi dòng của bảng A với mọi dòng của bảng B (ít dùng thực tế).
- **SELF JOIN**: Bảng tự join với chính nó (vd: tìm Quản lý của Nhân viên trong cùng 1 bảng).

**4. Đã từng làm DB nào, tạo Query/Thiết kế DB được không?**
- *Gợi ý trả lời:* "Tôi làm nhiều với Oracle và PostgreSQL. Tôi hoàn toàn tự tin vào khả năng viết Query phức tạp (sử dụng CTE, Window Functions). Về thiết kế DB, tôi nắm vững các quy tắc chuẩn hóa (Normalization 1NF, 2NF, 3NF) để tránh dư thừa dữ liệu, nhưng cũng biết lúc nào cần phi chuẩn hóa (Denormalization) hoặc Partitioning bảng để tối ưu tốc độ đọc."

**5. Tuning thì cần làm gì, các giải pháp để tuning?**
- Đọc Execution Plan để tìm "nút thắt cổ chai" (bottleneck).
- Đánh Index đúng loại (B-Tree, Bitmap, Function-based). Tránh đánh Index thừa gây chậm lúc `INSERT`/`UPDATE`.
- Dùng `EXISTS` thay vì `IN` với tập dữ liệu con lớn.
- Viết lại câu SQL (Tránh `SELECT *`, tránh hàm trong `WHERE`).
- Phân vùng (Partitioning) các bảng khổng lồ theo ngày/tháng để giới hạn vùng tìm kiếm.

**6. Đã từng làm query với độ phức tạp nào, tốc độ khoảng nào với bao nhiêu bản ghi?**
- *Gợi ý trả lời:* "Tôi từng viết các script PL/SQL tổng hợp dữ liệu giao dịch cuối ngày (batch processing). Truy vấn liên quan đến việc join 5-6 bảng lớn (khoảng 10-20 triệu bản ghi mỗi bảng). Sau khi áp dụng Bulk Collect và đánh lại Index, tốc độ xử lý giảm từ 30 phút xuống còn dưới 2 phút."

**7. Kinh nghiệm làm việc với MyBatis?**
- MyBatis là một ORM (Object-Relational Mapping) framework cho Java. Khác với Hibernate (tự động gen SQL), MyBatis cho phép Developer viết câu lệnh SQL thuần (Native SQL) trực tiếp vào file XML. Rất phù hợp cho các dự án cần Tuning SQL thủ công đến từng chi tiết như Oracle.

**8. SQL Injection là gì?**
- Là lỗ hổng bảo mật khi Hacker chèn (inject) các đoạn mã SQL độc hại vào input của người dùng để can thiệp vào Database (ví dụ nhập `' OR '1'='1` vào ô đăng nhập).
- **Cách phòng chống:** Luôn sử dụng Parameterized Queries (Truy vấn có tham số - vd: `PreparedStatement` trong Java, hoặc bind variable trong PL/SQL). Tuyệt đối không nối chuỗi (concatenate string) trực tiếp để tạo câu SQL.

**9. Quản lý chu kỳ Index (Index Lifecycle Management)?**
- Khi dữ liệu thường xuyên bị `UPDATE` hoặc `DELETE`, cấu trúc cây B-Tree của Index sẽ bị phân mảnh (fragmentation), làm giảm tốc độ tìm kiếm và lãng phí dung lượng (tablespace).
- **Cách xử lý:** Theo dõi chỉ số fragmentation. Nếu vượt ngưỡng tối ưu (thường > 20%) và lượng index lưu trữ trong tablespace quá lớn, ta cần Rebuild lại index (lệnh `ALTER INDEX ... REBUILD`).

**10. Đã từng làm cái CLOB (Character Large Object) trong Oracle hay chưa?**
- CLOB dùng để lưu trữ các đoạn văn bản (Text) có kích thước khổng lồ (lên tới 4GB), ví dụ như lưu nội dung bài viết, file XML/JSON.
- *Lưu ý:* Không thể thao tác CLOB bằng các hàm String thông thường một cách thoải mái, mà phải dùng thư viện `DBMS_LOB` (như `DBMS_LOB.SUBSTR`, `DBMS_LOB.GETLENGTH`) để xử lý.


# III. CÁC KIẾN THỨC BỔ SUNG QUAN TRỌNG (Rà soát theo bộ câu hỏi tổng hợp)

Dựa trên danh sách câu hỏi tổng hợp, dưới đây là những phần kiến thức còn thiếu hoặc cần phân tích sâu hơn để bạn có bộ tài liệu "vô khuyết":

### 1. Transaction (Giao dịch)
- **Mục đích:** Bảo toàn tính toàn vẹn dữ liệu (Nguyên tắc ACID). Nếu một chuỗi thao tác có 1 bước lỗi, toàn bộ sẽ bị hủy (`ROLLBACK`), đảm bảo "tất cả cùng đúng, hoặc tất cả cùng sai".
- **Lưu ý:** Không thể `ROLLBACK` khi đã gọi lệnh `COMMIT`, dù nằm trong 1 transaction.
- **Câu hỏi: Có cách nào commit 1 phần transaction không?**
  => **Có**. Ta dùng `SAVEPOINT` để đánh dấu các mốc lưu tạm thời. Nếu có lỗi xảy ra, ta chỉ cần rollback về đúng `SAVEPOINT` đó thay vì hủy toàn bộ transaction.

### 2. Các phép JOIN (Bổ sung)
- **RIGHT JOIN:** Lấy toàn bộ dữ liệu bảng Phải, bảng Trái không có thì điền NULL.
- **FULL JOIN:** Lấy toàn bộ dữ liệu của cả 2 bảng, nếu không có sự khớp, giá trị sẽ trả về NULL.
- **CROSS JOIN:** Tích Đề-các. Ghép mọi dòng bảng A với mọi dòng bảng B (Cực kỳ tốn tài nguyên, thực tế ít dùng).
- **SELF JOIN:** Bảng kết hợp với chính nó (Thường dùng để so sánh các hàng trong cùng một bảng, VD: So sánh lương nhân viên với người quản lý của họ trong cùng bảng Employee).

### 3. Đào sâu về Composite Index và Phân vùng (Partition)
- **Composite Index (Index đa cột):** Khi đánh index trên nhiều cột (VD: a, b, c), **bắt buộc** phải truy vấn đúng thứ tự từ trái sang phải.
  - *Đúng:* `WHERE a = x AND b = y AND c = z` (hoặc chỉ có `a`, hoặc `a và b`).
  - *Sai:* `WHERE b = x AND c = z` (Vì thiếu `a` đứng đầu, Index sẽ bị vô hiệu hóa toàn bộ).
- **Các loại Partition (Phân vùng):** Chia bảng/index khổng lồ thành các cục nhỏ dễ quản lý.
  - *Range:* Chia theo khoảng giá trị (VD: Phân vùng theo Năm/Tháng).
  - *List:* Chia theo danh sách cụ thể (VD: VN, USA, JPN).
  - *Hash:* Phân tán dữ liệu đều bằng hàm băm (Dùng khi không có cột Range/List rõ ràng).
  - *Key:* Tương tự Hash nhưng dựa trên một khóa duy nhất.
- **Index vs Partition?**
  - Dùng **Index** khi muốn tìm một lượng dữ liệu nhỏ (dưới 15%) trong bảng lớn.
  - Dùng **Partition** khi truy vấn thường xuyên quét qua một mảng dữ liệu cực lớn nhưng có tính quy luật (ví dụ: Tính báo cáo cho tháng hiện tại), quét Index vẫn sẽ chậm.

### 4. Thứ tự thực thi của một câu lệnh SELECT
Dù viết chữ `SELECT` ở đầu, nhưng Database sẽ chạy theo thứ tự sau:
**FROM** -> **ON** -> **JOIN** -> **WHERE** -> **GROUP BY** -> **HAVING** -> **SELECT** -> **DISTINCT** -> **ORDER BY** -> **LIMIT**.

### 5. Web API & Bảo mật (Nếu bị hỏi vòng quanh)
- **GET vs POST:** `GET` truyền dữ liệu qua URL (giới hạn độ dài, kém bảo mật), dùng để Đọc. `POST` truyền qua Body (ẩn, không giới hạn độ dài), dùng để Tạo mới.
- **Tối ưu RESTful API:** 1. Đánh Caching (Redis). 2. Phân trang dữ liệu. 3. Nén dữ liệu trả về. 4. Đẩy tác vụ nặng xuống Background Job (Message Queue).
- **Authen/Author:** 
  - *Authen (Xác thực):* Kiểm tra danh tính (Đăng nhập bằng JWT Token/OAuth2).
  - *Author (Phân quyền):* Kiểm tra xem user đó có quyền làm hành động này không (Role Admin/User).

### 6. Java, JPA vs Hibernate
- **Khác biệt:** JPA chỉ là tập hợp các bộ quy tắc (Interfaces) do Java định nghĩa. Hibernate là công cụ thực thi (Implementation) các quy tắc đó.
- **Quan hệ N-N:** Dùng bảng trung gian và đánh annotation `@ManyToMany`.
- **Truy vấn cực phức tạp làm sao?** Nếu dùng Hibernate bị chậm, tôi sẽ chuyển sang dùng **Native Query** (viết SQL thuần), hoặc dùng công cụ như **MyBatis / jOOQ** để tối ưu tốc độ trực tiếp trên SQL.

### 7. Giải đáp bài tập SQL thực hành hóc búa
- **Top học sinh có điểm cao nhất:** 
  Sử dụng hàm cửa sổ `DENSE_RANK() OVER(ORDER BY score DESC)` thay vì `LIMIT`, vì `DENSE_RANK` sẽ lấy chuẩn tất cả học sinh bị đồng điểm ở Top 1.
- **Loại bỏ bản ghi trùng lặp:** Dùng từ khóa `DISTINCT` sau `SELECT`, hoặc dùng `GROUP BY` tất cả các cột.
- **Tối ưu câu lệnh sau:** `SELECT * FROM A JOIN B ON A.Column = B.Column WHERE A.Column_1 NOT IN ('X', 'Z') AND B.Column_2 = 'Y';`
  => **Cách tối ưu & Đánh Index:** Không nên đánh Index vào `A.Column_1` vì nó dùng toán tử `NOT IN` (phủ định, rẽ nhánh quá nhiều nên CSDL thường bỏ qua Index). 
  **Nên đánh Index vào:** 
  1. `B.Column_2` (Vì điều kiện so sánh `=` là mạnh nhất để lọc dữ liệu).
  2. Các cột Join là `A.Column` và `B.Column`.




- Where và having khác gì nhau?
Where: lọc các row trong bảng gốc, thực hiện trước khi group
Having: lọc các nhóm, thực hiện sau khi group
Union

- Dùng để làm gì?
+ để kết hợp kết quả của 2 hoặc nhiều câu truy vấn select
- Số lượng cột và kiểu dữ liệu của 2 bảng phải giống nhau
- Có 2 loại union
+ Union:
kết hợp các kết quả từ nhiều truy vấn, loại bỏ các bản ghi trùng
+ Union all:
tương tự union, nhưng không bỏ các bản ghi trùng lặp
+ INTERSECT
trả về các bản ghi giống nhau trong cả 2 bảng
+ EXCEPT
trả về các bản ghi có trng truy vấn đầu tiên mà không có trong truy vấn thứ 2
View:
- Dùng để làm gì?
+ để tạo 1 bảng ảo, nó lưu trữ dữ liệu truy vấn chứ không lưu dữ liệu thực tế
- Khi update vào bảng gốc, sau đó query từ view ra, view có dữ liệu mới được update không?
=> Có vì view lưu dữ liệu truy vấn chứ không lưu dữ liệu thực tế
- Vì sao phải dùng view?
+ đơn giản hoá truy vấn (Tạo 1 view gồm các câu select, join, where...)
+ Giới hạn truy cập (cho phép truy cập vào 1 view thay vì bảng gốc)
+ cải thiện hiệu xuất (1 số csdl có thể tạo materialized views để lưu kết quả truy vấn)

-> Có update, delete được dữ liệu của bảng gốc thông qua view không?
=> Có nếu view dựa trên 1 bảng duy nhất và không chứa các toán tử join, group by
Procedure:
- Dùng để làm gì?
+ để thực hiện 1 loạt các câu sql một cách có tổ chức và hiệu quả, nó được lưu trữ trong csdl, khi cần sử dụng thì chỉ cần gọi procedure mà không cần viết lại tất cả câu sql
Ví dụ:
 Update lương của tất cả nhân viên có thâm niên hơn 1 năm
 => Thay vì ở dưới Backend sẽ lấy tất cả thông tin nhân viên có thâm niên hơn 1 năm, sau đó sẽ gọi câu lệnh sql để update => Gọi nhiều lần vào DB
 => Viết 1 store procedure để lấy tất cả nhân viên có thâm niên hơn 1 năm và update => Chỉ gọi 1 store procedure, nó sẽ sử lý trên DB

- Ưu điểm: 
+ Hiệu suất cao, giảm tải gọi DB, Tái sử dụng, khi thay đổi logic, không cần deploy lại server...
- Nhược điểm
+ Khó bảo trì
+ Phụ thuộc vào logic của store procedure, gây khó khăn khi thay đổi nghiệp vụ
Function
- Dùng để làm gì?
+ để thực hiện 1 tác vụ cụ thể và trả về 1 giá trị
+ function bắt buộc phải trả về 1 giá trị
Ví dụ: 1 bảng A gồm username, role (1,2) nếu là 1 thì Trả về ADMIN, 2 thì USER
=> Viết 1 function CHECK_ROLE nếu truyền vào là 1 thì return ADMIN, 2 return USER
=> Select u.username , CHECK_ROLE(u.role) from user u;
Function và procedure khác gì nhau?
=> Function bắt buộc phải trả về, procedure có thể trả về hoặc không
=> Có thể sử dụng function trong câu select, procedure thì không
=> Function không được phép Update, Delete, Insert dữ liệu, procedure thì có thể
Transaction
- Dùng để làm gì?
+ để bảo toàn dữ liệu (tất cả đúng => đúng, 1 phần sau => tất cả sai)
- không thể rollback khi đã gọi lệnh commit, dù có nằm trong 1 transaction
Join
- Dùng để làm gì?
+ để kết hợp giữa 2 hoặc nhiều bảng dựa trên mối quan hệ giữa chúng
- Inner Join
=> Chỉ trả về các bản ghi có sự khớp giữa 2 bảng
- LEFT JOIN (Hoặc LEFT OUTER JOIN)
=> trả về tất cả các bản ghi từ bảng bên trái và các bản ghi từ bảng bên phải, nếu không khớp, nó sẽ trả về null
- RIGHT JOIN (Hoặc RIGHT OUTER JOIN)
=> trả về tất cả các bản ghi từ bảng bên phải và các bản ghi từ bảng bên trái, nếu không khớp, nó sẽ trả về null
- FULL JOIN (Hoặc FULL OUTER JOIN)
=> trả về tất cả các bản ghi từ 2 bảng, nếu không có sự khợp, giá trị sẽ null
- CROSS JOIN
=> Trả về tích của hai bảng, tức là tất cả các kết hợp có thể của các bản ghi từ hai bảng. Điều này có thể tạo ra một số lượng lớn các bản ghi trong kết quả
- SELF JOIN
=> Là một loại join mà trong đó một bảng được kết hợp với chính nó. Nó thường được sử dụng để so sánh các hàng trong cùng một bảng.
Index
- Dùng để làm gì?
=> Tăng tốc độ truy vấn
- Tiêu chí đánh index
+ Cột thường truy vấn trong điều kiện where, join, order, group
+ Tần suất cập nhật ít

- Nhược điểm:
+ Tăng chi phí lưu trữ
+ Giảm tốc độ cập nhật

Lưu ý: không sử dụng like với % ở đầu khi query index, khi này index sẽ không được dùng (ví dụ like '%abc') vì index lưu theo dạng bTree nên việc sử dụng like % ở đầu sẽ không áp dùng được
Composite Index
- đánh index 2 hoặc nhiều cột, giúp cải thiện truy vấn khi có đk filter hoặc sort trên nhiều cột
Lưu ý: khi sử dụng Composite Index, phải truy vấn đúng theo thứ tự từ trái sang phải
Ví dụ: đánh index vào cột a,b,c khi truy vấn điều kiện phải truy vấn theo where a = xxx and b=xxx and c=xxx
hoặc a=xxx and b=xxx
hoặc a=xxx
nếu truy vấn a=xxx and c=xxx hoặc b=xxx c=xxx thì Composite Index sẽ không được áp dụng
Partition
- chia nhỏ bảng hoặc index thành các phần nhỏ hơn
- có 4 loại:
+ Range Partitioning: chia theo khoảng giá trị (ngày, năm...)
+ List Partitioning: chia theo danh sách (VN, USA...)
+ Hash Partitioning: chia theo 1 hàm băm, giúp phân tán dữ liệu giữa các vùng (khi truy vấn, nó sẽ sử dụng hàm băm để xác định nó thuộc partition nào)
+ Key Partitioning: Tương tự như hash partitioning, nhưng sử dụng một khóa duy nhất để phân vùng dữ liệu



Innovation Book
 
Quesstion
 
transaction là gì, vid dụ thực tế hỏi có cách nào commit 1 phần transaction không
 
viết câu truy vấn truy vấn top học sinh số điểm cao nhất
 
ví dụ thực tế leftjoin, inner join
 
loại bỏ các bản ghi trùng lặp khi truy vấn làm thế nào  
 
So sánh phương thức POST, GET khác biệt gì trong code 
 
So sánh Store Procedure & Function
 
Các cách để tăng performance trong câu lệnh truy vấn
 
SELECT * FROM A JOIN B ON A.Column = B.Column WHERE A.Column_1 NOT IN ('X', 'Z') AND B.Column_2 = 'Y';
 
Chỉ ra cách tăng hiệu suất của câu truy vấn trên? Nên đặt index vào cột nào?
 
Cách thể hiện mqh n-n giữa các entity sd Hibernate
 
Trong DB có các mqh nào giữa 2 table
 
  1. store produce vs function trong plsql
 
  2. trình bày công việc cụ thể làm về store prod
 
  => có thể trả lời là tự phát triển những store prod đơn   giản, mà chỉnh sửa theo yêu cầu của KH
 
  3. tuning trong plsql
 
  - đã có kinh nghiệm làm cái đó chưa
 
  - execution plans trong plsql, giải thích nó
 
  - execution plans trong plsql có làm đc ko
 
  - điều quan trọng nhất để duy trì tốc độ trong plsql là gì???
 
Có các loại join nào, giải thích khác nhau của các loại
 
Đã từng làm DB nào, tạo các query như thế nào, thiết kế db được không
 
Tuning thì cần làm gì, các giải pháp để tuning là gì
 
Đã từng làm query với độ phức tạp nào, tốc độ khoảng nào với bao nhiêu bản ghi
 
Kn làm việc with MyBatis
 
Sql injection?
 
quản lý chu kỳ trong index ntn
 
ã từng làm cái  CLOB (character large object) trong oracle hay chưa? gt nó?
 
Quản lý chu kỳ index (Index lifecyle management)?
 
=> Oracle index lifecycle khá đơn giả: chỉ là tunning khi mà chỉ số fragmentation lên vượt ngưỡng tối ưu và lượng index lưu trữ trong index tablespace qua lon
 
=> Làm giảm tốc độ truy vấn do lượng dữ liệu đã bị thay đổi và làm hổng index
 
=> Các bước thực hiện là chạy lệnh Index analyze 
Phân thích Select, Union,
 
Thứ tự chạy các thành phần trong 1 câu select?
 
 
Kinh nghiệm/ tư duy database? Khi nào cần thiết kế theo chuẩn hóa dữ liệu?
 
Kinh nghiệm tối ưu SQL?
 
Có các loại index nào?
 
Khi sử dung index thì đánh index ntn?
 
Trường hợp nào thì nên dùng index, trường hợp nào nên sử dung partition
 
Nếu như có 1 câu query phức tạp, không sử dụng Hibernate hay native query thì có cách nào để xử lí?
 
JPA với Hibernate khác gì nhau?
 
Làm thế nào để tối ưu RESTful API?
 
Em xử lí authen/author trong hệ thống ntn?



1. Câu hỏi thực tế về filter trong sql
2. thư viện pandas
3. 4 tính chất của OOP. lấy ví dụ code
4. Design Pattern, mô tả khái niệm + ví dụ (ít nhất 2 )
5. Double underscore function (3 cái)
6. ma trận 4x5 tìm số lớn thứ 2 của cột 3 và hàng 2 viết flow step by step
7. 100k user, tìm tên user duy nhất
8.sort list ngẫu nhiên
9. cân bi, 8 viên 2 lần cân 
10.