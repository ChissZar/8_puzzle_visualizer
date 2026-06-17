# 8-Puzzle Visualizer

Dự án trực quan hóa các thuật toán tìm kiếm cho bài toán 8-Puzzle, phục vụ học phần **Trí tuệ nhân tạo**. Ứng dụng được xây dựng bằng Python/Tkinter, cho phép theo dõi từng bước mở rộng trạng thái, frontier, đường đi hiện tại, lời giải cuối cùng và các mô hình như Belief State, Partially Observable, AND-OR Search, CSP và Adversarial Search.

## Thông tin sinh viên

- **Họ và tên:** Nguyễn Phước Minh Triết
- **Mã số sinh viên (MSSV):** 24110357
- **Giảng viên:** TS. Phan Thị Huyền Trang
- **Mã lớp học phần:** 252ARIN330585_08
- **Trường:** Đại học Công nghệ Kỹ thuật TP.HCM (HCMUTE)
- **Link Github bài tập:** https://github.com/ChissZar/8_puzzle_visualizer

## Cấu trúc thư mục

```text
8_puzzle_visualizer/
├── main.py
├── README.md
├── logic/
│   ├── puzzle_state.py
│   ├── uninformed_search/
│   │   ├── bfs_solver.py
│   │   ├── dfs_solver.py
│   │   ├── ids_solver.py
│   │   └── ucs_solver.py
│   ├── informed_search/
│   │   ├── greedy_solver.py
│   │   ├── astar_solver.py
│   │   └── ida_star_solver.py
│   ├── local_search/
│   │   ├── simple_hill_climbing_solver.py
│   │   ├── steepest_ascent_hill_climbing_solver.py
│   │   ├── stochastic_hill_climbing_solver.py
│   │   ├── random_restart_hill_climbing_solver.py
│   │   ├── local_beam_search_solver.py
│   │   └── simulated_annealing_solver.py
│   ├── complex_env_search/
│   │   ├── common.py
│   │   ├── sensorless_goal_solver.py
│   │   ├── sensorless_homing_solver.py
│   │   ├── partially_observable_solver.py
│   │   └── and_or_graph_search.py
│   ├── adversarial_search/
│   │   └── minimax_solver.py
│   └── csp/
│       └── backtracking_solver.py
└── ui/
    ├── main_window.py
    └── board_widget.py
```

## Cài đặt và khởi chạy

Yêu cầu:

- Python 3.x
- Tkinter, thường đã có sẵn khi cài Python

Chạy chương trình:

```bash
cd duong_dan_den_thu_muc/8_puzzle_visualizer
python main.py
```

## Cách nhập dữ liệu

### Trạng thái đơn

Dùng cho các thuật toán Chapter 1, 2, 3 và AND-OR Search:

```text
CUSTOM INITIAL BOARD: 1 2 3 4 0 6 7 5 8
CUSTOM GOAL BOARD:    1 2 3 4 5 6 7 8 0
```

Số `0` đại diện cho ô trống.

### Belief State

Dùng cho các thuật toán trong môi trường phức tạp:

- Searching with no observation (Has Goal)
- Searching with no observation (No Goal)
- Searching for partially observable problems

Có thể nhập nhiều board bằng dấu phẩy:

```text
1 2 3 4 0 6 7 5 8, 1 2 3 4 5 6 7 0 8
```

Nếu không nhập nhiều board, chương trình tự tạo một Belief State demo để mô phỏng trường hợp không quan sát được chính xác trạng thái ban đầu.

## Danh sách thuật toán

### Chapter 1: Uninformed Search

- BFS (Breadth-First Search)
- DFS (Depth-First Search)
- IDS (Iterative Deepening Search)
- UCS (Uniform Cost Search)

### Chapter 2: Informed Search

- Greedy Search
- A* Search
- IDA* Search

### Chapter 3: Local Search

- Simple Hill Climbing
- Steepest-Ascent Hill Climbing
- Stochastic Hill Climbing
- Random Restart Hill Climbing
- Local Beam Search
- Simulated Annealing

### Chapter 4: Complex Environments

- Searching with no observation (Has Goal)
- Searching with no observation (No Goal)
- Searching for partially observable problems
- AND-OR Search (Non-deterministic)

Nhóm này sử dụng Belief State hoặc conditional plan:

