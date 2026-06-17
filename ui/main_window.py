import copy
import tkinter as tk
from tkinter import ttk, messagebox
from ui.board_widget import BoardWidget

# --- CHƯƠNG 1: UNINFORMED SEARCH ---
from logic.uninformed_search.bfs_solver import BFSSolver
from logic.uninformed_search.dfs_solver import DFSSolver
from logic.uninformed_search.ids_solver import IDSSolver
from logic.uninformed_search.ucs_solver import UCSSolver

# --- CHƯƠNG 2: INFORMED SEARCH ---
from logic.informed_search.greedy_solver import GreedySolver
from logic.informed_search.astar_solver import AStarSolver
from logic.informed_search.ida_star_solver import IDAStarSolver

# --- CHƯƠNG 3: LOCAL SEARCH ---
from logic.local_search.simple_hill_climbing_solver import SimpleHillClimbingSolver
from logic.local_search.steepest_ascent_hill_climbing_solver import SteepestAscentHillClimbingSolver
from logic.local_search.stochastic_hill_climbing_solver import StochasticHillClimbingSolver
from logic.local_search.random_restart_hill_climbing_solver import RandomRestartHillClimbingSolver
from logic.local_search.local_beam_search_solver import LocalBeamSearchSolver
from logic.local_search.simulated_annealing_solver import SimulatedAnnealingSolver

# --- CHƯƠNG 4: COMPLEX ENVIRONMENTS ---
from logic.complex_env_search.sensorless_goal_solver import SensorlessGoalSolver
from logic.complex_env_search.sensorless_homing_solver import SensorlessHomingSolver
from logic.complex_env_search.partially_observable_solver import PartiallyObservableSolver
from logic.complex_env_search.and_or_graph_search import AndOrGraphSearchSolver
from logic.complex_env_search.common import make_auto_belief

# --- CHƯƠNG 5: CONSTRAINT SATISFACTION PROBLEMS ---
from logic.csp.backtracking_solver import BacktrackingCSPSolver, ForwardCheckingCSPSolver, AC3CSPSolver, MinConflictsCSPSolver

# --- CHƯƠNG 6: ADVERSARIAL SEARCH ---
from logic.adversarial_search.minimax_solver import MinimaxSolver

