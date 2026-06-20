"""
Demo code cho câu hỏi phỏng vấn 7, 8, 9:
- Câu 7: Tìm danh sách tên user DUY NHẤT
- Câu 8: Tìm kiếm tên user NHANH NHẤT (3 cách)
- Câu 9: 3 thuật toán Sort
"""

import random
import string
import time
import bisect
from collections import Counter


# ============================================================
# HELPER: Tạo dữ liệu mẫu 100K tên user (có trùng lặp)
# ============================================================
def generate_users(total: int = 100_000, unique_count: int = 60_000) -> list[str]:
    """Sinh ra 100K tên user có trùng lặp từ một pool 60K tên duy nhất."""
    base_names = [
        "".join(random.choices(string.ascii_lowercase, k=random.randint(4, 10)))
        for _ in range(unique_count)
    ]
    return random.choices(base_names, k=total)


# ============================================================
# CÂU 7: Tìm danh sách tên user DUY NHẤT
# ============================================================
def q7_find_unique_names(users: list[str]) -> list[str]:
    """
    Trả về danh sách tên KHÔNG TRÙNG LẶP.
    Dùng Set -> O(N) time, O(N) space.
    """
    return list(set(users))


def q7_find_appear_once(users: list[str]) -> list[str]:
    """
    Bonus: Tìm những tên CHỈ XUẤT HIỆN ĐÚNG 1 LẦN (không ai trùng).
    Dùng Counter (Hash Map) -> O(N) time.
    """
    freq = Counter(users)
    return [name for name, count in freq.items() if count == 1]


# ============================================================
# CÂU 8: Tìm kiếm tên user NHANH NHẤT
# ============================================================

# --- Cách 1: Hash Table / Set -> O(1) lookup ---
class HashSearch:
    """Load dữ liệu vào Set một lần, sau đó mỗi lần tìm kiếm tốn O(1)."""

    def __init__(self, users: list[str]):
        self.users_set = set(users)

    def search(self, name: str) -> bool:
        return name in self.users_set


# --- Cách 2: Binary Search -> O(log N) ---
class BinarySearch:
    """
    Yêu cầu: list phải được sắp xếp trước.
    Dùng module bisect của Python (đã được tối ưu bằng C).
    """

    def __init__(self, users: list[str]):
        self.sorted_users = sorted(set(users))  # sort một lần duy nhất

    def search(self, name: str) -> bool:
        idx = bisect.bisect_left(self.sorted_users, name)
        return idx < len(self.sorted_users) and self.sorted_users[idx] == name


# --- Cách 3: Trie (Prefix Tree) -> O(L) lookup, L = độ dài từ cần tìm ---
class TrieNode:
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_end = False


