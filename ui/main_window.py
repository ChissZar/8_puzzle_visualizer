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
            "Simulated Annealing (Manhattan)": SimulatedAnnealingSolver
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
            "Simulated Annealing": "== SIMULATED ANNEALING ==\n- Cảm hứng: Quá trình tôi luyện kim loại.\n- Cơ chế: Chọn ngẫu nhiên 1 lân cận.\n  + Δ < 0 (TỐT HƠN): Chấp nhận luôn (Ô XANH LÁ).\n  + Δ >= 0 (TỆ HƠN): Không bỏ qua ngay, mà chấp nhận với xác suất P = exp(-Δ/T) (Ô VÀNG GOLD), hoặc Từ chối (Ô ĐỎ).\n- Ý nghĩa: Nhiệt độ T càng cao (lúc mới chạy), thuật toán càng 'dễ dãi' đi vào đường xấu (Màu Vàng) để thoát khỏi cực đại cục bộ. T giảm dần, nó sẽ khắt khe hơn."        }
        
        self.solver = None 
        self.setup_ui()
        self.reset_environment()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=BG_MAIN, borderwidth=0)
        style.configure('TNotebook.Tab', background=BG_PANEL, foreground=TEXT_MUTED, font=('Fixedsys', 11, 'bold'), padding=[15, 8])
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
        tk.Label(self.left_sidebar, text="CUSTOM INITIAL BOARD", fg=HIGHLIGHT_GOLD, bg=BG_PANEL, font=('Fixedsys', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
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

        self.notebook.add(self.tab_uninformed, text="Chapter 1: Uninformed Search")
        self.notebook.add(self.tab_informed, text="Chapter 2: Informed Search")
        self.notebook.add(self.tab_local, text="Chapter 3: Local Search")

        self.cb_uninformed = ttk.Combobox(self.tab_uninformed, state="readonly", font=('Fixedsys', 12), width=50)
        self.cb_uninformed['values'] = ["BFS (Breadth-First Search)", "DFS (Depth-First Search)", "IDS (Iterative Deepening Search)", "UCS (Uniform Cost Search)"]
        self.cb_uninformed.current(0)
        self.cb_uninformed.pack(anchor=tk.W, padx=15, pady=15)
        self.cb_uninformed.bind("<<ComboboxSelected>>", lambda e: self.reset_environment())

        self.cb_informed = ttk.Combobox(self.tab_informed, state="readonly", font=('Fixedsys', 12), width=50)
        self.cb_informed['values'] = ["Greedy Search (Manhattan)", "A* Search (Inversions + Misplaced)", "IDA* Search (Manhattan + Misplaced)"]
        self.cb_informed.current(1) 
        self.cb_informed.pack(anchor=tk.W, padx=15, pady=15)
        self.cb_informed.bind("<<ComboboxSelected>>", lambda e: self.reset_environment())

        self.cb_local = ttk.Combobox(self.tab_local, state="readonly", font=('Fixedsys', 12), width=50)
        self.cb_local['values'] = ["Simple Hill Climbing (Manhattan)", "Steepest-Ascent Hill Climbing (Manhattan)", "Stochastic Hill Climbing (Manhattan)", "Random Restart Hill Climbing (Manhattan)", "Local Beam Search (k=2)", "Simulated Annealing (Manhattan)"]
        self.cb_local.current(0)
        self.cb_local.pack(anchor=tk.W, padx=15, pady=15)
        self.cb_local.bind("<<ComboboxSelected>>", lambda e: self.reset_environment())

        # --- SHARED WORKSPACE DISPLAY PANELS ---
        self.frontier_frame = tk.Frame(self.right_container, bg=BG_MAIN, pady=5)
        self.frontier_frame.pack(fill=tk.X, padx=15)
        
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

    def apply_custom_input(self):
        raw_initial = self.ent_input.get().strip()
        raw_goal = self.ent_goal.get().strip() 
        try:
            parts_initial = [int(x) for x in raw_initial.split() if x.strip() != ""]
            parts_goal = [int(x) for x in raw_goal.split() if x.strip() != ""]
            
            if len(parts_initial) != 9 or len(parts_goal) != 9:
                raise ValueError("Bắt buộc phải nhập đúng 9 số cho mỗi ô cờ!")
            if set(parts_initial) != set(range(9)) or set(parts_goal) != set(range(9)):
                raise ValueError("Bảng cờ phải chứa các số từ 0 đến 8 không trùng lặp!")
            
            self.initial_board = tuple(parts_initial)
            self.goal_board = tuple(parts_goal)
            self.reset_environment()
            messagebox.showinfo("Thành công", f"Đã áp dụng thông số mới!\nStart: {self.initial_board}\nGoal: {self.goal_board}")
        except Exception as e:
            messagebox.showerror("Lỗi dữ liệu", f"Chuỗi nhập không hợp lệ: {str(e)}\n\nĐịnh dạng đúng ví dụ: 1 2 3 4 0 6 7 5 8")

    def get_current_algo_name(self):
        tab_idx = self.notebook.index(self.notebook.select())
        if tab_idx == 0: return self.cb_uninformed.get()
        if tab_idx == 1: return self.cb_informed.get()
        return self.cb_local.get()

    def on_tab_changed(self, event):
        self.reset_environment()

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
        
        all_solvers = {}
        for k, v in self.algorithms.items():
            all_solvers[k] = v
        SolverClass = all_solvers[selected_algo_name]
        self.solver = SolverClass(self.initial_board, goal_board=self.goal_board)

        self.txt_docs.delete("1.0", tk.END)
        if "Stochastic" in selected_algo_name:
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

        self.node_center.update_board(self.solver.initial_node.board, highlight=True)
        self.node_center.config(bg="#a55b00")
        self.frontier_boards[0].update_board(self.solver.initial_node.board)
        
        if "IDS" in selected_algo_name or "IDA*" in selected_algo_name:
            self.lbl_stats.config(text="Limit: 0 | Steps: 0 | Frontier: 1", fg=TEXT_MUTED)
        elif "Stochastic" in selected_algo_name or "Restart" in selected_algo_name:
            self.lbl_stats.config(text="Steps: 0 | Better Neighbors: 1", fg=TEXT_MUTED)
        elif "Hill Climbing" in selected_algo_name or "Beam Search" in selected_algo_name:
            self.lbl_stats.config(text="Steps: 0 | Neighbors: 1", fg=TEXT_MUTED)
        elif "Annealing" in selected_algo_name:
            self.lbl_stats.config(text="Steps: 0 | Generated Neighbor: 1", fg=TEXT_MUTED)
        else:
            self.lbl_stats.config(text="Steps: 0 | Reached: 1 | Frontier: 1", fg=TEXT_MUTED)
        
        self.ui_history = [] 
        self.btn_prev.config(state=tk.DISABLED)

    def next_step(self):
        solver_snapshot = copy.deepcopy(self.solver)
        self.ui_history.append((self.step_count, solver_snapshot, self.current_state_data))
        self.btn_prev.config(state=tk.NORMAL) 

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
            m_val = getattr(node, 'move', None)
            m_str = f"Step {idx:02d}: " + (str(m_val) if m_val else "START")
            self.current_path_listbox.insert(tk.END, m_str)
        self.current_path_listbox.see(tk.END) 

    def colorize_node(self, widget, lbl_widget, move_name, children_info, current_algo):
        if move_name not in children_info:
            widget.update_board(None) 
            widget.config(bg=BG_PANEL) 
            lbl_widget.config(text="")
            return
            
        info = children_info[move_name]
        node_obj = info["node"]
        board_data = node_obj.board
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

    def update_ui_from_state(self, data):
        if data is None:
            return

        if data["status"] == "failure":
            self.lbl_stats.config(text="ALGORITHM STOPPED: NO PATH FOUND / STUCK IN LOCAL MAXIMUM!!!", fg=ACCENT_RED)
            self.btn_next.config(state=tk.DISABLED)
            self.btn_auto.config(state=tk.DISABLED)
            
            if "current" in data:
                self.node_center.update_board(data["current"].board, highlight=True)
                self.node_center.config(bg=ACCENT_RED)
                self.clear_neighbors()
            return
            
        current_algo = self.get_current_algo_name()
        is_heuristic_only = "Hill Climbing" in current_algo or "Greedy" in current_algo
            
        current_board = data["current"].board
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

        if data["status"] == "success":
            self.btn_next.config(state=tk.DISABLED)
            self.btn_auto.config(state=tk.DISABLED) 
            self.lbl_stats.config(text="THE GOAL HAS BEEN FOUND!!!", fg=ACCENT_GREEN)
            
            current_board = data["solution_node"].board
            self.node_center.update_board(current_board, highlight=True)
            self.node_center.config(bg=HIGHLIGHT_GOLD)
            
            self.clear_neighbors()
            
            self.solution_path = data["path"]
            self.path_listbox.delete(0, tk.END)
            for idx, node in enumerate(self.solution_path):
                move_val = getattr(node, 'move')
                move_str = f"Step {idx:02d}: " + (str(move_val) if move_val else "START")

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
            self.node_center.update_board(selected_node.board, highlight=True)
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