BG_MAIN = "#0f172a"      
BG_PANEL = "#1e293b"     
TEXT_MAIN = "#f8fafc"    
TEXT_MUTED = "#94a3b8"   
ACCENT_BLUE = "#38bdf8"  
ACCENT_GREEN = "#4ade80" 
ACCENT_ORANGE = "#fb923c"
ACCENT_RED = "#f87171"   
HIGHLIGHT_GOLD = "#facc15"

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Visualizer")
        self.root.configure(bg=BG_MAIN)
        self.root.state('zoomed') 
        
        self.is_auto_playing = False
        self.solution_path = []
        self.step_count = 0
        self.initial_board = (1, 2, 3, 4, 0, 6, 7, 5, 8) 
        self.goal_board = (1, 2, 3, 4, 5, 6, 7, 8, 0)
        self.initial_belief_states = [self.initial_board]
        self.manual_belief_input = False
        
        self.algorithms = {
            "BFS (Breadth-First Search)": BFSSolver,
            "DFS (Depth-First Search)": DFSSolver,
            "IDS (Iterative Deepening Search)": IDSSolver,
            "UCS (Uniform Cost Search)": UCSSolver,
            "Greedy Search (Manhattan)": GreedySolver,
            "A* Search (Inversions + Misplaced)": AStarSolver,
            "IDA* Search (Manhattan + Misplaced)": IDAStarSolver,
            "Simple Hill Climbing (Manhattan)": SimpleHillClimbingSolver,
            "Steepest-Ascent Hill Climbing (Manhattan)": SteepestAscentHillClimbingSolver,
            "Stochastic Hill Climbing (Manhattan)": StochasticHillClimbingSolver,
            "Random Restart Hill Climbing (Manhattan)": RandomRestartHillClimbingSolver,
            "Local Beam Search (k=2)": LocalBeamSearchSolver,
            "Simulated Annealing (Manhattan)": SimulatedAnnealingSolver,
            "Searching with no observation (Has Goal)": SensorlessGoalSolver,
            "Searching with no observation (No Goal)": SensorlessHomingSolver,
            "Searching for partially observable problems": PartiallyObservableSolver,
            "AND-OR Search (Non-deterministic)": AndOrGraphSearchSolver,
            "Backtracking Search (8-Puzzle CSP)": BacktrackingCSPSolver,
            "Backtracking + Forward Checking (8-Puzzle CSP)": ForwardCheckingCSPSolver,
            "AC-3 Search (8-Puzzle CSP)": AC3CSPSolver,
            "Min-Conflicts Search (8-Puzzle CSP)": MinConflictsCSPSolver,
            "Minimax Search (Tic-Tac-Toe Demo)": MinimaxSolver
        }

        self.algo_docs = {
            "BFS": "== BREADTH-FIRST SEARCH ==\n- Loại: Uninformed Search\n- Chiến lược: Duyệt hàng ngang (FIFO)\n- Độ phức tạp: O(b^d)\n- Bộ nhớ: Tốn kém (Lưu toàn bộ cây)\n- Tính tối ưu: Có (nếu cost = 1)",
            "DFS": "== DEPTH-FIRST SEARCH ==\n- Loại: Uninformed Search\n- Chiến lược: Duyệt sâu tận đáy (LIFO)\n- Độ phức tạp: O(b^m)\n- Bộ nhớ: Rất tiết kiệm O(bm)\n- Tính tối ưu: KHÔNG",
            "IDS": "== ITERATIVE DEEPENING ==\n- Loại: Uninformed Search\n- Chiến lược: Kết hợp DFS và BFS\n- Cơ chế: Tăng dần giới hạn độ sâu l\n- Ưu điểm: Tiết kiệm bộ nhớ như DFS nhưng đảm bảo tối ưu như BFS.",
            "UCS": "== UNIFORM COST SEARCH ==\n- Loại: Uninformed Search\n- Chiến lược: Mở rộng node có g(n) thấp nhất\n- Thuật toán gốc: Dijkstra\n- Tính tối ưu: Luôn tối ưu mọi trường hợp.",
            "Greedy": "== GREEDY BEST-FIRST SEARCH ==\n- Loại: Informed Search\n- Chiến lược: Đi theo Heuristic h(n) tốt nhất\n- Đặc điểm: Tìm đường cực nhanh nhưng dễ sa đà, không đảm bảo tối ưu.",
            "A*": "== A* SEARCH ==\n- Loại: Informed Search\n- Công thức: f(n) = g(n) + h(n)\n- Đặc điểm: Tính toán cả quá khứ g(n) và tương lai h(n). Tối ưu tuyệt đối.",
            "IDA*": "== ITERATIVE DEEPENING A* ==\n- Loại: Informed Search\n- Cơ chế: Giống IDS nhưng cắt tỉa bằng ngưỡng f_limit.\n- Ưu điểm: Hiệu năng cực cao, tốn siêu ít RAM.",
            "Simple HC": "== SIMPLE HILL CLIMBING ==\n- Loại: Local Search (Leo đồi)\n- Cơ chế: Duyệt L->R->U->D, gặp trạng thái tốt hơn là CHỐT NGAY, bỏ qua các hướng còn lại.\n- Điểm yếu: Dễ kẹt cực đại cục bộ.",
            "Steepest HC": "== STEEPEST-ASCENT HILL CLIMBING ==\n- Loại: Local Search (Leo đồi dốc nhất)\n- Cơ chế: Sinh TOÀN BỘ lân cận, cân đo đong đếm tìm ra hướng TỐT NHẤT rồi mới đi.\n- Đặc điểm: Bài bản, chậm mà chắc.",
            "Stochastic HC": "== STOCHASTIC HILL CLIMBING ==\n- Loại: Local Search (Ngẫu nhiên)\n- Đặc điểm: Lọc ra danh sách 'Better Neighbors', sau đó bốc NGẪU NHIÊN 1 trạng thái để đi tiếp. Giúp tránh kẹt lối mòn.",
            "Restart HC": "== RANDOM RESTART HILL CLIMBING ==\n- Cơ chế: Nếu kẹt cực đại cục bộ, thuật toán sẽ quay về ĐÚNG VẠCH XUẤT PHÁT (Start) để leo đồi lại. Dựa vào việc chọn ngẫu nhiên các lân cận (Stochastic), kỳ vọng lần chạy sau sẽ rẽ sang nhánh khác để thoát kẹt.\n- Phân tích: Áp dụng vào 8-Puzzle thường kém hiệu quả vì tập 'Better Neighbors' quá ít, thuật toán dễ đi lại vào vết xe đổ cũ.",
            "Beam Search": "== LOCAL BEAM SEARCH (k) ==\n- Cơ chế: Sinh TẤT CẢ lân cận từ k trạng thái hiện tại (chùm). Sau đó gom lại, sắp xếp và chỉ chọn ra đúng k lân cận tốt nhất để đi tiếp thế hệ sau.\n- Chú thích Giao diện ở Current State Set -> Neighbors:\n  + Bên trái ô trống: Tập k trạng thái của chùm hiện tại (Current State Set).\n  + Bên phải ô trống: Hồ bơi chứa các lân cận (Neighbors) vừa được sinh ra để chờ xét duyệt.\n- Ưu điểm: Tránh kẹt cục bộ tốt hơn Hill Climbing nhờ đi song song nhiều nhánh.",
            "Simulated Annealing": "== SIMULATED ANNEALING ==\n- Cảm hứng: Quá trình tôi luyện kim loại.\n- Cơ chế: Chọn ngẫu nhiên 1 lân cận.\n  + Δ < 0 (TỐT HƠN): Chấp nhận luôn (Ô XANH LÁ).\n  + Δ >= 0 (TỆ HƠN): Không bỏ qua ngay, mà chấp nhận với xác suất P = exp(-Δ/T) (Ô VÀNG GOLD), hoặc Từ chối (Ô ĐỎ).\n- Ý nghĩa: Nhiệt độ T càng cao (lúc mới chạy), thuật toán càng 'dễ dãi' đi vào đường xấu (Màu Vàng) để thoát khỏi cực đại cục bộ. T giảm dần, nó sẽ khắt khe hơn.",
            "Sensorless (Goal)": "== SENSORLESS (HAS GOAL) ==\n- Không quan sát được trạng thái ban đầu, nhưng biết Goal.\n- Nếu không nhập nhiều ma trận bằng dấu phẩy, chương trình tự dựng Belief State quanh CUSTOM GOAL BOARD.\n- Cơ chế: một action được áp dụng đồng thời cho mọi board trong Belief State; đụng tường thì board đó đứng im.\n- Mục tiêu: tìm chuỗi action làm toàn bộ Belief State co lại đúng Goal.",
            "Sensorless (No Goal)": "== SENSORLESS (NO GOAL) ==\n- Không có Goal để kiểm tra đích; thuật toán chỉ cần xóa mơ hồ.\n- Nếu không nhập nhiều ma trận bằng dấu phẩy, chương trình tự dựng Belief State demo.\n- Cơ chế: một action được áp dụng đồng thời cho mọi board có thể xảy ra.\n- Mục tiêu (Homing Sequence): dồn Belief State về đúng 1 board duy nhất, bất kể board đó là gì.",
            "Partially Observable": "== PARTIALLY OBSERVABLE (AND-OR) ==\n- Agent không thấy toàn bộ board, chỉ nhận percept một phần: vị trí ô trống (0).\n- Nếu không nhập nhiều ma trận bằng dấu phẩy, chương trình tự dựng Belief State demo.\n- OR: agent chọn action. AND: sensor chia kết quả thành các nhánh observation.\n- Mục tiêu: tìm plan xử lý được mọi nhánh quan sát cho tới Goal.",
            "AND-OR": "== AND-OR SEARCH (NON-DETERMINISTIC) ==\n- Đầu vào: 1 ma trận duy nhất.\n- Môi trường: Không tất định (bị trơn trượt). Lệnh UP có thể thành công, hoặc đứng yên.\n- Mục tiêu: Tìm 'Kế hoạch có điều kiện' để dù trượt chân vẫn về đích.",
            "Backtracking CSP": "== BACKTRACKING SEARCH FOR 8-PUZZLE CSP ==\n- Loại: Constraint Satisfaction Problems.\n- Variables: x1, x2, ..., x9 tương ứng 9 ô của bảng 8-puzzle.\n- Domain: mỗi xi có thể nhận giá trị 0..8.\n- ORDER-DOMAIN-VALUES: xáo trộn random thứ tự xét giá trị mỗi lần chọn biến.\n- Constraints: mỗi xi chỉ nhận 1 giá trị, các xi không được trùng nhau, và mỗi ô phải khớp CUSTOM GOAL BOARD.\n- Cơ chế đúng mã giả: chọn biến chưa gán -> thử từng giá trị domain -> nếu consistent thì add vào assignment -> gọi đệ quy -> nếu thất bại thì remove và backtrack.",
            "Forward Checking CSP": "== BACKTRACKING + FORWARD CHECKING FOR 8-PUZZLE CSP ==\n- Vẫn dùng X = {x1...x9}, D = {0...8}, C = all-different + fixed goal-cell constraints.\n- Khác Backtracking thường: thuật toán lưu domain riêng D(xi) của từng biến.\n- Khi đã gán xi = value, mọi biến chưa gán liên quan sẽ loại value khỏi domain.\n- Với 8-puzzle, các biến đều liên quan với nhau qua constraint không trùng số, nên gán x1 = 1 thì D(x2)...D(x9) đều bỏ 1.\n- Nếu domain của biến nào rỗng, thuật toán backtrack ngay.",
            "AC-3 CSP": "== AC-3 ARC CONSISTENCY FOR 8-PUZZLE CSP ==\n- Loại: Constraint Satisfaction Problems.\n- Variables: x1...x9 tương ứng 9 ô của 8-puzzle.\n- Domain ban đầu: D(xi) = {0...8}.\n- Queue ban đầu: toàn bộ arc có hướng (Xi, Xj).\n- Constraint: mỗi Xi phải khớp giá trị goal tại ô đó và Xi != Xj với mọi biến khác.\n- Mỗi bước lấy một arc khỏi queue, chạy RM-INCONSISTENT-VALUES(Xi, Xj).\n- Nếu D(Xi) bị giảm, thêm lại các arc liên quan (Xk, Xi) vào queue.\n- Khi queue rỗng, CSP đạt arc-consistency.",
            "Min-Conflicts CSP": "== MIN-CONFLICTS FOR 8-PUZZLE CSP ==\n- Loại: Local Search for Constraint Satisfaction Problems.\n- Bắt đầu bằng một complete assignment, ở đây lấy từ CUSTOM INITIAL BOARD.\n- Nếu current là solution thì dừng.\n- Chọn một biến đang conflict.\n- Hiển thị từng lần thử v trong domain và tính CONFLICTS(var, v, current, csp).\n- Sau khi xét xong D(var), chọn giá trị gây ít conflict nhất rồi set var = value.\n- Lặp tối đa max_steps; nếu hết bước mà chưa hết conflict thì failure.\n- Với 8-puzzle CSP, conflict gồm: sai vị trí goal và trùng giá trị với biến khác.",
            "Minimax": "== MINIMAX SEARCH ==\n- Loại: Adversarial Search, dùng cho trò chơi hai người.\n- Demo hiện tại dùng Tic-Tac-Toe để dễ thấy MAX/MIN.\n- MAX là X: cố gắng lấy utility lớn nhất.\n- MIN là O: cố gắng kéo utility xuống nhỏ nhất.\n- Utility: X thắng = +10, hòa = 0, O thắng = -10.\n- Cơ chế: đi xuống tới terminal state, gán utility, rồi truyền giá trị ngược lên cây.\n- MAX node chọn max(child values), MIN node chọn min(child values)."
        }
        
        self.solver = None 
        self.setup_ui()
        self.reset_environment()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=BG_MAIN, borderwidth=0)
        style.configure('TNotebook.Tab', background=BG_PANEL, foreground=TEXT_MUTED, font=('Fixedsys', 10, 'bold'), padding=[8, 7])
        style.map('TNotebook.Tab', background=[('selected', ACCENT_BLUE)], foreground=[('selected', BG_MAIN)])
        style.configure('TCombobox', fieldbackground=BG_PANEL, background=BG_MAIN, foreground=TEXT_MAIN)
        style.map('TCombobox',
                  fieldbackground=[('readonly', BG_PANEL)],
                  selectbackground=[('readonly', BG_PANEL)],
                  selectforeground=[('readonly', TEXT_MAIN)],
                  foreground=[('readonly', TEXT_MAIN)])

        # Can thiệp vào hệ thống của Tkinter
        self.root.option_add('*TCombobox*Listbox.font', ('Fixedsys', 12, 'bold')) 
        self.root.option_add('*TCombobox*Listbox.background', BG_PANEL)
        self.root.option_add('*TCombobox*Listbox.foreground', TEXT_MAIN)
        self.root.option_add('*TCombobox*Listbox.selectBackground', ACCENT_BLUE)
        self.root.option_add('*TCombobox*Listbox.selectForeground', BG_MAIN)

        # ==========================================
        # LEFT COLUMN: SIDEBAR CONTROLS & DOCS
        # ==========================================
        self.left_sidebar = tk.Frame(self.root, bg=BG_PANEL, padx=20, pady=20, width=380)
        self.left_sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        self.left_sidebar.pack_propagate(False)

        # Custom Input Matrix
        self.lbl_initial_title = tk.Label(self.left_sidebar, text="CUSTOM INITIAL BOARD", fg=HIGHLIGHT_GOLD, bg=BG_PANEL, font=('Fixedsys', 11, 'bold'))
        self.lbl_initial_title.pack(anchor=tk.W, pady=(0, 5))
        self.ent_input = tk.Entry(self.left_sidebar, font=('Fixedsys', 14), bg=BG_MAIN, fg=TEXT_MAIN, insertbackground=TEXT_MAIN, relief=tk.FLAT)
        self.ent_input.insert(0, "1 2 3 4 0 6 7 5 8")
        self.ent_input.pack(fill=tk.X, pady=(0, 15))

        tk.Label(self.left_sidebar, text="CUSTOM GOAL BOARD", fg=ACCENT_GREEN, bg=BG_PANEL, font=('Fixedsys', 11, 'bold')).pack(anchor=tk.W, pady=(0, 2))
        self.ent_goal = tk.Entry(self.left_sidebar, font=('Fixedsys', 14), bg=BG_MAIN, fg=TEXT_MAIN, insertbackground=TEXT_MAIN, relief=tk.FLAT)
        self.ent_goal.insert(0, "1 2 3 4 5 6 7 8 0")
        self.ent_goal.pack(fill=tk.X, pady=(0, 15))

        # Speed Control Slider
        tk.Label(self.left_sidebar, text="AUTO PLAY SPEED (ms)", fg=TEXT_MUTED, bg=BG_PANEL, font=('Fixedsys', 10, 'bold')).pack(anchor=tk.W)
        self.slider_speed = tk.Scale(self.left_sidebar, from_=50, to=2000, orient=tk.HORIZONTAL, bg=BG_PANEL, fg=TEXT_MAIN,
                                     activebackground=ACCENT_BLUE, highlightthickness=0, relief=tk.FLAT, sliderlength=25)
        self.slider_speed.set(300) 
        self.slider_speed.pack(fill=tk.X, pady=(0, 20))

        # Global Action Button
        self.btn_control_frame = tk.Frame(self.left_sidebar, bg=BG_PANEL)
        self.btn_control_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_prev = tk.Button(self.btn_control_frame, text="◀ Prev Step", command=self.previous_step, 
                                  font=('Fixedsys', 11, 'bold'), bg=TEXT_MUTED, fg=BG_MAIN, relief=tk.FLAT, pady=8, cursor="hand2")
        self.btn_prev.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.btn_next = tk.Button(self.btn_control_frame, text="Next Step ▶", command=self.next_step, 
                                  font=('Fixedsys', 11, 'bold'), bg=ACCENT_GREEN, fg=BG_MAIN, relief=tk.FLAT, pady=8, cursor="hand2")
        self.btn_next.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self.btn_control_frame.columnconfigure(0, weight=1)
        self.btn_control_frame.columnconfigure(1, weight=1)

        self.btn_auto = tk.Button(self.left_sidebar, text="Auto Play ⏵", command=self.toggle_auto_play, 
                                  font=('Fixedsys', 13, 'bold'), bg=ACCENT_ORANGE, fg=BG_MAIN, relief=tk.FLAT, pady=10, cursor="hand2")
        self.btn_auto.pack(fill=tk.X, pady=(0, 15))

        self.btn_reset = tk.Button(self.left_sidebar, text="Apply Custom & Reset", command=self.apply_custom_input, 
                                   font=('Fixedsys', 11, 'bold'), bg=ACCENT_RED, fg=TEXT_MAIN, relief=tk.FLAT, pady=8, cursor="hand2")
        self.btn_reset.pack(fill=tk.X, pady=(0, 20))

        # Algorithm Documentation Area
        tk.Label(self.left_sidebar, text="ALGORITHM INFORMATION", fg=ACCENT_BLUE, bg=BG_PANEL, font=('Fixedsys', 11, 'bold')).pack(anchor=tk.W, pady=(5, 5))
        self.txt_docs = tk.Text(self.left_sidebar, font=('Fixedsys', 11), bg=BG_MAIN, fg=TEXT_MAIN, relief=tk.FLAT, wrap=tk.WORD, padx=10, pady=10)
        self.txt_docs.pack(fill=tk.BOTH, expand=True) # Cho phép giãn nở chiếm hết phần dư dưới cùng

        # ==========================================
        # RIGHT COLUMN: ACADEMIC CHAPTER TABS
        # ==========================================
        self.right_container = tk.Frame(self.root, bg=BG_MAIN)
        self.right_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=10)

        self.notebook = ttk.Notebook(self.right_container)
        self.notebook.pack(fill=tk.X, pady=(0, 10))
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.tab_uninformed = tk.Frame(self.notebook, bg=BG_MAIN)
        self.tab_informed = tk.Frame(self.notebook, bg=BG_MAIN)
        self.tab_local = tk.Frame(self.notebook, bg=BG_MAIN)
        self.tab_complex = tk.Frame(self.notebook, bg=BG_MAIN)
        self.tab_csp = tk.Frame(self.notebook, bg=BG_MAIN)
        self.tab_adversarial = tk.Frame(self.notebook, bg=BG_MAIN)

        self.notebook.add(self.tab_uninformed, text="Ch1: Uninformed")
        self.notebook.add(self.tab_informed, text="Ch2: Informed")
        self.notebook.add(self.tab_local, text="Ch3: Local")
        self.notebook.add(self.tab_complex, text="Ch4: Complex")
        self.notebook.add(self.tab_csp, text="Ch5: CSP")
        self.notebook.add(self.tab_adversarial, text="Ch6: Adversarial")

        self.cb_uninformed = ttk.Combobox(self.tab_uninformed, state="readonly", font=('Fixedsys', 12), width=50)
        self.cb_uninformed['values'] = [
            "BFS (Breadth-First Search)", 
            "DFS (Depth-First Search)", 
            "IDS (Iterative Deepening Search)", 
            "UCS (Uniform Cost Search)"
        ]
        self.cb_uninformed.current(0)
        self.cb_uninformed.pack(anchor=tk.W, padx=15, pady=15)
        self.cb_uninformed.bind("<<ComboboxSelected>>", lambda e: self.reset_environment())

        self.cb_informed = ttk.Combobox(self.tab_informed, state="readonly", font=('Fixedsys', 12), width=50)
        self.cb_informed['values'] = [
            "Greedy Search (Manhattan)", 
            "A* Search (Inversions + Misplaced)", 
            "IDA* Search (Manhattan + Misplaced)"]
        self.cb_informed.current(1) 
        self.cb_informed.pack(anchor=tk.W, padx=15, pady=15)
        self.cb_informed.bind("<<ComboboxSelected>>", lambda e: self.reset_environment())

        self.cb_local = ttk.Combobox(self.tab_local, state="readonly", font=('Fixedsys', 12), width=50)
        self.cb_local['values'] = [
            "Simple Hill Climbing (Manhattan)", 
            "Steepest-Ascent Hill Climbing (Manhattan)", 
            "Stochastic Hill Climbing (Manhattan)", 
            "Random Restart Hill Climbing (Manhattan)", 
            "Local Beam Search (k=2)", 
            "Simulated Annealing (Manhattan)"]
        self.cb_local.current(0)
        self.cb_local.pack(anchor=tk.W, padx=15, pady=15)
        self.cb_local.bind("<<ComboboxSelected>>", lambda e: self.reset_environment())

        self.cb_complex = ttk.Combobox(self.tab_complex, state="readonly", font=('Fixedsys', 12), width=50)
        self.cb_complex['values'] = [
            "Searching with no observation (Has Goal)", 
            "Searching with no observation (No Goal)", 
            "Searching for partially observable problems",
            "AND-OR Search (Non-deterministic)"
        ]
        self.cb_complex.current(0)
        self.cb_complex.pack(anchor=tk.W, padx=15, pady=15)
        self.cb_complex.bind("<<ComboboxSelected>>", lambda e: self.reset_environment())

        self.cb_csp = ttk.Combobox(self.tab_csp, state="readonly", font=('Fixedsys', 12), width=50)
        self.cb_csp['values'] = [
            "Backtracking Search (8-Puzzle CSP)",
            "Backtracking + Forward Checking (8-Puzzle CSP)",
            "AC-3 Search (8-Puzzle CSP)",
            "Min-Conflicts Search (8-Puzzle CSP)"
        ]
        self.cb_csp.current(0)
        self.cb_csp.pack(anchor=tk.W, padx=15, pady=15)
        self.cb_csp.bind("<<ComboboxSelected>>", lambda e: self.reset_environment())

        self.cb_adversarial = ttk.Combobox(self.tab_adversarial, state="readonly", font=('Fixedsys', 12), width=50)
        self.cb_adversarial['values'] = [
            "Minimax Search (Tic-Tac-Toe Demo)"
        ]
        self.cb_adversarial.current(0)
        self.cb_adversarial.pack(anchor=tk.W, padx=15, pady=15)
        self.cb_adversarial.bind("<<ComboboxSelected>>", lambda e: self.reset_environment())

        # --- SHARED WORKSPACE DISPLAY PANELS ---
        self.frontier_frame = tk.Frame(self.right_container, bg=BG_MAIN, pady=5)
        self.frontier_frame.pack(fill=tk.X, padx=15)
        self.frontier_strip_visible = True
        
        self.lbl_frontier_title = tk.Label(self.frontier_frame, text="Frontier (Queue):", fg=TEXT_MUTED, bg=BG_MAIN, font=('Fixedsys', 12, 'bold'))
        self.lbl_frontier_title.pack(side=tk.LEFT, padx=5)
        
        self.frontier_boards = []
        for _ in range(10): 
            bw = BoardWidget(self.frontier_frame, size="mini")
            bw.pack(side=tk.LEFT, padx=5)
            self.frontier_boards.append(bw)

        # --- CORE WORKSPACE: MATRIX EXPANSION & PATH LISTBOXES ---
        self.workspace_frame = tk.Frame(self.right_container, bg=BG_MAIN)
        self.workspace_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # KHU VỰC ĐỒ HỌA
        self.center_wrapper = tk.Frame(self.workspace_frame, bg=BG_PANEL)
        self.center_wrapper.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

        self.expand_frame = tk.Frame(self.center_wrapper, bg=BG_PANEL)
        self.expand_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        def create_node_with_cost(row, col, padx=0, pady=0, bd=2):
            wrapper = tk.Frame(self.expand_frame, bg=BG_PANEL)
            wrapper.grid(row=row, column=col, padx=padx, pady=pady)
            
            board = BoardWidget(wrapper, bd=bd)
            board.pack(side=tk.TOP)
            
            lbl = tk.Label(wrapper, text="", fg=HIGHLIGHT_GOLD, bg=BG_PANEL, font=('Consolas', 9, 'bold'))
            lbl.pack(side=tk.TOP, pady=(0, 0)) 
            return board, lbl

        self.node_up, self.lbl_up = create_node_with_cost(0, 1, pady=0)
        self.node_left, self.lbl_left = create_node_with_cost(1, 0, padx=15)
        self.node_center, self.lbl_center = create_node_with_cost(1, 1, padx=4, pady=2, bd=3)
        self.node_right, self.lbl_right = create_node_with_cost(1, 2, padx=15)
        self.node_down, self.lbl_down = create_node_with_cost(2, 1, pady=0)

        self.and_or_tree_frame = tk.Frame(self.center_wrapper, bg=BG_PANEL)
        self.and_or_tree_canvas = tk.Canvas(
            self.and_or_tree_frame,
            bg=BG_PANEL,
            highlightthickness=0,
            xscrollincrement=20,
            yscrollincrement=20
        )
        self.and_or_tree_xscroll = tk.Scrollbar(
            self.and_or_tree_frame,
            orient=tk.HORIZONTAL,
            command=self.and_or_tree_canvas.xview
        )
        self.and_or_tree_yscroll = tk.Scrollbar(
            self.and_or_tree_frame,
            orient=tk.VERTICAL,
            command=self.and_or_tree_canvas.yview
        )
        self.and_or_tree_canvas.configure(
            xscrollcommand=self.and_or_tree_xscroll.set,
            yscrollcommand=self.and_or_tree_yscroll.set
        )
        self.and_or_tree_canvas.grid(row=0, column=0, sticky="nsew")
        self.and_or_tree_yscroll.grid(row=0, column=1, sticky="ns")
        self.and_or_tree_xscroll.grid(row=1, column=0, sticky="ew")
        self.and_or_tree_frame.rowconfigure(0, weight=1)
        self.and_or_tree_frame.columnconfigure(0, weight=1)

        # KHU VỰC LISTBOX
        self.path_container = tk.Frame(self.workspace_frame, bg=BG_MAIN, width=380)
        self.path_container.pack(side=tk.RIGHT, fill=tk.Y)
        self.path_container.pack_propagate(False)

        tk.Label(self.path_container, text="Current Path", fg=ACCENT_BLUE, bg=BG_MAIN, font=('Fixedsys', 12, 'bold')).pack(anchor=tk.W)
        self.current_path_listbox = tk.Listbox(self.path_container, font=('Fixedsys', 11), bg=BG_PANEL, fg=TEXT_MAIN, relief=tk.FLAT, height=15, highlightthickness=0)
        self.current_path_listbox.pack(fill=tk.X, pady=(0, 15))

        tk.Label(self.path_container, text="Final Solution", fg=ACCENT_GREEN, bg=BG_MAIN, font=('Fixedsys', 12, 'bold')).pack(anchor=tk.W)
        self.path_listbox = tk.Listbox(self.path_container, font=('Fixedsys', 11), bg=BG_PANEL, fg=TEXT_MAIN, relief=tk.FLAT, highlightthickness=0)
        self.path_listbox.pack(fill=tk.BOTH, expand=True)
        self.path_listbox.bind('<<ListboxSelect>>', self.on_path_select)

        # Bottom Thanh Thống kê thông số
        self.lbl_stats = tk.Label(self.right_container, text="Ready", fg=HIGHLIGHT_GOLD, bg=BG_MAIN, font=('Fixedsys', 13, 'bold'), pady=8)
        self.lbl_stats.pack(fill=tk.X)

    # Hàm dọn dẹp tất cả các ô xung quanh và xóa nhãn Cost
    def clear_neighbors(self):
        for widget in [self.node_up, self.node_down, self.node_left, self.node_right]:
            widget.update_board(None)
            widget.config(bg=BG_PANEL)
        for lbl in [self.lbl_up, self.lbl_down, self.lbl_left, self.lbl_right]:
            lbl.config(text="")

    def set_and_or_tree_visible(self, visible):
        if visible:
            self.expand_frame.place_forget()
            self.and_or_tree_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        else:
            self.and_or_tree_frame.place_forget()
            self.expand_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def set_frontier_strip_visible(self, visible):
        if visible and not self.frontier_strip_visible:
            self.frontier_frame.pack(fill=tk.X, padx=15, before=self.workspace_frame)
            self.frontier_strip_visible = True
        elif not visible and self.frontier_strip_visible:
            self.frontier_frame.pack_forget()
            self.frontier_strip_visible = False

    def set_tree_scrollbars_visible(self, horizontal=True, vertical=True):
        if horizontal:
            self.and_or_tree_xscroll.grid()
        else:
            self.and_or_tree_xscroll.grid_remove()

        if vertical:
            self.and_or_tree_yscroll.grid()
        else:
            self.and_or_tree_yscroll.grid_remove()

    def is_csp_algorithm(self, algo_name=None):
        name = algo_name if algo_name is not None else self.get_current_algo_name()
        return "Backtracking Search" in name or "CSP" in name

    def is_belief_algorithm(self, algo_name=None):
        name = algo_name if algo_name is not None else self.get_current_algo_name()
        return "observation" in name or "observable" in name

    def is_adversarial_algorithm(self, algo_name=None):
        name = algo_name if algo_name is not None else self.get_current_algo_name()
        return "Minimax" in name

    def get_complex_initial_belief(self, algo_name):
        if self.manual_belief_input and len(self.initial_belief_states) > 1:
            return list(self.initial_belief_states)

        if "Has Goal" in algo_name:
            anchor = self.goal_board
            reason = "Auto Belief State: no observed initial board, generated around CUSTOM GOAL BOARD."
        elif "No Goal" in algo_name:
            anchor = self.goal_board
            reason = "Auto Belief State: no goal is used by the solver; CUSTOM GOAL BOARD is only a seed for hidden states."
        else:
            anchor = self.goal_board
            reason = "Auto Belief State: partial observation starts from several possible hidden boards."

        self.auto_belief_reason = reason
        return make_auto_belief(anchor)

    def board_to_lines(self, board):
        rows = []
        for row in range(3):
            values = []
            for col in range(3):
                value = board[row * 3 + col]
                values.append("_" if value == 0 else str(value))
            rows.append(" ".join(values))
        return rows

    def draw_tree_board(self, x, y, board, title, fill_color, outline_color, subtitle=""):
        canvas = self.and_or_tree_canvas
        width, height = 138, 118
        canvas.create_rectangle(
            x - width // 2,
            y - height // 2,
            x + width // 2,
            y + height // 2,
            fill=fill_color,
            outline=outline_color,
            width=3
        )
        canvas.create_text(x, y - 42, text=title, fill=TEXT_MAIN, font=("Fixedsys", 10, "bold"))
        for index, line in enumerate(self.board_to_lines(board)):
            canvas.create_text(x, y - 12 + index * 20, text=line, fill=TEXT_MAIN, font=("Consolas", 13, "bold"))
        if subtitle:
            canvas.create_text(x, y + 45, text=subtitle, fill=TEXT_MUTED, font=("Fixedsys", 8))

    def draw_tictactoe_node(self, canvas, x, y, node, active_node_id=None, best_path_ids=None):
        best_path_ids = best_path_ids or []
        width, height = 92, 112
        is_active = node["id"] == active_node_id
        is_on_best_path = node["id"] in best_path_ids
        role = "MAX" if node["player"] == "X" else "MIN"

        fill = "#26344d" if role == "MAX" else "#3b2f1f"
        outline = ACCENT_BLUE if role == "MAX" else ACCENT_ORANGE
        if node["is_terminal"]:
            outline = ACCENT_GREEN if node["value"] == 10 else ACCENT_RED if node["value"] == -10 else HIGHLIGHT_GOLD
        if is_on_best_path:
            outline = ACCENT_GREEN
        if is_active:
            outline = HIGHLIGHT_GOLD

        canvas.create_rectangle(
            x - width // 2,
            y - height // 2,
            x + width // 2,
            y + height // 2,
            fill=fill,
            outline=outline,
            width=4 if is_active or is_on_best_path else 2
        )
        label = f"N{node['id']} {role}"
        if node["move"]:
            label += f" m{node['move']}"
        canvas.create_text(x, y - 45, text=label, fill=TEXT_MAIN, font=("Fixedsys", 8, "bold"))

        cell = 22
        start_x = x - cell * 3 // 2
        start_y = y - 29
        for row in range(3):
            for col in range(3):
                idx = row * 3 + col
                x1 = start_x + col * cell
                y1 = start_y + row * cell
                x2 = x1 + cell
                y2 = y1 + cell
                canvas.create_rectangle(x1, y1, x2, y2, fill="#1e293b", outline="#64748b", width=1)
                mark = node["board"][idx]
                if mark:
                    color = ACCENT_BLUE if mark == "X" else ACCENT_ORANGE
                    canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=mark, fill=color, font=("Consolas", 12, "bold"))

        value = "?" if node["value"] is None else node["value"]
        canvas.create_text(x, y + 43, text=f"value = {value}", fill=HIGHLIGHT_GOLD, font=("Fixedsys", 8, "bold"))

    def get_minimax_move_path(self, node, node_by_id):
        moves = []
        current = node
        while current and current["parent_id"] is not None:
            moves.append(current["move"])
            current = node_by_id.get(current["parent_id"])
        return tuple(reversed(moves))

    def get_minimax_demo_positions(self, nodes, node_by_id):
        layout = {
            (): (560, 320),
            (7,): (250, 500),
            (8,): (560, 500),
            (9,): (870, 500),
            (7, 8): (160, 690),
            (7, 9): (340, 690),
            (7, 9, 8): (340, 875),
            (8, 7): (470, 690),
            (8, 7, 9): (470, 875),
            (8, 9): (650, 690),
            (8, 9, 7): (650, 875),
        }
        positions = {}
        for node in nodes:
            path = self.get_minimax_move_path(node, node_by_id)
            positions[node["id"]] = layout.get(path, (120 + len(positions) * 120, 320 + node["depth"] * 185))
        return positions

    def get_minimax_step_explanation(self, snapshot, node_by_id):
        event_kind = snapshot.get("event_kind", "start")
        active_node = node_by_id.get(snapshot.get("active_node_id"))
        active_child = node_by_id.get(snapshot.get("active_child_id"))

        if event_kind == "visit" and active_node:
            role = "MAX" if active_node["player"] == "X" else "MIN"
            return (
                "1. VISIT",
                f"Thuật toán đi xuống Node {active_node['id']} ({role}) để xét trạng thái bàn cờ này."
            )
        if event_kind == "terminal" and active_node:
            return (
                "2. TERMINAL",
                f"Node {active_node['id']} là lá: tính utility ngay. X thắng=+10, hòa=0, O thắng=-10."
            )
        if event_kind == "return" and active_node and active_child:
            value = "?" if active_child["value"] is None else active_child["value"]
            return (
                "3. RETURN VALUE",
                f"Node {active_child['id']} đã có value={value}, trả ngược kết quả này về Node {active_node['id']}."
            )
        if event_kind == "choose" and active_node:
            role = "MAX" if active_node["player"] == "X" else "MIN"
            child_values = []
            for child_id in active_node["children"]:
                child = node_by_id[child_id]
                child_value = "?" if child["value"] is None else child["value"]
                child_values.append(f"N{child_id}:{child_value}")
            rule = "lấy giá trị lớn nhất" if role == "MAX" else "lấy giá trị nhỏ nhất"
            return (
                "4. CHOOSE",
                f"Node {active_node['id']} là {role}, nên {rule} trong [{', '.join(child_values)}]."
            )
        if event_kind == "success":
            return (
                "DONE",
                "Root đã có value cuối cùng. Đường xanh là nước đi tối ưu nếu cả hai bên chơi tốt nhất."
            )
        return (
            "START",
            "Bấm Next Step: Minimax sẽ đi xuống các lá trước, sau đó truyền utility ngược lên gốc."
        )

    def draw_minimax_tree(self, snapshot):
        canvas = self.and_or_tree_canvas
        old_x = canvas.xview()[0] if canvas.xview() else 0
        old_y = canvas.yview()[0] if canvas.yview() else 0
        canvas.delete("all")
        self.set_tree_scrollbars_visible(horizontal=True, vertical=True)

        nodes = snapshot.get("nodes", []) if snapshot else []
        if not nodes:
            canvas.create_text(440, 240, text="Bấm Next Step để chạy Minimax.", fill=TEXT_MUTED, font=("Fixedsys", 15, "bold"))
            canvas.configure(scrollregion=(0, 0, 900, 520))
            return

        node_by_id = {node["id"]: node for node in nodes}
        levels = {}
        for node in nodes:
            levels.setdefault(node["depth"], []).append(node)

        positions = self.get_minimax_demo_positions(nodes, node_by_id)

        active_node_id = snapshot.get("active_node_id")
        active_child_id = snapshot.get("active_child_id")
        best_path_ids = snapshot.get("best_path_ids", [])
        step_title, step_detail = self.get_minimax_step_explanation(snapshot, node_by_id)
        view_width = max(760, canvas.winfo_width())
        content_width = max(1120, view_width)
        text_width = max(640, min(1040, view_width - 60))

        canvas.create_rectangle(0, 0, content_width, 245, fill=BG_PANEL, outline="#334155", width=2)
        canvas.create_text(
            20,
            18,
            anchor=tk.W,
            text="MINIMAX TREE",
            fill=HIGHLIGHT_GOLD,
            font=("Fixedsys", 12, "bold")
        )
        canvas.create_text(
            20,
            43,
            anchor=tk.W,
            text="MAX = X chọn giá trị lớn nhất  |  MIN = O chọn giá trị nhỏ nhất  |  move k = đánh vào ô k",
            fill=HIGHLIGHT_GOLD,
            font=("Fixedsys", 10, "bold"),
            width=text_width
        )
        canvas.create_text(20, 72, anchor=tk.W, text=snapshot.get("message", ""), fill=TEXT_MUTED, font=("Fixedsys", 10), width=text_width)
        canvas.create_text(
            20,
            100,
            anchor=tk.W,
            text="Utility: X thắng = +10, hòa = 0, O thắng = -10. Value chỉ xuất hiện sau khi node lá được xét.",
            fill=ACCENT_BLUE,
            font=("Fixedsys", 9, "bold"),
            width=text_width
        )
        canvas.create_rectangle(20, 125, view_width - 25, 170, fill="#0f172a", outline="#475569", width=1)
        canvas.create_text(34, 140, anchor=tk.W, text=step_title, fill=HIGHLIGHT_GOLD, font=("Fixedsys", 10, "bold"))
        canvas.create_text(160, 140, anchor=tk.W, text=step_detail, fill=TEXT_MAIN, font=("Fixedsys", 9), width=max(460, view_width - 220))

        canvas.create_rectangle(20, 180, view_width - 25, 230, fill="#0f172a", outline="#475569", width=1)
        canvas.create_text(34, 195, anchor=tk.W, text="Cách đọc node", fill=ACCENT_GREEN, font=("Fixedsys", 10, "bold"))
        canvas.create_text(190, 195, anchor=tk.W, text="N7 MAX m7 = node 7, lượt X, vừa đánh ô 7", fill=TEXT_MUTED, font=("Fixedsys", 8), width=max(320, view_width - 230))
        canvas.create_text(190, 215, anchor=tk.W, text="value=? là chưa biết; viền xanh là đường tối ưu sau khi xong", fill=TEXT_MUTED, font=("Fixedsys", 8), width=max(320, view_width - 230))

        for node in nodes:
            parent_id = node["parent_id"]
            if parent_id is None:
                continue
            x1, y1 = positions[parent_id]
            x2, y2 = positions[node["id"]]
            parent = node_by_id[parent_id]
            edge_color = ACCENT_BLUE if parent["player"] == "X" else ACCENT_RED
            if parent_id in best_path_ids and node["id"] in best_path_ids:
                edge_color = ACCENT_GREEN
            width = 4 if edge_color == ACCENT_GREEN or node["id"] == active_child_id else 2
            if node["id"] == active_child_id:
                edge_color = HIGHLIGHT_GOLD
            canvas.create_line(x1, y1 + 58, x2, y2 - 58, fill=edge_color, width=width, arrow=tk.LAST)
            canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2 - 8, text=f"move {node['move']}", fill=edge_color, font=("Fixedsys", 7, "bold"))

        for node in nodes:
            x, y = positions[node["id"]]
            self.draw_tictactoe_node(canvas, x, y, node, active_node_id, best_path_ids)

        scroll_w = content_width
        scroll_h = 1010
        canvas.configure(scrollregion=(0, 0, scroll_w, scroll_h))
        if snapshot.get("event_kind") == "start":
            canvas.xview_moveto(0)
            canvas.yview_moveto(0)
        else:
            canvas.xview_moveto(old_x)
            canvas.yview_moveto(old_y)

    def draw_and_or_tree(self, tree_snapshot):
        canvas = self.and_or_tree_canvas
        canvas.delete("all")
        self.set_tree_scrollbars_visible(horizontal=True, vertical=True)

        if not tree_snapshot:
            canvas.create_text(
                440,
                240,
                text="Bấm Next Step để dựng cây AND-OR.",
                fill=TEXT_MUTED,
                font=("Fixedsys", 15, "bold")
            )
            canvas.configure(scrollregion=(0, 0, 900, 520))
            return

        width = max(900, self.and_or_tree_canvas.winfo_width())
        center_x = width // 2
        root_y = 92
        action_y = 255
        outcome_y = 430

        canvas.create_text(
            20,
            18,
            anchor=tk.W,
            text="AND-OR TREE VIEW  |  OR: AI chọn hành động  |  AND: môi trường sinh mọi kết quả",
            fill=HIGHLIGHT_GOLD,
            font=("Fixedsys", 12, "bold")
        )

        note = tree_snapshot.get("note", "")
        if note:
            canvas.create_text(20, 43, anchor=tk.W, text=note, fill=TEXT_MUTED, font=("Fixedsys", 10))

        depth = tree_snapshot.get("depth", 0)
        self.draw_tree_board(
            center_x,
            root_y,
            tree_snapshot["root"],
            "OR STATE",
            "#26344d",
            ACCENT_BLUE,
            f"depth = {depth}"
        )

        action = tree_snapshot.get("action")
        outcomes = tree_snapshot.get("outcomes", [])
        if not action:
            canvas.create_text(
                center_x,
                260,
                text="OR node đang chờ thuật toán thử các hành động UP, DOWN, LEFT, RIGHT.",
                fill=TEXT_MUTED,
                font=("Fixedsys", 12)
            )
            canvas.configure(scrollregion=(0, 0, width, 540))
            return

        diamond_w, diamond_h = 120, 72
        canvas.create_line(center_x, root_y + 60, center_x, action_y - diamond_h // 2, fill=TEXT_MUTED, width=2, arrow=tk.LAST)
        canvas.create_polygon(
            center_x,
            action_y - diamond_h // 2,
            center_x + diamond_w // 2,
            action_y,
            center_x,
            action_y + diamond_h // 2,
            center_x - diamond_w // 2,
            action_y,
            fill="#3b2f1f",
            outline=ACCENT_ORANGE,
            width=3
        )
        canvas.create_text(center_x, action_y - 10, text="AND", fill=TEXT_MAIN, font=("Fixedsys", 12, "bold"))
        canvas.create_text(center_x, action_y + 12, text=f"Action: {action}", fill=HIGHLIGHT_GOLD, font=("Fixedsys", 10, "bold"))

        if not outcomes:
            canvas.create_text(center_x, outcome_y, text="Chưa có outcome từ môi trường.", fill=TEXT_MUTED, font=("Fixedsys", 12))
            canvas.configure(scrollregion=(0, 0, width, 540))
            return

        spacing = 190
        total_width = spacing * (len(outcomes) - 1)
        start_x = center_x - total_width // 2
        max_x = width

        for index, board in enumerate(outcomes):
            x = start_x + index * spacing
            max_x = max(max_x, x + 110)
            canvas.create_line(center_x, action_y + diamond_h // 2, x, outcome_y - 62, fill=TEXT_MUTED, width=2, arrow=tk.LAST)
            self.draw_tree_board(
                x,
                outcome_y,
                board,
                f"OUTCOME {index + 1}",
                "#1f3a2d",
                ACCENT_GREEN if board == self.goal_board else TEXT_MUTED,
                "must solve"
            )

        canvas.configure(scrollregion=(0, 0, max_x + 80, 570))

    def draw_compact_board(self, canvas, x, y, board, title="", outline=TEXT_MUTED, fill="#26344d", subtitle=""):
        width, height = 94, 102
        canvas.create_rectangle(
            x,
            y,
            x + width,
            y + height,
            fill=fill,
            outline=outline,
            width=2
        )
        if title:
            canvas.create_text(x + 8, y + 10, anchor=tk.W, text=title, fill=HIGHLIGHT_GOLD, font=("Fixedsys", 8, "bold"))

        cell = 24
        start_x = x + 11
        start_y = y + 24
        for row in range(3):
            for col in range(3):
                value = board[row * 3 + col]
                x1 = start_x + col * cell
                y1 = start_y + row * cell
                x2 = x1 + cell - 2
                y2 = y1 + cell - 2
                tile_fill = "#34495e" if value != 0 else "#26344d"
                canvas.create_rectangle(x1, y1, x2, y2, fill=tile_fill, outline="#516174", width=1)
                if value != 0:
                    canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=str(value), fill=TEXT_MAIN, font=("Consolas", 11, "bold"))

        if subtitle:
            canvas.create_text(x + width // 2, y + 92, text=subtitle, fill=TEXT_MUTED, font=("Fixedsys", 7))

    def draw_belief_boards(self, canvas, boards, x, y, max_items=8, columns=4, title_prefix="S"):
        boards = sorted(boards)
        for index, board in enumerate(boards[:max_items]):
            row, col = divmod(index, columns)
            self.draw_compact_board(
                canvas,
                x + col * 112,
                y + row * 118,
                board,
                f"{title_prefix}{index + 1}",
                outline=ACCENT_BLUE
            )

        if len(boards) > max_items:
            row, col = divmod(max_items, columns)
            canvas.create_text(
                x + col * 112 + 44,
                y + row * 118 + 48,
                text=f"+{len(boards) - max_items} more",
                fill=TEXT_MUTED,
                font=("Fixedsys", 10, "bold")
            )

    def draw_belief_state(self, data):
        canvas = self.and_or_tree_canvas
        canvas.delete("all")
        self.set_tree_scrollbars_visible(horizontal=False, vertical=False)

        current_node = data.get("current", getattr(self.solver, "initial_node", None)) if data else getattr(self.solver, "initial_node", None)
        current_boards = sorted(current_node.boards) if current_node and hasattr(current_node, "boards") else []
        algo_name = self.get_current_algo_name()
        mode_title = "PARTIALLY OBSERVABLE SEARCH" if "observable" in algo_name else "SENSORLESS SEARCH"
        goal_text = "Goal: not used" if "No Goal" in algo_name else f"Goal: {self.format_board_inline(self.goal_board)}"

        canvas.create_text(
            20,
            18,
            anchor=tk.W,
            text=f"{mode_title}  |  Belief State = set of possible hidden boards",
            fill=HIGHLIGHT_GOLD,
            font=("Fixedsys", 12, "bold")
        )
        canvas.create_text(20, 43, anchor=tk.W, text=goal_text, fill=TEXT_MUTED, font=("Fixedsys", 9, "bold"))
        if getattr(self, "auto_belief_reason", "") and not self.manual_belief_input:
            canvas.create_text(20, 66, anchor=tk.W, text=self.auto_belief_reason, fill=ACCENT_BLUE, font=("Fixedsys", 9, "bold"))

        canvas.create_text(
            20,
            102,
            anchor=tk.W,
            text=f"Current Belief State |B| = {len(current_boards)}",
            fill=ACCENT_GREEN,
            font=("Fixedsys", 12, "bold")
        )
        self.draw_belief_boards(canvas, current_boards, 20, 125, max_items=8, columns=4, title_prefix="B")

        children_info = data.get("children_info", {}) if data else {}
        action_y = 395
        canvas.create_text(20, action_y - 28, anchor=tk.W, text="Action results", fill=ACCENT_ORANGE, font=("Fixedsys", 12, "bold"))

        if not children_info:
            canvas.create_text(
                20,
                action_y + 20,
                anchor=tk.W,
                text="Bấm Next Step để sinh kết quả cho từng action.",
                fill=TEXT_MUTED,
                font=("Fixedsys", 11)
            )
        else:
            for index, move in enumerate(("UP", "DOWN", "LEFT", "RIGHT")):
                info = children_info.get(move)
                x = 20 + index * 230
                if not info:
                    canvas.create_rectangle(x, action_y, x + 205, action_y + 178, fill="#1b2536", outline="#334155", width=2)
                    canvas.create_text(x + 102, action_y + 82, text=move, fill="#526176", font=("Fixedsys", 13, "bold"))
                    continue

                child_node = info["node"]
                child_boards = sorted(child_node.boards)
                status = info.get("type", "new")
                outline = ACCENT_GREEN if status == "new" else ACCENT_RED
                if status == "success":
                    outline = HIGHLIGHT_GOLD

                canvas.create_rectangle(x, action_y, x + 205, action_y + 178, fill="#1b2536", outline=outline, width=3)
                canvas.create_text(x + 10, action_y + 16, anchor=tk.W, text=f"{move}  -> |B'|={len(child_boards)}", fill=TEXT_MAIN, font=("Fixedsys", 10, "bold"))
                canvas.create_text(x + 10, action_y + 38, anchor=tk.W, text=status.upper(), fill=outline, font=("Fixedsys", 9, "bold"))

                percepts = info.get("percepts")
                if percepts:
                    canvas.create_text(x + 10, action_y + 60, anchor=tk.W, text=f"observations: {len(percepts)}", fill=ACCENT_BLUE, font=("Fixedsys", 8, "bold"))
                    for p_idx, percept in enumerate(percepts[:2]):
                        canvas.create_text(x + 10, action_y + 82 + p_idx * 22, anchor=tk.W, text=f"obs {p_idx + 1}: |B|={len(percept)}", fill=TEXT_MUTED, font=("Fixedsys", 8))
                    if len(percepts) > 2:
                        canvas.create_text(x + 10, action_y + 126, anchor=tk.W, text=f"+{len(percepts) - 2} obs more", fill=TEXT_MUTED, font=("Fixedsys", 8))
                elif child_boards:
                    self.draw_compact_board(canvas, x + 55, action_y + 58, child_boards[0], "rep", outline=outline)
                    if len(child_boards) > 1:
                        canvas.create_text(x + 102, action_y + 165, text=f"+{len(child_boards) - 1} possible boards", fill=TEXT_MUTED, font=("Fixedsys", 8))

        frontier_count = data.get("frontier_count", 0) if data else 0
        canvas.create_text(
            20,
            590,
            anchor=tk.W,
            text=f"Frontier in memory: {frontier_count} belief node(s)",
            fill=TEXT_MUTED,
            font=("Fixedsys", 10, "bold")
        )

        canvas.configure(scrollregion=(0, 0, 980, 620))

    def draw_csp_state(self, snapshot):
        canvas = self.and_or_tree_canvas
        canvas.delete("all")
        self.set_tree_scrollbars_visible(horizontal=True, vertical=True)

        assignment = snapshot.get("assignment", {})
        selected_var = snapshot.get("selected_var")
        peer_var = snapshot.get("peer_var")
        trying_value = snapshot.get("trying_value")
        stage = snapshot.get("stage", "start")
        variables = snapshot.get("variables", [])
        fixed_values = snapshot.get("fixed_values", {})
        current_domains = snapshot.get("current_domains", snapshot.get("domains", {}))
        current_arc = snapshot.get("current_arc")
        removed_values = snapshot.get("removed_values", [])
        queue_preview = snapshot.get("queue_preview", [])
        queue_size = snapshot.get("queue_size", 0)
        conflicted_vars = snapshot.get("conflicted_vars", [])
        candidate_scores = snapshot.get("candidate_scores", {})
        total_conflicts = snapshot.get("total_conflicts")
        local_step = snapshot.get("local_step", 0)
        max_steps = snapshot.get("max_steps", 0)
        is_ac3 = "AC-3" in self.get_current_algo_name()
        is_min_conflicts = "Min-Conflicts" in self.get_current_algo_name()

        canvas.create_text(
            20,
            18,
            anchor=tk.W,
            text=(
                "AC-3 ARC CONSISTENCY  |  8-Puzzle CSP"
                if is_ac3
                else "MIN-CONFLICTS LOCAL SEARCH  |  8-Puzzle CSP"
                if is_min_conflicts
                else "CSP BACKTRACKING SEARCH  |  8-Puzzle Cell Assignment"
            ),
            fill=HIGHLIGHT_GOLD,
            font=("Fixedsys", 12, "bold")
        )
        canvas.create_text(
            20,
            44,
            anchor=tk.W,
            text=snapshot.get("message", ""),
            fill=TEXT_MUTED,
            font=("Fixedsys", 10)
        )

        start_x, start_y = 120, 100
        cell = 110

        for index, var in enumerate(variables):
            row, col = divmod(index, 3)
            x1 = start_x + col * cell
            y1 = start_y + row * cell
            x2 = x1 + cell - 10
            y2 = y1 + cell - 10

            value = assignment.get(var)
            shown_value = "_" if value is None else str(value)
            target_value = fixed_values.get(var)

            fill = "#26344d"
            outline = HIGHLIGHT_GOLD if var == selected_var else TEXT_MUTED
            width = 5 if var == selected_var else 2
            if is_min_conflicts and var in conflicted_vars:
                outline = ACCENT_RED
                width = 4
            if is_min_conflicts and var == selected_var:
                outline = HIGHLIGHT_GOLD
                fill = "#3b2f1f"
                width = 5
            if is_ac3 and var == peer_var:
                outline = ACCENT_BLUE
                width = 4
            if var == selected_var and trying_value is not None and stage == "reject":
                outline = ACCENT_RED
                fill = "#3b1f2a"
            elif var == selected_var and trying_value is not None and stage in ["consistent", "success"]:
                outline = ACCENT_GREEN
                fill = "#1f3a2d"
            elif is_ac3 and var == selected_var and removed_values:
                outline = ACCENT_RED
                fill = "#3b1f2a"
            elif is_ac3 and var == selected_var:
                outline = HIGHLIGHT_GOLD

            canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=width)
            canvas.create_text(x1 + 16, y1 + 14, text=var, fill=TEXT_MUTED, font=("Fixedsys", 9, "bold"))
            canvas.create_text(x1 + 50, y1 + 50, text=shown_value, fill=TEXT_MAIN, font=("Consolas", 26, "bold"))
            canvas.create_text(x1 + 50, y1 + 82, text=f"target={target_value}", fill=TEXT_MUTED, font=("Fixedsys", 8))

        domain_x = 540
        canvas.create_text(domain_x, 92, anchor=tk.W, text="Domain of each xi", fill=ACCENT_BLUE, font=("Fixedsys", 13, "bold"))
        canvas.create_text(domain_x, 125, anchor=tk.W, text="{0, 1, 2, 3, 4, 5, 6, 7, 8}", fill=TEXT_MAIN, font=("Consolas", 12, "bold"))
        domain_order = snapshot.get("domain_order", [])
        if is_ac3:
            arc_text = f"Current arc: {current_arc}" if current_arc else "Current arc: waiting"
            random_order_text = arc_text
        elif is_min_conflicts:
            random_order_text = f"Local step: {local_step}/{max_steps} | total conflicts = {total_conflicts}"
        else:
            random_order_text = f"Random order: {domain_order}" if domain_order else "Random order: waiting for SELECT"
        canvas.create_text(domain_x, 155, anchor=tk.W, text=random_order_text, fill=HIGHLIGHT_GOLD, font=("Consolas", 10, "bold"))

        if is_ac3:
            canvas.create_text(domain_x, 205, anchor=tk.W, text="AC-3 Queue + Revision", fill=ACCENT_GREEN, font=("Fixedsys", 13, "bold"))
            canvas.create_text(domain_x, 235, anchor=tk.W, text=f"Queue size: {queue_size}", fill=TEXT_MAIN, font=("Fixedsys", 10))
            removed_text = f"Removed from D({selected_var}): {removed_values}" if selected_var else "Removed: []"
            canvas.create_text(domain_x, 262, anchor=tk.W, text=removed_text, fill=ACCENT_RED if removed_values else TEXT_MUTED, font=("Fixedsys", 10))
            queue_text = ", ".join(str(arc) for arc in queue_preview[:4])
            if len(queue_preview) > 4:
                queue_text += f", ... +{len(queue_preview) - 4}"
            canvas.create_text(domain_x, 289, anchor=tk.W, text=f"Next arcs: {queue_text if queue_text else '[]'}", fill=TEXT_MUTED, font=("Fixedsys", 9))
        elif is_min_conflicts:
            canvas.create_text(domain_x, 205, anchor=tk.W, text="Min-Conflicts Repair", fill=ACCENT_GREEN, font=("Fixedsys", 13, "bold"))
            canvas.create_text(domain_x, 235, anchor=tk.W, text=f"Conflicted vars: {conflicted_vars}", fill=ACCENT_RED if conflicted_vars else ACCENT_GREEN, font=("Fixedsys", 10))
            if stage == "evaluate_conflict":
                chosen_text = f"Testing: {selected_var} = {trying_value}"
            elif stage == "select_conflicted":
                chosen_text = f"Selected var: {selected_var}; evaluating D({selected_var})"
            elif selected_var:
                chosen_text = f"Set: {selected_var} = {trying_value}"
            else:
                chosen_text = "Selected var: waiting"
            canvas.create_text(domain_x, 262, anchor=tk.W, text=chosen_text, fill=HIGHLIGHT_GOLD, font=("Fixedsys", 10))
            score_items = sorted(candidate_scores.items(), key=lambda item: item[0])
            score_text = ", ".join(f"{value}:{score}" for value, score in score_items[:9])
            canvas.create_text(domain_x, 289, anchor=tk.W, text=f"CONFLICTS(v): {score_text if score_text else 'waiting'}", fill=TEXT_MUTED, font=("Consolas", 9, "bold"))
        else:
            canvas.create_text(domain_x, 205, anchor=tk.W, text="Constraints C", fill=ACCENT_GREEN, font=("Fixedsys", 13, "bold"))
            canvas.create_text(domain_x, 235, anchor=tk.W, text="1. Each xi has exactly one value.", fill=TEXT_MAIN, font=("Fixedsys", 10))
            canvas.create_text(domain_x, 262, anchor=tk.W, text="2. All xi values are different.", fill=TEXT_MAIN, font=("Fixedsys", 10))
            canvas.create_text(domain_x, 289, anchor=tk.W, text="3. xi must match its goal cell.", fill=TEXT_MAIN, font=("Fixedsys", 10))

        canvas.create_text(domain_x, 330, anchor=tk.W, text="Assignment + Current Domains", fill=HIGHLIGHT_GOLD, font=("Fixedsys", 13, "bold"))
        for idx, var in enumerate(variables):
            value = assignment.get(var, "-")
            row, col = divmod(idx, 3)
            target = fixed_values.get(var)
            domain_values = current_domains.get(var, [])
            domain_text = "fixed" if value != "-" else str(domain_values)
            canvas.create_text(
                domain_x,
                365 + idx * 24,
                anchor=tk.W,
                text=f"{var} ({row},{col}) = {value}  target:{target}  D:{domain_text}",
                fill=TEXT_MAIN if value != "-" else TEXT_MUTED,
                font=("Consolas", 9, "bold")
            )

        canvas.create_text(
            20,
            565,
            anchor=tk.W,
            text=(
                "AC-3 formulation: queue = all directed arcs (Xi, Xj); revise removes values with no support."
                if is_ac3
                else "Min-Conflicts formulation: start complete, pick conflicted var, set value with minimum conflicts."
                if is_min_conflicts
                else "CSP formulation: X = {x1...x9}, D = {0...8}, C = all-different + fixed goal-cell constraints."
            ),
            fill=TEXT_MUTED,
            font=("Fixedsys", 10)
        )
        canvas.configure(scrollregion=(0, 0, 980, 620))

    def update_csp_ui(self, data):
        snapshot = data.get("csp_snapshot")
        if snapshot:
            self.draw_csp_state(snapshot)

        self.clear_neighbors()
        for bw in self.frontier_boards:
            bw.update_board(None)

        assignment = snapshot.get("assignment", {}) if snapshot else {}
        assigned_count = len(assignment)
        if "AC-3" in self.get_current_algo_name() and snapshot:
            arc = snapshot.get("current_arc") or "waiting"
            queue_size = snapshot.get("queue_size", 0)
            removed = snapshot.get("removed_values", [])
            self.lbl_stats.config(
                text=f"Step: {self.step_count} | Arc: {arc} | Queue: {queue_size} | Removed: {removed}",
                fg=TEXT_MUTED
            )
        elif "Min-Conflicts" in self.get_current_algo_name() and snapshot:
            local_step = snapshot.get("local_step", 0)
            max_steps = snapshot.get("max_steps", 0)
            conflicts = snapshot.get("total_conflicts", 0)
            selected_var = snapshot.get("selected_var") or "waiting"
            self.lbl_stats.config(
                text=f"Step: {local_step}/{max_steps} | Conflicts: {conflicts} | Selected: {selected_var}",
                fg=TEXT_MUTED
            )
        else:
            self.lbl_stats.config(
                text=f"Step: {self.step_count} | Assigned: {assigned_count}/9 | Stage: {snapshot.get('stage', 'N/A') if snapshot else 'N/A'}",
                fg=TEXT_MUTED
            )

        if data["status"] == "failure":
            self.btn_next.config(state=tk.DISABLED)
            self.btn_auto.config(state=tk.DISABLED)
            self.lbl_stats.config(text="CSP FAILED: NO CONSISTENT ASSIGNMENT FOUND", fg=ACCENT_RED)
            self.solution_path = []
            self.path_listbox.delete(0, tk.END)
            self.path_listbox.insert(tk.END, "No solution found")
            return

        if data["status"] == "success":
            self.btn_next.config(state=tk.DISABLED)
            self.btn_auto.config(state=tk.DISABLED)
            if "AC-3" in self.get_current_algo_name():
                self.lbl_stats.config(text="AC-3 DONE: QUEUE EMPTY, DOMAINS ARE ARC-CONSISTENT", fg=ACCENT_GREEN)
            elif "Min-Conflicts" in self.get_current_algo_name():
                self.lbl_stats.config(text="MIN-CONFLICTS SOLVED: NO CONFLICT REMAINS", fg=ACCENT_GREEN)
            else:
                self.lbl_stats.config(text="CSP SOLVED: COMPLETE 8-PUZZLE CELL ASSIGNMENT", fg=ACCENT_GREEN)
            self.solution_path = []
            self.path_listbox.delete(0, tk.END)

            path = data.get("path", [])
            for idx, node in enumerate(path):
                text = f"Step {idx:02d}: " + (node.move if node.move else "START")
                self.path_listbox.insert(tk.END, text)
                self.solution_path.append({
                    "text": text,
                    "csp_snapshot": {
                        "variables": self.solver.variables,
                        "domains": self.solver.domains,
                        "positions": self.solver.positions,
                        "fixed_values": self.solver.fixed_values,
                        "assignment": dict(node.assignment),
                        "board": node.board,
                        "stage": "success",
                        "selected_var": None,
                        "trying_value": None,
                        "message": text
                    }
                })
            return

    def apply_custom_input(self):
        raw_initial = self.ent_input.get().strip()
        raw_goal = self.ent_goal.get().strip() 
        try:
            parts_goal = [int(x) for x in raw_goal.split() if x.strip() != ""]
            if len(parts_goal) != 9 or set(parts_goal) != set(range(9)):
                raise ValueError("Bảng cờ đích phải đúng 9 số từ 0-8!")
            self.goal_board = tuple(parts_goal)
            
            if raw_initial == "":
                if self.is_belief_algorithm(self.get_current_algo_name()):
                    self.initial_belief_states = []
                    self.initial_board = self.goal_board
                    self.manual_belief_input = False
                    self.reset_environment()
                    messagebox.showinfo("Thành công", "Đã để trống input và dùng Belief State tự động cho môi trường phức tạp.")
                    return
                raise ValueError("Bảng cờ ban đầu không được để trống với thuật toán trạng thái đơn!")

            initial_strings = raw_initial.split(',')
            self.initial_belief_states = []
            
            for state_str in initial_strings:
                parts = [int(x) for x in state_str.split() if x.strip() != ""]
                if len(parts) != 9 or set(parts) != set(range(9)):
                    raise ValueError("Mỗi bảng cờ phải đúng 9 số từ 0-8!")
                self.initial_belief_states.append(tuple(parts))
                
            self.initial_board = self.initial_belief_states[0] 
            self.manual_belief_input = len(self.initial_belief_states) > 1
            self.reset_environment()
            messagebox.showinfo("Thành công", f"Đã nạp {len(self.initial_belief_states)} trạng thái đầu vào!")
        except Exception as e:
            messagebox.showerror("Lỗi dữ liệu", f"Lỗi: {str(e)}\n\nNếu nhập nhiều ma trận Belief State, hãy dùng dấu phẩy.\nVí dụ: 1 2 3 4 0 6 7 5 8, 1 2 3 4 5 6 7 0 8")
    
    def get_current_algo_name(self):
        tab_idx = self.notebook.index(self.notebook.select())
        if tab_idx == 0: return self.cb_uninformed.get()
        if tab_idx == 1: return self.cb_informed.get()
        if tab_idx == 2: return self.cb_local.get()
        if tab_idx == 3: return self.cb_complex.get()
        if tab_idx == 4: return self.cb_csp.get()
        if tab_idx == 5: return self.cb_adversarial.get()
        return ""

    def on_tab_changed(self, event):
        self.reset_environment()

    def create_solver_for_current_selection(self):
        selected_algo_name = self.get_current_algo_name()
        SolverClass = self.algorithms[selected_algo_name]

        if self.is_csp_algorithm(selected_algo_name):
            return SolverClass(self.initial_board, goal_board=self.goal_board)

        if self.is_belief_algorithm(selected_algo_name):
            belief_states = self.get_complex_initial_belief(selected_algo_name)
            return SolverClass(belief_states, goal_board=self.goal_board)

        return SolverClass(self.initial_board, goal_board=self.goal_board)

    def make_solver_history_snapshot(self):
        try:
            return copy.deepcopy(self.solver)
        except TypeError:
            pass

        selected_algo_name = self.get_current_algo_name()
        can_replay = (
            "AND-OR" in selected_algo_name
            or self.is_belief_algorithm(selected_algo_name)
            or self.is_csp_algorithm(selected_algo_name)
        )
        if not can_replay:
            return None

        replay_solver = self.create_solver_for_current_selection()
        for _ in range(self.step_count):
            replay_solver.step()
        return replay_solver

    def make_data_history_snapshot(self):
        try:
            return copy.deepcopy(self.current_state_data)
        except Exception:
            return self.current_state_data

    def reset_environment(self):
        self.is_auto_playing = False
        self.btn_auto.config(text="Auto Play ⏵", bg=ACCENT_ORANGE, state=tk.NORMAL)
        self.btn_next.config(state=tk.NORMAL)
        
        self.step_count = 0
        self.solution_path = []
        self.current_state_data = None
        self.path_listbox.delete(0, tk.END)
        self.current_path_listbox.delete(0, tk.END)
        self.clear_neighbors()
        for bw in self.frontier_boards:
            bw.update_board(None)

        selected_algo_name = self.get_current_algo_name()
        is_csp = self.is_csp_algorithm(selected_algo_name)
        is_belief = self.is_belief_algorithm(selected_algo_name)
        is_adversarial = self.is_adversarial_algorithm(selected_algo_name)
        self.lbl_initial_title.config(text="CUSTOM INITIAL BOARD (OPTIONAL)" if is_belief else "CUSTOM INITIAL BOARD")
        self.set_and_or_tree_visible("AND-OR" in selected_algo_name or is_csp or is_belief or is_adversarial)
        self.set_frontier_strip_visible(not ("AND-OR" in selected_algo_name or is_csp or is_belief or is_adversarial))
        
        self.solver = self.create_solver_for_current_selection()

        self.txt_docs.delete("1.0", tk.END)
        
        if is_adversarial:
            self.lbl_frontier_title.config(text="Game Tree:")
            self.txt_docs.insert("1.0", self.algo_docs["Minimax"])
        elif is_csp:
            self.lbl_frontier_title.config(text="CSP Assignment:")
            if "AC-3" in selected_algo_name:
                doc_key = "AC-3 CSP"
            elif "Min-Conflicts" in selected_algo_name:
                doc_key = "Min-Conflicts CSP"
            elif "Forward Checking" in selected_algo_name:
                doc_key = "Forward Checking CSP"
            else:
                doc_key = "Backtracking CSP"
            self.txt_docs.insert("1.0", self.algo_docs[doc_key])
        elif "AND-OR" in selected_algo_name or is_belief: 
            if "AND-OR" in selected_algo_name:
                self.lbl_frontier_title.config(text="Erratic Environment:")
                self.txt_docs.insert("1.0", self.algo_docs["AND-OR"])
            else:
                self.lbl_frontier_title.config(text="Current Belief State -> :")
                if "No Goal" in selected_algo_name:
                    self.txt_docs.insert("1.0", self.algo_docs["Sensorless (No Goal)"])
                elif "observable" in selected_algo_name:
                    self.txt_docs.insert("1.0", self.algo_docs["Partially Observable"])
                else:
                    self.txt_docs.insert("1.0", self.algo_docs["Sensorless (Goal)"])
        elif "Stochastic" in selected_algo_name:
            self.lbl_frontier_title.config(text="Better Neighbors:")
            self.txt_docs.insert("1.0", self.algo_docs["Stochastic HC"])
        elif "Beam Search" in selected_algo_name:
            self.lbl_frontier_title.config(text="Current State Set -> Neighbors:")
            self.txt_docs.insert("1.0", self.algo_docs["Beam Search"])
        elif "Annealing" in selected_algo_name:
            self.lbl_frontier_title.config(text="Generated Neighbor:") 
            self.txt_docs.insert("1.0", self.algo_docs["Simulated Annealing"])
        elif "Restart" in selected_algo_name:
            self.lbl_frontier_title.config(text="Better Neighbors:")
            self.txt_docs.insert("1.0", self.algo_docs["Restart HC"])
        elif "Hill Climbing" in selected_algo_name:
            self.lbl_frontier_title.config(text="Neighbors:")
            doc_key = "Simple HC" if "Simple" in selected_algo_name else "Steepest HC"
            self.txt_docs.insert("1.0", self.algo_docs[doc_key])
        else:
            if "DFS" in selected_algo_name or "IDS" in selected_algo_name:
                self.lbl_frontier_title.config(text="Frontier (Stack):")
            elif "BFS" in selected_algo_name:
                self.lbl_frontier_title.config(text="Frontier (Queue):")
            else:
                self.lbl_frontier_title.config(text="Frontier (Priority Queue):")

            # Chèn nội dung mã giả
            if "BFS" in selected_algo_name: self.txt_docs.insert("1.0", self.algo_docs["BFS"])
            elif "DFS" in selected_algo_name: self.txt_docs.insert("1.0", self.algo_docs["DFS"])
            elif "IDS" in selected_algo_name: self.txt_docs.insert("1.0", self.algo_docs["IDS"])
            elif "UCS" in selected_algo_name: self.txt_docs.insert("1.0", self.algo_docs["UCS"])
            elif "Greedy" in selected_algo_name: self.txt_docs.insert("1.0", self.algo_docs["Greedy"])
            elif "IDA*" in selected_algo_name: self.txt_docs.insert("1.0", self.algo_docs["IDA*"])
            elif "A*" in selected_algo_name: self.txt_docs.insert("1.0", self.algo_docs["A*"])

        if is_adversarial:
            self.draw_minimax_tree(self.solver.initial_snapshot())
            self.lbl_stats.config(text="Steps: 0 | Root: MAX | Utility: waiting", fg=TEXT_MUTED)
            self.ui_history = []
            self.btn_prev.config(state=tk.DISABLED)
            return

        if is_csp:
            self.draw_csp_state(self.solver.initial_snapshot())
            self.lbl_stats.config(text="Steps: 0 | Assigned: 0/9 | Stage: start", fg=TEXT_MUTED)
            self.ui_history = []
            self.btn_prev.config(state=tk.DISABLED)
            return

        if is_belief:
            initial_data = {
                "status": "start",
                "current": self.solver.initial_node,
                "frontier_preview": sorted(self.solver.initial_node.boards),
                "frontier_count": 1
            }
            self.draw_belief_state(initial_data)
            for index, board in enumerate(sorted(self.solver.initial_node.boards)[:len(self.frontier_boards)]):
                self.frontier_boards[index].update_board(board)
            b_size = len(self.solver.initial_node.boards)
            source = "Manual" if self.manual_belief_input and len(self.initial_belief_states) > 1 else "Auto"
            self.lbl_stats.config(text=f"Steps: 0 | {source} Belief State Size: {b_size} | Frontier: 1", fg=TEXT_MUTED)
            self.ui_history = []
            self.btn_prev.config(state=tk.DISABLED)
            return

        # Tự nhận diện Node mảng hay Node đơn
        first_board = list(self.solver.initial_node.boards)[0] if hasattr(self.solver.initial_node, 'boards') else self.solver.initial_node.board        
        self.node_center.update_board(first_board, highlight=True)
        self.node_center.config(bg="#a55b00")
        self.frontier_boards[0].update_board(first_board)
        if "AND-OR" in selected_algo_name:
            self.draw_and_or_tree(getattr(self.solver, "last_tree_snapshot", None))
        
        if "IDS" in selected_algo_name or "IDA*" in selected_algo_name:
            self.lbl_stats.config(text="Limit: 0 | Steps: 0 | Frontier: 1", fg=TEXT_MUTED)
        elif "Stochastic" in selected_algo_name or "Restart" in selected_algo_name:
            self.lbl_stats.config(text="Steps: 0 | Better Neighbors: 1", fg=TEXT_MUTED)
        elif "Hill Climbing" in selected_algo_name or "Beam Search" in selected_algo_name:
            self.lbl_stats.config(text="Steps: 0 | Neighbors: 1", fg=TEXT_MUTED)
        elif "Annealing" in selected_algo_name:
            self.lbl_stats.config(text="Steps: 0 | Generated Neighbor: 1", fg=TEXT_MUTED)
        elif "AND-OR" in selected_algo_name or "observation" in selected_algo_name or "observable" in selected_algo_name:
            # Tự động đếm kích thước mảng nếu có, nếu không thì mặc định là 1 (AND-OR)
            node = self.solver.initial_node
            b_size = len(node.boards) if hasattr(node, 'boards') else 1
            self.lbl_stats.config(text=f"Steps: 0 | Belief State Size: {b_size} | Frontier: 1", fg=TEXT_MUTED)
        else:
            self.lbl_stats.config(text="Steps: 0 | Reached: 1 | Frontier: 1", fg=TEXT_MUTED)
        
        self.ui_history = [] 
        self.btn_prev.config(state=tk.DISABLED)

    def next_step(self):
        solver_snapshot = self.make_solver_history_snapshot()
        data_snapshot = self.make_data_history_snapshot()

        if solver_snapshot is not None:
            self.ui_history.append((self.step_count, solver_snapshot, data_snapshot))
            self.btn_prev.config(state=tk.NORMAL)
        else:
            self.btn_prev.config(state=tk.DISABLED)

        self.step_count += 1
        state_data = self.solver.step()
        
        self.current_state_data = state_data 
        self.update_ui_from_state(state_data)
        self.track_current_path(state_data)

    def previous_step(self):
        if self.is_auto_playing:
            self.is_auto_playing = False
            self.btn_auto.config(text="Auto Play ⏵", bg=ACCENT_ORANGE)

        if not self.ui_history:
            return
        prev_step_count, prev_solver_state, prev_state_data = self.ui_history.pop()
        self.step_count = prev_step_count
        self.solver = prev_solver_state 
        self.current_state_data = prev_state_data
        
        if prev_state_data is None:
            self.reset_environment()
            return
        else:
            self.update_ui_from_state(prev_state_data)
            self.track_current_path(prev_state_data)
        
        if not self.ui_history:
            self.btn_prev.config(state=tk.DISABLED)
            
        self.btn_next.config(state=tk.NORMAL)
        self.btn_auto.config(state=tk.NORMAL)

    def track_current_path(self, data):
        if self.is_adversarial_algorithm():
            return

        self.current_path_listbox.delete(0, tk.END)
        if data is None or "current" not in data or data.get("status") in ["success", "failure"]:
            return
        
        temp_path = []
        curr = data["current"]
        while curr:
            temp_path.append(curr)
            curr = curr.parent
        temp_path.reverse()
        
        for idx, node in enumerate(temp_path):
            m_str = f"Step {idx:02d}: " + self.format_path_step_label(idx, node)
            self.current_path_listbox.insert(tk.END, m_str)
        self.current_path_listbox.see(tk.END) 

    def format_path_step_label(self, idx, node):
        move_val = getattr(node, 'move', None)
        if move_val:
            return str(move_val)

        if idx == 0:
            return "START"

        current_algo = self.get_current_algo_name()
        if "observable" in current_algo:
            return "SENSOR OBSERVATION"
        if self.is_belief_algorithm(current_algo):
            return "BELIEF UPDATE"

        return "START"

    def colorize_node(self, widget, lbl_widget, move_name, children_info, current_algo):
        if move_name not in children_info:
            widget.update_board(None) 
            widget.config(bg=BG_PANEL) 
            lbl_widget.config(text="")
            return
            
        info = children_info[move_name]
        node_obj = info["node"]
        board_data = list(node_obj.boards)[0] if hasattr(node_obj, 'boards') else node_obj.board
        widget.update_board(board_data)
        
        # BÓC TÁCH CHI PHÍ
        cost_str = ""
        if "A*" in current_algo or "IDA*" in current_algo:
            if hasattr(node_obj, 'g') and hasattr(node_obj, 'h') and hasattr(node_obj, 'f'):
                # Xử lý Dummy Node của A* (tránh in ra số 0)
                if node_obj.g == 0 and node_obj.h == 0 and info["type"] == "reached":
                    cost_str = "(Đã xét)"
                else:
                    cost_str = f"g:{node_obj.g} h:{node_obj.h} f:{node_obj.f}"
        elif "Hill Climbing" in current_algo:
            if hasattr(node_obj, 'h'):
                cost_str = f"h(n): {node_obj.h}"
        elif "Greedy" in current_algo or "UCS" in current_algo:
            if hasattr(self.solver, 'node_costs') and board_data in self.solver.node_costs:
                val = self.solver.node_costs[board_data]
                prefix = "h:" if "Greedy" in current_algo else "Cost:"
                cost_str = f"{prefix} {val}"
                
        lbl_widget.config(text=cost_str) 

        # Đổ màu trạng thái
        if info["type"] == "new":
            widget.config(bg=ACCENT_GREEN)      
        elif info["type"] == "reached":
            widget.config(bg=ACCENT_RED)      
        elif info["type"] == "success":
            widget.config(bg=HIGHLIGHT_GOLD)

    def add_solution_item(self, text, board=None):
        self.path_listbox.insert(tk.END, text)
        self.solution_path.append({"text": text, "board": board})

    def format_board_inline(self, board):
        rows = []
        for row in range(3):
            values = []
            for col in range(3):
                value = board[row * 3 + col]
                values.append("_" if value == 0 else str(value))
            rows.append(" ".join(values))
        return " / ".join(rows)

    def show_and_or_solution(self, plan, start_board):
        self.solution_path = []
        self.path_listbox.delete(0, tk.END)
        self.add_solution_item("Step 00: START", start_board)

        step_no = 1

        def walk(state, sub_plan, depth=0):
            nonlocal step_no
            indent = "  " * depth

            if sub_plan == []:
                self.add_solution_item(f"{indent}GOAL reached", state)
                return

            if isinstance(sub_plan, str):
                retry_text = sub_plan.replace("RETRY_FROM_DEPTH_", "retry from step ")
                self.add_solution_item(f"{indent}if slip/stay -> {retry_text}", state)
                return

            if not isinstance(sub_plan, list) or len(sub_plan) != 2:
                self.add_solution_item(f"{indent}{sub_plan}", state)
                return

            action, outcomes = sub_plan
            current_step = step_no
            self.add_solution_item(f"{indent}Step {current_step:02d}: TRY {action}", state)
            step_no += 1

            if not isinstance(outcomes, dict):
                return

            for outcome_board, outcome_plan in outcomes.items():
                outcome_label = self.format_board_inline(outcome_board)
                if outcome_board == state:
                    self.add_solution_item(
                        f"{indent}  if slip/stay -> retry Step {current_step:02d}",
                        outcome_board
                    )
                else:
                    self.add_solution_item(
                        f"{indent}  if success -> {outcome_label}",
                        outcome_board
                    )

                if outcome_board != state:
                    walk(outcome_board, outcome_plan, depth + 1)

        walk(start_board, plan)

    def update_belief_ui(self, data):
        self.draw_belief_state(data)
        self.clear_neighbors()

        preview = [board for board in data.get("frontier_preview", []) if board != "SEPARATOR"]
        for i, board_widget in enumerate(self.frontier_boards):
            if i < len(preview):
                board_widget.update_board(preview[i])
            else:
                board_widget.update_board(None)

        current_node = data.get("current")
        belief_size = len(current_node.boards) if current_node and hasattr(current_node, "boards") else 0
        self.lbl_stats.config(
            text=f"Step: {self.step_count} | Belief State Size: {belief_size} | Frontier: {data.get('frontier_count', 0)}",
            fg=TEXT_MUTED
        )

        if data["status"] == "failure":
            self.btn_next.config(state=tk.DISABLED)
            self.btn_auto.config(state=tk.DISABLED)
            self.lbl_stats.config(text="BELIEF SEARCH STOPPED: NO PLAN FOUND", fg=ACCENT_RED)
            return

        if data["status"] == "success":
            self.btn_next.config(state=tk.DISABLED)
            self.btn_auto.config(state=tk.DISABLED)
            final_size = len(data["solution_node"].boards)
            success_text = "BELIEF STATE REACHED GOAL" if "Has Goal" in self.get_current_algo_name() else "BELIEF STATE COLLAPSED TO ONE STATE"
            if "observable" in self.get_current_algo_name():
                success_text = "PARTIALLY OBSERVABLE PLAN FOUND"
            self.lbl_stats.config(text=f"{success_text} | Final |B| = {final_size}", fg=ACCENT_GREEN)

            self.path_listbox.delete(0, tk.END)
            self.solution_path = []

            if "plan" in data and "observable" in self.get_current_algo_name():
                def add_plan_line(text, boards=None):
                    self.path_listbox.insert(tk.END, text)
                    self.solution_path.append({"text": text, "belief_boards": boards})

                add_plan_line("Conditional plan found", sorted(data["solution_node"].boards))

                def walk_plan(plan, depth=0):
                    indent = "  " * depth
                    if plan == []:
                        add_plan_line(f"{indent}GOAL reached")
                        return
                    if not isinstance(plan, list) or len(plan) != 2:
                        add_plan_line(f"{indent}{plan}")
                        return

                    action, branches = plan
                    add_plan_line(f"{indent}TRY {action}")
                    if isinstance(branches, dict):
                        for index, (percept, sub_plan) in enumerate(branches.items(), start=1):
                            boards = sorted(percept)
                            add_plan_line(f"{indent}  if observation {index}: |B|={len(boards)}", boards)
                            walk_plan(sub_plan, depth + 2)
                    else:
                        walk_plan(branches, depth + 1)

                walk_plan(data["plan"])
                return

            self.solution_path = data.get("path", [])
            for idx, node in enumerate(self.solution_path):
                move_str = f"Step {idx:02d}: " + self.format_path_step_label(idx, node)
                if hasattr(node, "boards"):
                    move_str += f"  |B|={len(node.boards)}"
                self.path_listbox.insert(tk.END, move_str)

    def update_minimax_ui(self, data):
        snapshot = data.get("minimax_snapshot")
        self.draw_minimax_tree(snapshot)
        self.clear_neighbors()
        for bw in self.frontier_boards:
            bw.update_board(None)

        active_node_id = snapshot.get("active_node_id")
        event_kind = snapshot.get("event_kind", "start")
        active_node = None
        for node in snapshot.get("nodes", []):
            if node["id"] == active_node_id:
                active_node = node
                break

        self.current_path_listbox.delete(0, tk.END)
        self.current_path_listbox.insert(tk.END, f"Event: {event_kind}")
        self.current_path_listbox.insert(tk.END, snapshot.get("message", ""))
        if active_node:
            role = "MAX" if active_node["player"] == "X" else "MIN"
            value = "?" if active_node["value"] is None else active_node["value"]
            self.current_path_listbox.insert(tk.END, f"Node {active_node_id}: {role}, value={value}")

        root_value = "?"
        for node in snapshot.get("nodes", []):
            if node["id"] == snapshot.get("root_id"):
                root_value = "?" if node["value"] is None else node["value"]
                break

        self.lbl_stats.config(
            text=f"Step: {self.step_count} | Active Node: {active_node_id} | Root Utility: {root_value}",
            fg=TEXT_MUTED
        )

        if data["status"] == "success":
            self.btn_next.config(state=tk.DISABLED)
            self.btn_auto.config(state=tk.DISABLED)
            self.lbl_stats.config(text=f"MINIMAX DONE | Best utility for MAX = {root_value}", fg=ACCENT_GREEN)
            self.path_listbox.delete(0, tk.END)
            self.solution_path = []

            nodes_by_id = {node["id"]: node for node in snapshot.get("nodes", [])}
            for idx, node_id in enumerate(snapshot.get("best_path_ids", [])):
                node = nodes_by_id[node_id]
                role = "MAX" if node["player"] == "X" else "MIN"
                move = "ROOT" if node["move"] is None else f"move {node['move']}"
                value = "?" if node["value"] is None else node["value"]
                text = f"Step {idx:02d}: Node {node_id} | {role} | {move} | value={value}"
                self.path_listbox.insert(tk.END, text)
                selected_snapshot = copy.deepcopy(snapshot)
                selected_snapshot["active_node_id"] = node_id
                selected_snapshot["active_child_id"] = None
                self.solution_path.append({"text": text, "minimax_snapshot": selected_snapshot})

    def update_ui_from_state(self, data):
        if data is None:
            return

        current_algo = self.get_current_algo_name()
        if self.is_adversarial_algorithm(current_algo):
            self.update_minimax_ui(data)
            return

        if "AND-OR" in current_algo:
            self.draw_and_or_tree(data.get("tree_snapshot"))

        if self.is_csp_algorithm(current_algo):
            self.update_csp_ui(data)
            return

        if self.is_belief_algorithm(current_algo):
            self.update_belief_ui(data)
            return

        if data["status"] == "failure":
            self.lbl_stats.config(text="ALGORITHM STOPPED: NO PATH FOUND / STUCK IN LOCAL MAXIMUM!!!", fg=ACCENT_RED)
            self.btn_next.config(state=tk.DISABLED)
            self.btn_auto.config(state=tk.DISABLED)
            
            if "current" in data:
                err_board = list(data["current"].boards)[0] if hasattr(data["current"], 'boards') else data["current"].board
                self.node_center.update_board(err_board, highlight=True)
                self.node_center.config(bg=ACCENT_RED)
                self.clear_neighbors()
            return
            
        is_heuristic_only = "Hill Climbing" in current_algo or "Greedy" in current_algo
            
        current_board = list(data["current"].boards)[0] if hasattr(data["current"], 'boards') else data["current"].board
        self.node_center.update_board(current_board, highlight=True)
        self.node_center.config(bg="#a55b00")

        if data["status"] == "next_depth":
            self.clear_neighbors()
            self.lbl_stats.config(text=f"INCREASE THE LIMIT TO l = {data['current_l']}!", fg=HIGHLIGHT_GOLD)
            return

        if "children_info" in data:
            info = data["children_info"]
            self.colorize_node(self.node_up, self.lbl_up, 'UP', info, current_algo)
            self.colorize_node(self.node_down, self.lbl_down, 'DOWN', info, current_algo)
            self.colorize_node(self.node_left, self.lbl_left, 'LEFT', info, current_algo)
            self.colorize_node(self.node_right, self.lbl_right, 'RIGHT', info, current_algo)
        else:
            self.clear_neighbors()

        if data["status"] == "success":
            self.btn_next.config(state=tk.DISABLED)
            self.btn_auto.config(state=tk.DISABLED) 
            self.lbl_stats.config(text="THE GOAL HAS BEEN FOUND!!!", fg=ACCENT_GREEN)
            
            solution_node = data["solution_node"]
            # Nếu Node có chứa mảng '.boards' (Sensorless) thì bốc cái đầu tiên, nếu không thì lấy '.board' (AND-OR và các thuật toán cũ)
            current_board = list(solution_node.boards)[0] if hasattr(solution_node, 'boards') else solution_node.board
            self.node_center.update_board(current_board, highlight=True)
            self.node_center.config(bg=HIGHLIGHT_GOLD)
            
            self.clear_neighbors()
            self.path_listbox.delete(0, tk.END)

            # NẾU LÀ BÀI AND-OR TRẢ VỀ KẾ HOẠCH CÓ ĐIỀU KIỆN
            if "plan" in data:
                start_board = data["solution_node"].board
                self.show_and_or_solution(data["plan"], start_board)
                    
            # CÁC THUẬT TOÁN CÒN LẠI TRẢ VỀ ĐƯỜNG ĐI THẲNG 
            else:
                self.solution_path = data["path"]
                for idx, node in enumerate(self.solution_path):
                    move_str = f"Step {idx:02d}: " + self.format_path_step_label(idx, node)

                    if hasattr(node, 'f') and hasattr(node, 'h'): 
                        if is_heuristic_only:
                            move_str += f" (h = {node.h})"
                        else:
                            move_str += f" (f = {node.f})"
                    elif hasattr(self.solver, 'node_costs'):
                        cost_val = self.solver.node_costs.get(node.board, 0)
                        move_str += f" (Cost: {cost_val})"
                        
                    self.path_listbox.insert(tk.END, move_str)
            return

        frontier_list = data["frontier_preview"]
        for i in range(10):
            if i < len(frontier_list):
                self.frontier_boards[i].update_board(frontier_list[i])
            else:
                self.frontier_boards[i].update_board(None)

        stats_text = ""
        if "current_l" in data:
            # IDS
            reached_val = data.get('reached_count', 0)
            stats_text = f"Limit: {data['current_l']} | Step: {self.step_count} | Reached: {reached_val} | Frontier: {data['frontier_count']}"
        elif "Annealing" in current_algo:
            # Simulated Annealing
            h_val = data['current'].h if hasattr(data['current'], 'h') else "N/A"
            T_val = data.get('sa_T', 0)
            delta = data.get('sa_delta', 0)
            p_val = data.get('sa_p', 0)
            acc = data.get('sa_accepted', False)
            
            status_str = "ACCEPTED" if acc else "REJECTED"
            
            # Nếu tốt hơn (Delta âm)
            if delta < 0:
                stats_text = f"Step: {self.step_count} | T: {T_val:.2f} | Δ = {delta} (<0) -> {status_str} | h(n) = {h_val}"
            else:
                # Nếu tệ hơn (Delta dương), hiện cả Xác suất P
                stats_text = f"Step: {self.step_count} | T: {T_val:.2f} | Δ = {delta} | P = {p_val:.2f} -> {status_str} | h(n) = {h_val}"
            self.lbl_stats.config(text=stats_text, fg=TEXT_MUTED)

        elif "Beam Search" in current_algo:
            # Local Beam Search
            h_val = data['current'].h if hasattr(data['current'], 'h') else "N/A"
            k_val = data.get('beam_k', 2)
            stats_text = f"Step: {self.step_count} | Beam (k={k_val}) | Neighbors: {data['frontier_count']} | h(n) = {h_val}"
        elif "Hill Climbing" in current_algo:
            # Hill Climbing
            h_val = data['current'].h if hasattr(data['current'], 'h') else "N/A"
            restarts = data.get('restart_count', 0)
            restart_str = f" | Restarts: {restarts}" if "Restart" in current_algo else ""
            
            if "Stochastic" in current_algo or "Restart" in current_algo:
                stats_text = f"Step: {self.step_count} | Better Neighbors: {data['frontier_count']} | h(n) = {h_val}{restart_str}"
            else:
                stats_text = f"Step: {self.step_count} | Neighbors: {data['frontier_count']} | h(n) = {h_val}"
        elif hasattr(data["current"], 'f') and hasattr(data["current"], 'h'): 
            if "Greedy" in current_algo:
                # GREEDY
                stats_text = f"Step: {self.step_count} | Reached: {data.get('reached_count',0)} | Frontier: {data['frontier_count']} | h(n) = {data['current'].h}"
            else:
                # A* và IDA*
                stats_text = f"Step: {self.step_count} | Reached: {data.get('reached_count',0)} | Frontier: {data['frontier_count']} | f(n) = {data['current'].f}"
        elif hasattr(self.solver, 'node_costs'):
            # UCS
            current_cost = self.solver.node_costs.get(current_board, 0)
            stats_text = f"Step: {self.step_count} | Reached: {data.get('reached_count',0)} | Frontier: {data['frontier_count']} | Cost: {current_cost}"
        else:
            # Các thuật toán Uninformed còn lại
            stats_text = f"Step: {self.step_count} | Reached: {data.get('reached_count',0)} | Frontier: {data['frontier_count']}"
            
        self.lbl_stats.config(text=stats_text, fg=TEXT_MUTED)
    def on_path_select(self, event):
        selection = self.path_listbox.curselection()
        if selection:
            index = selection[0]
            selected_node = self.solution_path[index]
            if isinstance(selected_node, dict):
                if "minimax_snapshot" in selected_node:
                    self.draw_minimax_tree(selected_node["minimax_snapshot"])
                    return

                if "csp_snapshot" in selected_node:
                    self.draw_csp_state(selected_node["csp_snapshot"])
                    return

                if "belief_boards" in selected_node:
                    boards = selected_node.get("belief_boards") or []
                    if boards:
                        class SelectedBeliefNode:
                            def __init__(self, node_boards):
                                self.boards = frozenset(node_boards)

                        self.draw_belief_state({
                            "status": "selected",
                            "current": SelectedBeliefNode(boards),
                            "frontier_preview": sorted(boards),
                            "frontier_count": 0
                        })
                    return

                selected_board = selected_node.get("board")
                if selected_board is None:
                    return
                if "AND-OR" in self.get_current_algo_name():
                    self.draw_and_or_tree({
                        "root": selected_board,
                        "action": None,
                        "outcomes": [],
                        "depth": 0,
                        "note": selected_node["text"]
                    })
            else:
                if hasattr(selected_node, "boards") and self.is_belief_algorithm():
                    self.draw_belief_state({
                        "status": "selected",
                        "current": selected_node,
                        "frontier_preview": sorted(selected_node.boards),
                        "frontier_count": 0
                    })
                    return
                selected_board = list(selected_node.boards)[0] if hasattr(selected_node, 'boards') else selected_node.board
            self.node_center.update_board(selected_board, highlight=True)
            self.node_center.config(bg=HIGHLIGHT_GOLD) 
            
            self.clear_neighbors()

    def toggle_auto_play(self):
        if not self.is_auto_playing:
            self.is_auto_playing = True
            self.btn_auto.config(text="Stop ⏸", bg=ACCENT_RED) 
            self.btn_next.config(state=tk.DISABLED) 
            self.run_auto_step()
        else:
            self.is_auto_playing = False
            self.btn_auto.config(text="Auto Play ⏵", bg=ACCENT_ORANGE)

            if self.current_state_data and self.current_state_data.get("status") in ["success", "failure"]:
                self.btn_next.config(state=tk.DISABLED)
                self.btn_auto.config(state=tk.DISABLED)
            else:
                self.btn_next.config(state=tk.NORMAL)
                self.btn_auto.config(state=tk.NORMAL)

    def run_auto_step(self):
        if self.is_auto_playing:
            self.next_step()
            
            if self.current_state_data and self.current_state_data.get("status") not in ["success", "failure"]:
                speed = self.slider_speed.get()
                self.root.after(speed, self.run_auto_step) 
            else:
                self.toggle_auto_play()
    
if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
