# 8-Puzzle Visualizer

Dự án trực quan hóa các thuật toán tìm kiếm để giải bài toán 8-Puzzle (Còn nhiều thuật toán sẽ được thêm vào). Đây là phiên bản nâng cao được thiết kế chuyên biệt cho mục đích học thuật, hỗ trợ phân tích chi tiết quá trình ra quyết định của thuật toán. Đây là các bài tập hàng tuần cho môn học **Trí tuệ nhân tạo**.

## Thông tin sinh viên
* **Họ và tên:** Nguyễn Phước Minh Triết
* **Mã số sinh viên (MSSV):** 24110357
* **Giảng viên:** TS. Phan Thị Huyền Trang
* **Mã lớp học phần:** 252ARIN330585_08
* **Trường:** Đại học Công nghệ Kỹ Thuật TP.HCM (HCMUTE)
* **Link Github bài tập:** [https://github.com/ChissZar/8_puzzle_visualizer](https://github.com/ChissZar/8_puzzle_visualizer)

---

## Cấu trúc thư mục dự án
Dự án được thiết kế theo mô hình tách biệt rõ ràng giữa Logic toán học (Thuật toán) và Giao diện người dùng (UI):

```text
8_puzzle_bfs_visualizer/
│
├── main.py                # Điểm bắt đầu (Entry point) để kích hoạt ứng dụng
│
├── logic/                 # Thư mục chứa thuần logic thuật toán
│   ├── __init__.py
│   ├── puzzle_state.py    # Định nghĩa cấu trúc Node, các bước di chuyển hợp lệ, hàm Heuristic
│   └── ..._solver.py      # Trái tim của các thuật toán tìm kiếm (Unifromed Search, Infromed Search, Local Search,...)
│
└── ui/                    # Thư mục quản lý toàn bộ giao diện Tkinter
    ├── __init__.py
    ├── main_window.py     # Sân khấu chính, bố cục Frontier, khu vực Expansion và Controls
    └── board_widget.py    # Thành phần (Component) vẽ ma trận 3x3 tái sử dụng liên tục
```
## Hướng dẫn cài đặt và khởi chạy
**1. Yêu cầu hệ thống**

- Máy tính đã cài đặt sẵn Python 3.x.

- Dự án này sử dụng thư viện giao diện đồ họa Tkinter (thư viện core đã được tích hợp sẵn khi cài đặt Python, không cần cài thêm từ bên ngoài).

**2. Cách khởi chạy chương trình**
- Để tránh lỗi nạp gói dữ liệu (ImportError), bạn cần đảm bảo rằng VS Code hoặc Terminal của bạn đang mở chính xác tại thư mục dự án.

- Mở Terminal hoặc Command Prompt lên.

- Di chuyển vào thư mục gốc của dự án:

```bash
  cd đường_dẫn_đến_thư_mục/8_puzzle_visualizer
```
- Khởi chạy ứng dụng bằng lệnh:
```bash
  python main.py
```

## Hướng dẫn Tùy chỉnh
Bạn **không cần phải can thiệp vào mã nguồn** để thay đổi bài toán. Mọi thao tác cấu hình đều có thể thực hiện trực tiếp trên giao diện trực quan:

1. **Thay đổi Trạng thái Ban đầu (Initial Board) và Đích (Goal Board):**
   - Nhìn sang thanh Sidebar bên trái màn hình.
   - Nhập chuỗi 9 số (từ 0 đến 8, cách nhau bởi khoảng trắng) vào ô **CUSTOM INITIAL BOARD** và **CUSTOM GOAL BOARD**. (Số `0` đại diện cho ô trống).
   - *Ví dụ:* `1 2 3 4 0 6 7 5 8`
2. **Áp dụng cấu hình:**
   - Bấm nút **"Apply Custom & Reset"** (Màu Đỏ). 
   - Hệ thống sẽ tự động cập nhật lại toàn bộ lõi thuật toán và giao diện với bài toán mới ngay lập tức.

---

## Các tính năng học thuật nổi bật

- **Hệ thống Thuật toán:** Ứng dụng hỗ trợ phân tích 3 chương kiến thức cốt lõi của AI (sẽ còn được cập nhật thêm), dễ dàng chuyển đổi qua Tab và Combobox:
  - *Chapter 1 (Uninformed Search):* BFS, DFS, IDS, UCS.
  - *Chapter 2 (Informed Search):* Greedy, A*, IDA*.
  - *Chapter 3 (Local Search):* Simple Hill Climbing, Steepest-Ascent Hill Climbing.

- **Khu vực Expansion & Bóc tách Chi phí thông minh:** Trực quan hóa hàm EXPAND với 4 hướng trượt.
  - Tự động hiển thị các chỉ số toán học ($g$, $h$, $f$, Cost) ngay bên dưới các trạng thái lân cận tùy theo thuật toán đang chạy (Ví dụ: A* sẽ hiện $f(n) = g(n) + h(n)$, Hill Climbing chỉ hiện $h(n)$).
  - Đổ màu sắc thái chuẩn học thuật: 
    - **Ô viền xanh lá:** Trạng thái mới, hợp lệ.
    - **Ô viền đỏ:** Trạng thái đã tồn tại (Reached/Cutoff), hoặc có Heuristic tệ hơn hiện tại, bị loại bỏ.
    - **Ô viền vàng:** Trạng thái đích (Goal).

- **Frontier View Linh hoạt:** Khay chứa tự động đổi tên và cấu trúc mô phỏng đúng lý thuyết: **Queue** (BFS), **Stack** (DFS, IDS), **Priority Queue** (UCS, Greedy, A*), và **Neighbors** (dành riêng cho thuật toán không lưu vết như Hill Climbing).

- **Kiểm soát & Truy vết quá trình:** - Cung cấp nút `Next Step` / `Prev Step` để phân tích thủ công từng chu kỳ, hoặc `Auto Play` để AI tự động giải (có thể tùy chỉnh tốc độ).
  - Bảng **Final Solution** hiển thị danh sách các bước đi tối ưu kèm theo chi phí của từng bước. Cho phép click vào từng bước để xem lại cấu hình ma trận trong quá khứ.