- **Sensorless Has Goal:** tìm chuỗi hành động đưa toàn bộ Belief State về đúng Goal.
- **Sensorless No Goal:** không cần Goal, chỉ cần dồn Belief State về còn đúng một trạng thái.
- **Partially Observable:** agent chỉ quan sát được một phần trạng thái, hiện tại sensor mô phỏng bằng vị trí ô trống `0`.
- **AND-OR Search:** xử lý môi trường không tất định, ví dụ hành động có thể thành công hoặc bị trượt và đứng yên.

### Chapter 5: Constraint Satisfaction Problems

- Backtracking Search (8-Puzzle CSP)
- Backtracking + Forward Checking (8-Puzzle CSP)
- AC-3 Search (8-Puzzle CSP)
- Min-Conflicts Search (8-Puzzle CSP)

Mô hình CSP trong chương này:

- **Variables:** `x1, x2, ..., x9`, tương ứng 9 ô của bảng 8-puzzle.
- **Domain:** mỗi biến có miền giá trị `{0, 1, 2, 3, 4, 5, 6, 7, 8}`.
- **Constraints:**
  - Mỗi biến nhận đúng một giá trị.
  - Các biến không được trùng giá trị.
  - Giá trị tại từng ô phải khớp với `CUSTOM GOAL BOARD`.
- **Backtracking:** chọn biến chưa gán, thử giá trị domain theo thứ tự random, kiểm tra ràng buộc rồi quay lui khi thất bại.
- **Forward Checking:** sau khi gán một giá trị, loại giá trị đó khỏi domain của các biến liên quan.
- **AC-3:** đưa toàn bộ arc `(Xi, Xj)` vào queue, loại các giá trị không có support trong domain biến còn lại, và thêm lại các arc liên quan khi một domain bị giảm.
- **Min-Conflicts:** bắt đầu bằng một complete assignment, chọn ngẫu nhiên biến đang conflict, rồi đổi sang giá trị gây ít conflict nhất.

### Chapter 6: Adversarial Search

- Minimax Search (Tic-Tac-Toe Demo)

Demo Minimax dùng tic-tac-toe thay vì 8-puzzle vì Minimax là thuật toán cho trò chơi đối kháng hai người:

- **MAX:** người chơi `X`, chọn nhánh có utility lớn nhất.
- **MIN:** người chơi `O`, chọn nhánh có utility nhỏ nhất.
- **Utility:** `X` thắng = `+10`, hòa = `0`, `O` thắng = `-10`.
- Thuật toán đi xuống các trạng thái terminal, gán utility, rồi truyền giá trị ngược lên cây.
- Giao diện hiển thị cây game, node đang xét, cạnh đang trả value và đường đi cuối cùng MAX chọn.

## Tính năng giao diện

- Chia thuật toán theo tab chương học.
- `Next Step` để chạy từng bước.
- `Prev Step` để quay lại bước trước, bao gồm cả các solver dùng generator như Partially Observable, AND-OR và nhóm CSP.
- `Auto Play` với tốc độ tùy chỉnh.
- `Current Path` hiển thị đường đi hoặc nhánh quan sát hiện tại.
- `Final Solution` hiển thị lời giải cuối cùng, có thể bấm vào từng bước để xem lại trạng thái.
- Frontier tự đổi cách hiển thị theo thuật toán: Queue, Stack, Priority Queue, Neighbors, Belief State hoặc CSP Assignment.
- Với Belief State:
  - Hiển thị kích thước `|B|`.
  - Hiển thị các board có thể xảy ra.
  - Hiển thị kết quả sau từng action.
  - Với Partially Observable, hiển thị `SENSOR OBSERVATION` để phân biệt bước quan sát với bước hành động.
- Với AND-OR Search:
  - Hiển thị cây OR/AND.
  - OR node là trạng thái agent chọn hành động.
  - AND node là các kết quả môi trường có thể sinh ra.
- Với CSP:
  - Hiển thị assignment hiện tại.
  - Hiển thị domain từng biến.
  - Hiển thị biến đang xét, giá trị đang thử và trạng thái accept/reject.
  - Với AC-3, hiển thị current arc, queue size, queue preview và các giá trị bị loại khỏi domain.
  - Với Min-Conflicts, hiển thị biến đang conflict, từng giá trị candidate được thử, điểm `CONFLICTS(v)` và bước gán giá trị tốt nhất.
- Với Minimax:
  - Hiển thị cây trò chơi MAX/MIN.
  - Hiển thị utility tại terminal node và giá trị được truyền ngược lên.
  - Tô node/cạnh đang xét và đường đi tối ưu sau khi thuật toán kết thúc.
