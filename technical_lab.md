1.
2.
3. 4 tính chất của OOP.

4 tính chất của OOP là câu hỏi phỏng vấn cực kỳ phổ biến. Thay vì học thuộc định nghĩa, hãy hiểu theo cách thực tế.

# 1. Encapsulation (Đóng gói)

## Ý tưởng

> Dữ liệu và hàm xử lý dữ liệu được gói chung vào một đối tượng.

Đồng thời che giấu những gì không muốn người khác truy cập trực tiếp.

Ví dụ tài khoản ngân hàng:

```python
class BankAccount:
    def __init__(self):
        self.__balance = 1000

    def deposit(self, amount):
        self.__balance += amount

    def get_balance(self):
        return self.__balance
```

Sử dụng:

```python
acc = BankAccount()

acc.deposit(500)

print(acc.get_balance())
```

Output:

```python
1500
```

Không thể:

```python
acc.__balance = 1000000
```

vì `__balance` đã được đóng gói.

---

## Thực tế

Ví dụ API Banking:

```python
account.withdraw(100)
```

Thay vì:

```python
account.balance -= 100
```

để tránh dữ liệu bị sửa linh tinh.

---

# 2. Inheritance (Kế thừa)

## Ý tưởng

> Class con tái sử dụng thuộc tính và phương thức của class cha.

Ví dụ:

```python
class Animal:
    def eat(self):
        print("Eating...")
```

Class con:

```python
class Dog(Animal):
    pass
```

Dùng:

```python
dog = Dog()

dog.eat()
```

Output:

```python
Eating...
```

---

## Thực tế

Ví dụ hệ thống nhân viên:

```python
Employee
├── Developer
├── Tester
└── Manager
```

Mọi nhân viên đều có:

```python
name
email
salary
```

không cần viết lại.

---

# 3. Polymorphism (Đa hình)

## Ý tưởng

> Cùng một hàm nhưng hành vi khác nhau.

Ví dụ:

```python
class Dog:
    def speak(self):
        print("Woof")


class Cat:
    def speak(self):
        print("Meow")
```

Sử dụng:

```python
animals = [Dog(), Cat()]

for animal in animals:
    animal.speak()
```

Output:

```python
Woof
Meow
```

Cùng gọi:

```python
animal.speak()
```

nhưng kết quả khác nhau.

---

## Thực tế

Ví dụ payment:

```python
payment.pay()
```

Có thể là:

```python
StripePayment.pay()
PaypalPayment.pay()
BankTransferPayment.pay()
```

Code gọi không cần biết loại thanh toán nào.

---

# 4. Abstraction (Trừu tượng)

## Ý tưởng

> Chỉ cho người dùng biết "làm gì", không cần biết "làm như thế nào".

Ví dụ:

Bạn lái xe:

```text
Nhấn ga -> xe chạy
Đạp phanh -> xe dừng
```

Bạn không cần biết:

```text
Piston
Trục khuỷu
Buồng đốt
```

hoạt động thế nào.

---

## Python

```python
from abc import ABC, abstractmethod


class Payment(ABC):

    @abstractmethod
    def pay(self, amount):
        pass
```

Implement:

```python
class StripePayment(Payment):

    def pay(self, amount):
        print(f"Pay {amount} via Stripe")
```

Dùng:

```python
payment = StripePayment()

payment.pay(100)
```

Output:

```python
Pay 100 via Stripe
```

Người dùng chỉ biết:

```python
payment.pay()
```

không cần biết bên trong gọi API Stripe ra sao.

---

# Ví dụ thực tế trong một hệ thống E-commerce

```python
from abc import ABC, abstractmethod


class Payment(ABC):              # Abstraction

    @abstractmethod
    def pay(self, amount):
        pass


class StripePayment(Payment):    # Inheritance

    def pay(self, amount):       # Polymorphism
        print(f"Stripe: {amount}")


class PaypalPayment(Payment):

    def pay(self, amount):
        print(f"Paypal: {amount}")


class Order:

    def __init__(self):
        self.__total = 100       # Encapsulation

    def checkout(self, payment):
        payment.pay(self.__total)
```

Sử dụng:

```python
order = Order()

order.checkout(StripePayment())
order.checkout(PaypalPayment())
```

---

## Cách nhớ nhanh khi đi phỏng vấn

