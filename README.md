# 8_puzzle_visualizer

Dự án trực quan hóa các thuật toán tìm kiếm để giải bài toán 8-Puzzle (Còn nhiều thuật toán sẽ được thêm vào). Đây là các bài tập hàng tuần cho môn học **Trí tuệ nhân tạo**.

## Thông tin sinh viên
* **Họ và tên:** Nguyễn Phước Minh Triết
* **Mã số sinh viên (MSSV):** 24110357
* **Giảng viên:** TS. Phan Thị Huyền Trang
* **Mã lớp học phần:** 252ARIN330585_08
* **Trường:** Đại học Công nghệ Kỹ thuật TP.HCM (HCMUTE)
* **Link Github bài tập:** https://github.com/ChissZar/8_puzzle_visualizer

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
│   ├── puzzle_state.py    # Định nghĩa cấu trúc Node, các bước di chuyển hợp lệ
│   └── ..._solver.py      # Trái tim của các thuật toán tìm kiếm (BFS, DFS,...)
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

`
cd đường_dẫn_đến_thư_mục/8_puzzle_visualizer
`

- Khởi chạy ứng dụng bằng lệnh:

`
python main.py
`
## Hướng dẫn tùy chỉnh cấu hình Trạng thái

Để thay đổi các bài toán test hoặc cấu hình lại trò chơi, bạn có thể chỉnh sửa trực tiếp trong mã nguồn theo các lưu ý sau:

- **1/ Thay đổi Trạng thái Đích (Goal State).**<br>

    - Vị trí file: **logic/puzzle_state.py**

    - Nơi chỉnh sửa: Bên trong lớp PuzzleState, tìm hàm is_goal(self).

    - Cách sửa: Thay đổi mảng Tuple 1 chiều đại diện cho 9 ô số (với số 0 là ô trống) theo ý muốn.

    - Ví dụ cấu hình đích mặc định: 1 2 3, 4 5 6, 7 8 0

```text
def is_goal(self):
        return self.board == (1, 2, 3, 
                              4, 5, 6, 
                              7, 8, 0)
```

- **2/ Thay đổi Trạng thái Ban đầu (Initial State)**<br>
    - Vị trí file: ui/main_window.py

    - Nơi chỉnh sửa: Bên trong lớp MainWindow, tìm hàm khởi tạo __init__(self, root).

    - Cách sửa: Thay đổi giá trị của biến initial_board.

    - Ví dụ cấu hình trạng thái ban đầu cần giải:

```text
initial_board = (2, 8, 3, 
                 1, 6, 4,
                 7, 0, 5)
```

---

## Các tính năng chính trên UI (QUAN TRỌNG)

- **Đa thuật toán:** Dễ dàng chuyển đổi qua lại giữa các thuật toán BFS, DFS, IDS,... (còn nhiều thuật toán sẽ được thêm vào) ngay trên thanh Combobox của giao diện và Apply mà không cần khởi động lại ứng dụng.

- **Frontier View:** Hiển thị hàng ngang 5 ma trận mini đại diện cho các trạng thái chuẩn bị được lấy ra xét. View sẽ tự động thích ứng **hiển thị các Node cũ nhất (đối với FIFO Queue) hoặc các Node mới nhất (đối với LIFO Stack)** tùy vào thuật toán đang chạy.

- **Khu vực Expansion:** Trực quan hóa hàm EXPAND. Ô trung tâm màu cam là Node đang xét, 4 ô xung quanh đại diện cho 4 hướng trượt.

    - **Ô mờ xám:** Hướng đi bị cụt (không hợp lệ).

    - **Ô viền xanh lá:** Trạng thái mới, hợp lệ để đưa vào Frontier.

    - **Ô viền đỏ:** Trạng thái đã tồn tại trong reached hoặc bị lặp chu trình, bị loại bỏ.

- **Kiểm soát quy trình:** Cung cấp nút Next Step để nhảy từng bước phân tích thuật toán, hoặc Auto Play để AI tự động giải liên tục (có thể tạm dừng bất cứ lúc nào).

- **Thống kê thời gian thực & Truy vết:** Cập nhật liên tục số lượng trạng thái đã duyệt, số lượng Frontier. Khi tìm thấy đích, cho phép click vào từng bước trong Solution Path để xem lại chính xác cấu hình ma trận tại bước đó.

- **Xử lý ngoại lệ an toàn:** Tự động vét cạn các trường hợp vô nghiệm và báo "Failure" an toàn, chống treo máy.