class Trie:
    """
    Prefix Tree: Tốc độ tìm kiếm chỉ phụ thuộc vào độ dài từ cần tìm.
    Rất phù hợp cho Autocomplete / Prefix search.
    """

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
        """Tìm kiếm chính xác một từ."""
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end

    def starts_with(self, prefix: str) -> list[str]:
        """Autocomplete: trả về tất cả tên bắt đầu bằng prefix."""
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
    """
    Divide & Conquer.
    Time: O(N log N) trung bình, O(N^2) worst case.
    Space: O(log N) đệ quy.
    """
    if len(arr) <= 1:
        return arr

    pivot = arr[len(arr) // 2]          # chọn pivot ở giữa để tránh worst case
    left   = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right  = [x for x in arr if x > pivot]

    return quick_sort(left) + middle + quick_sort(right)


# --- 2. Merge Sort ---
def merge_sort(arr: list) -> list:
    """
    Divide & Conquer.
    Time: O(N log N) mọi trường hợp (ổn định nhất).
    Space: O(N) bộ nhớ phụ.
    """
    if len(arr) <= 1:
        return arr

    mid   = len(arr) // 2
    left  = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return _merge(left, right)


def _merge(left: list, right: list) -> list:
    """Hàm phụ: trộn 2 mảng đã sắp xếp lại với nhau."""
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
    """
    Python's built-in sort (Timsort) - hybrid Merge Sort + Insertion Sort.
    Time: O(N log N) worst, O(N) best (khi gần sorted).
    Đây là thuật toán mặc định và tối ưu nhất cho dữ liệu thực tế.
    """
    return sorted(arr)


# ============================================================
# MAIN: Chạy demo và benchmark
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("SINH DỮ LIỆU 100K TÊN USER...")
    print("=" * 60)
    users = generate_users(total=100_000, unique_count=60_000)
    print(f"Tổng số tên (có trùng):   {len(users):,}")

    # ---- CÂU 7 ----
    print("\n" + "=" * 60)
    print("CÂU 7: TÌM TÊN USER DUY NHẤT")
    print("=" * 60)
    unique = q7_find_unique_names(users)
    print(f"Tên duy nhất (no-dup):    {len(unique):,}")

    appear_once = q7_find_appear_once(users)
    print(f"Tên xuất hiện đúng 1 lần: {len(appear_once):,}")
    print(f"Ví dụ 5 tên:              {appear_once[:5]}")

    # ---- CÂU 8 ----
    print("\n" + "=" * 60)
    print("CÂU 8: BENCHMARK 3 CÁCH TÌM KIẾM")
    print("=" * 60)

    target = users[42_000]   # chọn một tên có trong danh sách
    missing = "zzzzzzzzzzz"  # tên chắc chắn không có

    # Setup
    hash_searcher   = HashSearch(users)
    binary_searcher = BinarySearch(users)
    trie = Trie()
    for name in set(users):
        trie.insert(name)

    RUNS = 10_000

    # Hash Search
    t0 = time.perf_counter()
    for _ in range(RUNS):
        hash_searcher.search(target)
    t1 = time.perf_counter()
    print(f"Hash Search  (found={hash_searcher.search(target)}): {(t1-t0)*1000:.2f} ms / {RUNS:,} runs")

    # Binary Search
    t0 = time.perf_counter()
    for _ in range(RUNS):
        binary_searcher.search(target)
    t1 = time.perf_counter()
    print(f"Binary Search(found={binary_searcher.search(target)}): {(t1-t0)*1000:.2f} ms / {RUNS:,} runs")

    # Trie Search
    t0 = time.perf_counter()
    for _ in range(RUNS):
        trie.search(target)
    t1 = time.perf_counter()
    print(f"Trie Search  (found={trie.search(target)}): {(t1-t0)*1000:.2f} ms / {RUNS:,} runs")

    # Autocomplete demo
    prefix = target[:3]
    suggestions = trie.starts_with(prefix)[:5]
    print(f"\nAutocomplete prefix='{prefix}': {suggestions}")

    # ---- CÂU 9 ----
    print("\n" + "=" * 60)
    print("CÂU 9: BENCHMARK 3 THUẬT TOÁN SORT")
    print("=" * 60)
    sample = random.sample(range(1_000_000), 10_000)

    t0 = time.perf_counter()
    quick_sort(sample.copy())
    t1 = time.perf_counter()
    print(f"Quick Sort:  {(t1-t0)*1000:.2f} ms (N=10,000)")

    t0 = time.perf_counter()
    merge_sort(sample.copy())
    t1 = time.perf_counter()
    print(f"Merge Sort:  {(t1-t0)*1000:.2f} ms (N=10,000)")

    t0 = time.perf_counter()
    timsort(sample.copy())
    t1 = time.perf_counter()
    print(f"Timsort:     {(t1-t0)*1000:.2f} ms (N=10,000) <- Python built-in")

    # Verify tất cả đều cho kết quả giống nhau
    expected = sorted(sample)
    assert quick_sort(sample.copy()) == expected, "Quick Sort sai!"
    assert merge_sort(sample.copy()) == expected, "Merge Sort sai!"
    assert timsort(sample.copy())    == expected, "Timsort sai!"
    print("\n✅ Tất cả 3 thuật toán cho kết quả chính xác!")