| Tính chất     | Ý nghĩa đơn giản                          |
| ------------- | ----------------------------------------- |
| Encapsulation | Giấu dữ liệu, chỉ cho truy cập qua method |
| Inheritance   | Class con dùng lại code của class cha     |
| Polymorphism  | Cùng method, nhiều cách thực hiện         |
| Abstraction   | Chỉ lộ chức năng, giấu chi tiết bên trong |

Một câu trả lời phỏng vấn ngắn gọn:

> OOP có 4 tính chất chính: Encapsulation giúp bảo vệ dữ liệu bằng cách đóng gói thuộc tính và phương thức trong class; Inheritance giúp tái sử dụng code từ class cha; Polymorphism cho phép cùng một interface nhưng nhiều cách triển khai khác nhau; Abstraction giúp ẩn chi tiết cài đặt và chỉ cung cấp những chức năng cần thiết cho người dùng.

4. Design Pattern, mô tả khái niệm + ví dụ (ít nhất 2)

Đối với level **Python Middle**, interviewer thường không cần bạn thuộc lòng 23 Design Pattern của GoF. Họ muốn biết:

1. Design Pattern là gì.
2. Khi nào dùng.
3. Đã từng áp dụng thực tế chưa.

Một câu trả lời tốt khoảng 2-3 phút:

---

### Design Pattern là gì?

Design Pattern là các giải pháp thiết kế đã được kiểm chứng để giải quyết những vấn đề lặp đi lặp lại trong quá trình phát triển phần mềm.

Mục tiêu của Design Pattern là:

* Tăng khả năng tái sử dụng code.
* Giảm coupling giữa các module.
* Dễ mở rộng và bảo trì hệ thống.

Trong Python tôi thường gặp và sử dụng các pattern như Singleton, Factory, Strategy, Observer và Dependency Injection.

---

## Ví dụ 1: Singleton Pattern

### Khái niệm

Đảm bảo trong toàn bộ application chỉ tồn tại một instance của một class.

### Ví dụ thực tế

Trong dự án FastAPI hoặc Data Pipeline, tôi thường áp dụng Singleton cho:

* Redis Client
* Kafka Producer
* Database Connection Pool

Ví dụ Redis:

```python
class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

Khi gọi:

```python
r1 = RedisClient()
r2 = RedisClient()
```

thì:

```python
r1 is r2
```

sẽ trả về:

```python
True
```

=> Chỉ tạo một kết nối Redis duy nhất.

### Trade-off

* Tiết kiệm tài nguyên.
* Khó unit test nếu lạm dụng.

---

## Ví dụ 2: Strategy Pattern

### Khái niệm

Cho phép thay đổi thuật toán hoặc hành vi tại runtime mà không cần sửa code client.

### Ví dụ thực tế

Hệ thống thanh toán:

```python
class PaymentStrategy:
    def pay(self, amount):
        pass
```

Stripe:

```python
class StripePayment(PaymentStrategy):
    def pay(self, amount):
        print("Stripe Payment")
```

PayPal:

```python
class PaypalPayment(PaymentStrategy):
    def pay(self, amount):
        print("Paypal Payment")
```

Context:

```python
class Checkout:
    def __init__(self, strategy):
        self.strategy = strategy

    def checkout(self, amount):
        self.strategy.pay(amount)
```

Sử dụng:

```python
Checkout(StripePayment()).checkout(100)
Checkout(PaypalPayment()).checkout(100)
```

### Thực tế

Tôi thường áp dụng Strategy cho:

* Payment Gateway
* Authentication Provider
* Data Export (CSV, Excel, PDF)
* AI Model Selection (GPT, Claude, Gemini)

Ưu điểm:

* Tuân thủ Open/Closed Principle.
* Dễ thêm provider mới.

---

## Ví dụ 3: Dependency Injection (DI)

### Khái niệm

Thay vì class tự tạo ra (khởi tạo) các dependency (các object nó cần để hoạt động), ta sẽ truyền (inject) chúng từ bên ngoài vào. Điều này giúp giảm coupling (sự phụ thuộc), làm cho code linh hoạt và dễ test hơn.

### Ví dụ thực tế

Tưởng tượng một service cần gửi thông báo. Nếu không dùng DI:

```python
class EmailService:
    def send(self, message):
        print(f"Sending email: {message}")

class NotificationManager:
    def __init__(self):
        # Tự khởi tạo dependency bên trong -> Khó thay đổi, khó test (High coupling)
        self.email_service = EmailService()

    def notify(self, message):
        self.email_service.send(message)
```

Nếu dùng DI, ta truyền dependency vào qua constructor (Constructor Injection):

```python
class NotificationManager:
    def __init__(self, message_service):
        # Dependency được truyền từ ngoài vào (Low coupling)
        self.message_service = message_service

    def notify(self, message):
        self.message_service.send(message)
```

Sử dụng:

```python
email_service = EmailService()
manager = NotificationManager(email_service)
manager.notify("Hello DI!")
```

### Thực tế

Trong **FastAPI**, DI là một tính năng cốt lõi cực kì mạnh mẽ (thông qua `Depends`).
Tôi thường dùng DI để:

* Truyền (Inject) Database Session vào các endpoint (Router).
* Truyền Authentication/Authorization context (kiểm tra token người dùng).
* Truyền Configuration/Settings.

**Ưu điểm lớn nhất**:
* Cực kỳ dễ mock/fake data khi viết Unit Test (chỉ cần truyền một class Mock vào thay vì class thật).
* Các module hoạt động độc lập, dễ dàng thay đổi thành phần (ví dụ đổi từ `EmailService` sang `SMSService` mà class `NotificationManager` không cần thay đổi một dòng code nào).

---

## Liên hệ với kinh nghiệm của bạn

Nếu interviewer hỏi:

> Em đã dùng Design Pattern nào trong dự án thực tế chưa?

Bạn có thể trả lời:

> Trong dự án AI Slide Generation bằng FastAPI, tôi sử dụng Singleton cho Redis client để tránh tạo nhiều connection không cần thiết. Ngoài ra tôi áp dụng Strategy Pattern cho việc lựa chọn các AI provider và workflow khác nhau. Mỗi provider có cùng interface nhưng cách triển khai khác nhau, giúp hệ thống dễ mở rộng khi bổ sung model mới.

---

### Phiên bản trả lời ngắn gọn khi phỏng vấn

> Design Pattern là các mẫu thiết kế giúp giải quyết các vấn đề phổ biến trong phát triển phần mềm. Tôi thường sử dụng Singleton và Strategy Pattern. Singleton đảm bảo chỉ có một instance của một đối tượng như Redis hoặc Database Client trong toàn hệ thống. Strategy Pattern cho phép thay đổi thuật toán hoặc hành vi tại runtime, ví dụ như chuyển đổi giữa Stripe, PayPal hoặc các AI provider khác mà không cần sửa code nghiệp vụ chính. Điều này giúp hệ thống dễ mở rộng và bảo trì hơn.

5. Double underscore function (Dunder / Magic Methods) - 3 hàm phổ biến

Trong Python, các hàm bắt đầu và kết thúc bằng hai dấu gạch dưới `__` được gọi là **Dunder methods** (Double UNDERscore) hoặc **Magic methods**. Chúng cho phép class của bạn định nghĩa các hành vi "tích hợp sẵn" (built-in) của Python, ví dụ như cách khởi tạo, cách in ra màn hình, hay cách class tương tác với các toán tử (+, -, ==).

Dưới đây là 3 hàm thường được hỏi nhất, rất dễ hiểu và hay gặp trong thực tế:

---

## 1. `__init__(self)`: Hàm khởi tạo (Constructor)

### Khi nào dùng?
Được gọi tự động ngay sau khi một instance (đối tượng) mới của class được tạo ra. Dùng để khởi tạo các thuộc tính (dữ liệu ban đầu) cho đối tượng đó.

### Ví dụ:

```python
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

# Khi bạn tạo object, __init__ tự động chạy và truyền giá trị
user = User("john_doe", "john@example.com")
print(user.username)  # john_doe
```

---

## 2. `__str__(self)`: Định nghĩa cách hiển thị object (String Representation)

### Khi nào dùng?
Được gọi khi bạn dùng hàm `print()` hoặc `str()` lên một object. Mục đích là để trả về một chuỗi **dễ hiểu, thân thiện với con người** (đặc biệt khi ghi log).

*(Lưu ý: Python còn có `__repr__` dùng để hiển thị chuỗi mang tính chất debug cho Developer).*

### Ví dụ:

```python
class User:
    def __init__(self, username):
        self.username = username
    
    # Nếu không có __str__, print(user) sẽ ra chuỗi khó hiểu kiểu: <__main__.User object at 0x10b...>
    def __str__(self):
        return f"Tài khoản người dùng: {self.username}"

user = User("john_doe")
print(user)  # Output: Tài khoản người dùng: john_doe
```

---

## 3. `__call__(self)`: Biến object thành Callable (Gọi như một hàm)

### Khi nào dùng?
Cho phép một object (instance của class) có thể được gọi (thực thi) bằng dấu ngoặc tròn `()`, giống hệt như cách bạn gọi một function bình thường. Rất hữu ích khi bạn muốn một hàm có thể lưu lại trạng thái (state) qua nhiều lần gọi.

### Ví dụ:

```python
class RateLimiter:
    def __init__(self, limit):
        self.limit = limit
        self.count = 0

    def __call__(self):
        self.count += 1
        if self.count > self.limit:
            return "Too many requests!"
        return "Request passed."

# Khởi tạo object
limiter = RateLimiter(limit=2)

# Gọi object như một function nhờ có __call__
print(limiter())  # Request passed.
print(limiter())  # Request passed.
print(limiter())  # Too many requests!
```

---

### Mẹo trả lời phỏng vấn:

> "Dunder methods giúp class của Python tương tác trơn tru với các tính năng có sẵn của ngôn ngữ. Trong thực tế, em luôn dùng `__init__` để khởi tạo dữ liệu. Em hay dùng `__str__` để khi `print()` hoặc ghi file log, object in ra thông tin có ý nghĩa thay vì địa chỉ bộ nhớ. Ngoài ra, em từng dùng `__call__` để biến object thành một hàm có trạng thái, rất tiện khi viết Decorator dưới dạng class."

7. Có 100K tên user, thuật toán tìm danh sách tên khách hàng DUY NHẤT

Với yêu cầu lọc ra các tên "duy nhất" từ 100K dữ liệu, thuật toán tối ưu nhất là sử dụng **Hash Set (Tập hợp)**.

*   **Cách làm:** Duyệt qua danh sách 100K tên và đưa chúng vào một `Set`. Cấu trúc dữ liệu Set sử dụng Hash Table ở bên dưới, tự động loại bỏ các phần tử trùng lặp.
*   **Độ phức tạp thời gian (Time Complexity):** `O(N)` để duyệt qua 100K tên. Việc check/thêm vào Set tốn trung bình `O(1)` cho mỗi phần tử.
*   **Code Python:** `unique_users = list(set(users_list))`

*(Lưu ý: Nếu câu hỏi có nghĩa là tìm những người có tên CHỈ XUẤT HIỆN ĐÚNG 1 LẦN trong list (không bị trùng với ai), ta sẽ dùng **Hash Map / Dictionary** để đếm tần suất xuất hiện `O(N)`, sau đó lọc ra những tên có `count == 1`).*

---

8. Có 100K tên user, thuật toán search (tìm kiếm) tên khách hàng NHANH NHẤT

Để tìm kiếm cực nhanh trong 100K tên, cách tiếp cận phụ thuộc vào bài toán thực tế:

*   **Trường hợp 1: Tìm kiếm nhiều lần (Nhanh nhất - O(1)) -> Dùng Hash Table (Set/Dict)**
    *   **Cách làm:** Load 100K tên vào một `Set` (hoặc `Dict` nếu lưu thêm info).
    *   **Tại sao:** Tìm kiếm trong Hash Table tốn thời gian trung bình là **O(1)**. Trong Python chỉ cần dùng `if name in users_set:`. Tốn bộ nhớ nhưng tốc độ vô đối.
*   **Trường hợp 2: List đã được sắp xếp sẵn & cần tiết kiệm bộ nhớ -> Binary Search (O(log N))**
    *   **Cách làm:** Chặt đôi mảng liên tục để tìm tên. Với 100K user (~ $2^{17}$), ta chỉ mất tối đa **17 phép so sánh** để tìm ra kết quả. Rất tiết kiệm tài nguyên.
*   **Trường hợp 3: Tìm kiếm theo tiền tố (gõ "Nguy" gợi ý ra "Nguyễn") -> Dùng Trie (Prefix Tree)**
    *   Được dùng trong các thanh Autocomplete. Tốc độ tìm kiếm chỉ phụ thuộc vào độ dài chữ bạn gõ, hoàn toàn không phụ thuộc vào việc có 100K hay 1 triệu user.

---

9. Kể tên và giải thích 2-3 thuật toán Sort (sắp xếp) list ngẫu nhiên

Khi đi phỏng vấn, bạn nên nêu bật 3 thuật toán phổ biến và hiệu quả nhất (thường có độ phức tạp trung bình là `O(N log N)`):

**1. Quick Sort (Sắp xếp nhanh)**
*   **Nguyên lý (Divide & Conquer):** Chọn ngẫu nhiên một phần tử làm "trục" (pivot). Đưa các số nhỏ hơn pivot sang trái, lớn hơn sang phải. Đệ quy lặp lại quá trình này cho 2 mảng con.
*   **Ưu điểm:** Tốc độ thực tế rất nhanh, không tốn thêm bộ nhớ đệm (In-place).
*   **Nhược điểm:** Trường hợp xui xẻo nhất (chọn pivot quá tệ) tốc độ có thể rớt xuống `O(N^2)`.

**2. Merge Sort (Sắp xếp trộn)**
*   **Nguyên lý (Divide & Conquer):** Chia đôi mảng liên tục cho đến khi mỗi mảng chỉ còn 1 phần tử. Sau đó "trộn" (merge) 2 mảng nhỏ dần dần lại với nhau theo thứ tự tăng dần.
*   **Ưu điểm:** Tốc độ cực kỳ ổn định, luôn luôn là `O(N log N)` dù mảng ban đầu có lộn xộn cỡ nào.
*   **Nhược điểm:** Tốn thêm bộ nhớ `O(N)` để chứa mảng phụ trong quá trình trộn.

**3. Timsort (Thuật toán thực tế tối ưu nhất - Default của Python)**
*   **Nguyên lý:** Là sự kết hợp (hybrid) giữa **Merge Sort** và **Insertion Sort**. Timsort nhận ra rằng dữ liệu thực tế thường có sẵn những mảng con ngắn đã được sắp xếp (gọi là runs). Nó dùng Insertion Sort cho các mảng nhỏ và Merge Sort để gộp chúng lại.
*   **Ưu điểm:** Hàm `.sort()` và `sorted()` của Python đang sử dụng chính thuật toán này! Nêu được thuật toán này sẽ ghi điểm tuyệt đối với Interviewer.

---

### Python Code Implementation (Cho câu 7, 8, 9)

Dưới đây là code Python demo cho các thuật toán trên:

```python
import random
import string
import bisect
from collections import Counter

# ============================================================
# CÂU 7: Tìm danh sách tên user DUY NHẤT
# ============================================================
def q7_find_unique_names(users: list[str]) -> list[str]:
    """ Dùng Set -> O(N) time, O(N) space. """
    return list(set(users))

def q7_find_appear_once(users: list[str]) -> list[str]:
    """ Bonus: Tìm những tên CHỈ XUẤT HIỆN ĐÚNG 1 LẦN. """
    freq = Counter(users)
    return [name for name, count in freq.items() if count == 1]


# ============================================================
# CÂU 8: Tìm kiếm tên user NHANH NHẤT
# ============================================================

# --- Cách 1: Hash Table / Set -> O(1) lookup ---
class HashSearch:
    def __init__(self, users: list[str]):
        self.users_set = set(users)

    def search(self, name: str) -> bool:
        return name in self.users_set


# --- Cách 2: Binary Search -> O(log N) ---
class BinarySearch:
    def __init__(self, users: list[str]):
        self.sorted_users = sorted(set(users))  # sort một lần

    def search(self, name: str) -> bool:
        idx = bisect.bisect_left(self.sorted_users, name)
        return idx < len(self.sorted_users) and self.sorted_users[idx] == name


# --- Cách 3: Trie (Prefix Tree) -> O(L) lookup ---
class TrieNode:
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end

    def starts_with(self, prefix: str) -> list[str]:
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        results = []
        self._dfs(node, prefix, results)
        return results

    def _dfs(self, node: TrieNode, current: str, results: list[str]) -> None:
        if node.is_end:
            results.append(current)
        for char, child in node.children.items():
            self._dfs(child, current + char, results)


# ============================================================
# CÂU 9: 3 Thuật toán Sort
# ============================================================

# --- 1. Quick Sort ---
def quick_sort(arr: list) -> list:
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left   = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right  = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

# --- 2. Merge Sort ---
def merge_sort(arr: list) -> list:
    if len(arr) <= 1:
        return arr
    mid   = len(arr) // 2
    left  = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)

def _merge(left: list, right: list) -> list:
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# --- 3. Timsort (Built-in của Python) ---
def timsort(arr: list) -> list:
    return sorted(arr)
```
