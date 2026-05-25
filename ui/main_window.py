import copy
import tkinter as tk
from tkinter import ttk
from logic.bfs_solver import BFSSolver
from logic.dfs_solver import DFSSolver
from logic.ids_solver import IDSSolver
from logic.ucs_solver import UCSSolver
from ui.board_widget import BoardWidget

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Search Visualizer")
        self.root.configure(bg="#2c3e50")
        
        self.is_auto_playing = False
        self.solution_path = []
        self.step_count = 0
        
        self.initial_board = (1, 2, 3, 
                              4, 0, 6, 
                              7, 5, 8) 
        
        # Từ điển ánh xạ Tên Thuật Toán -> Class Solver
        self.algorithms = {
            "BFS (Breadth-First Search)": BFSSolver,
            "DFS (Depth-First Search)": DFSSolver,
            "IDS (Iterative Deepening Search)": IDSSolver,
            "UCS (Uniform Cost Search)": UCSSolver 
        }
        
        self.solver = None # Sẽ được khởi tạo khi gọi reset_environment()

        self.setup_ui()
        self.reset_environment() # Khởi tạo lần đầu chạy app

    def setup_ui(self):
        # --- TOP FRAME: CHỌN THUẬT TOÁN ---
        self.header_frame = tk.Frame(self.root, bg="#34495e", pady=10, bd=2, relief=tk.RAISED)
        self.header_frame.pack(fill=tk.X)

        tk.Label(self.header_frame, text="Algorithm:", fg="white", bg="#34495e", font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=10)
        
        self.combo_algo = ttk.Combobox(self.header_frame, values=list(self.algorithms.keys()), state="readonly", width=35, font=('Arial', 11))
        self.combo_algo.current(0) # Mặc định chọn BFS
        self.combo_algo.pack(side=tk.LEFT, padx=10)

        self.btn_reset = tk.Button(self.header_frame, text="Apply & Reset", command=self.reset_environment, 
                                  font=('Arial', 11, 'bold'), bg="#c0392b", fg="white")
        self.btn_reset.pack(side=tk.LEFT, padx=10)

        # --- FRONTIER FRAME ---
        self.frontier_frame = tk.Frame(self.root, bg="#2c3e50", pady=10)
        self.frontier_frame.pack(fill=tk.X)
        
        tk.Label(self.frontier_frame, text="Frontier:", fg="white", bg="#2c3e50", font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=10)
        
        self.frontier_boards = []
        for _ in range(5): 
            bw = BoardWidget(self.frontier_frame, size="mini")
            bw.pack(side=tk.LEFT, padx=5)
            self.frontier_boards.append(bw)

        # --- BODY FRAME ---
        self.body_frame = tk.Frame(self.root, bg="#2c3e50")
        self.body_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        self.expand_frame = tk.Frame(self.body_frame, bg="#34495e", padx=15, pady=15, relief=tk.SUNKEN, bd=3)
        self.expand_frame.grid(row=0, column=0, padx=10, sticky="nsew")

        self.node_up = BoardWidget(self.expand_frame, bd=4)
        self.node_up.grid(row=0, column=1, pady=5)
        self.node_left = BoardWidget(self.expand_frame, bd=4)
        self.node_left.grid(row=1, column=0, padx=5)
        self.node_center = BoardWidget(self.expand_frame, bd=4)
        self.node_center.grid(row=1, column=1, padx=15, pady=15)
        self.node_right = BoardWidget(self.expand_frame, bd=4)
        self.node_right.grid(row=1, column=2, padx=5)
        self.node_down = BoardWidget(self.expand_frame, bd=4)
        self.node_down.grid(row=2, column=1, pady=5)

        self.path_frame = tk.Frame(self.body_frame, bg="#34495e", padx=15, pady=15, relief=tk.SUNKEN, bd=3)
        self.path_frame.grid(row=0, column=1, padx=10, sticky="nsew")

        tk.Label(self.path_frame, text="Solution Path:", fg="white", bg="#34495e", font=('Arial', 11, 'bold')).pack(pady=5)
        self.path_listbox = tk.Listbox(self.path_frame, font=('Arial', 10), bg="#2c3e50", fg="white", selectbackground="#e67e22", width=30, height=15)
        self.path_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.path_listbox.bind('<<ListboxSelect>>', self.on_path_select)

        self.body_frame.columnconfigure(0, weight=1)
        self.body_frame.columnconfigure(1, weight=1)

        # --- CONTROL FRAME ---
        self.control_frame = tk.Frame(self.root, bg="#2c3e50", pady=10)
        self.control_frame.pack(fill=tk.X)

        self.button_container = tk.Frame(self.control_frame, bg="#2c3e50")
        self.button_container.pack(anchor=tk.CENTER)

        self.btn_next = tk.Button(self.button_container, text="Next Step", command=self.next_step, 
                                  font=('Arial', 12, 'bold'), bg="#e67e22", fg="white", width=12)
        self.btn_next.grid(row=0, column=0, padx=10)

        self.btn_prev = tk.Button(self.button_container, text="Previous Step", command=self.previous_step, 
                                  font=('Arial', 12, 'bold'), bg="#7f8c8d", fg="white", width=12, state=tk.DISABLED)
        self.btn_prev.grid(row=0, column=1, padx=10)

        self.btn_auto = tk.Button(self.button_container, text="Auto Play", command=self.toggle_auto_play, 
                                  font=('Arial', 12, 'bold'), bg="#2980b9", fg="white", width=12)
        self.btn_auto.grid(row=0, column=2, padx=10)

        self.lbl_stats = tk.Label(self.button_container, text="Ready", fg="#bdc3c7", bg="#2c3e50", font=('Arial', 12))
        self.lbl_stats.grid(row=0, column=3, padx=15)

    def reset_environment(self):
        """Khởi tạo lại trạng thái hệ thống dựa trên thuật toán được chọn"""
        # Tắt Auto Play nếu đang chạy
        self.is_auto_playing = False
        self.btn_auto.config(text="Auto Play", bg="#2980b9", state=tk.NORMAL)
        self.btn_next.config(state=tk.NORMAL)
        
        # Xóa sạch dữ liệu cũ
        self.step_count = 0
        self.solution_path = []
        self.current_state_data = None
        self.path_listbox.delete(0, tk.END)
        for widget in [self.node_up, self.node_down, self.node_left, self.node_right]:
            widget.update_board(None)
            widget.config(bg="#2c3e50")
        for bw in self.frontier_boards:
            bw.update_board(None)

        # Khởi tạo Solver mới dựa trên lựa chọn của Combobox
        selected_algo_name = self.combo_algo.get()
        SolverClass = self.algorithms[selected_algo_name]
        self.solver = SolverClass(self.initial_board)

        # Hiển thị Node ban đầu
        self.node_center.update_board(self.solver.initial_node.board, highlight=True)
        self.node_center.config(bg="#a55b00")
        self.frontier_boards[0].update_board(self.solver.initial_node.board)
        
        # Cập nhật Label ban đầu tùy vào loại thuật toán
        if "IDS" in selected_algo_name:
            self.lbl_stats.config(text="Limit (l): 0 | Step: 0 | Frontier: 1", fg="#bdc3c7")
        else:
            self.lbl_stats.config(text="Step: 0 | Reached: 1 | Frontier: 1", fg="#bdc3c7")
        
        self.ui_history = [] 
        self.btn_prev.config(state=tk.DISABLED)

    def next_step(self):
        # Trước khi chạy bước mới, lưu lại nguyên văn bộ nhớ hiện tại của Solver và thông số bước
        # Sử dụng copy.deepcopy để nhân bản độc lập, tránh bị ghi đè dữ liệu
        solver_snapshot = copy.deepcopy(self.solver)
        self.ui_history.append((self.step_count, solver_snapshot, self.current_state_data))
        self.btn_prev.config(state=tk.NORMAL) # Kích hoạt nút quay lại

        self.step_count += 1
        state_data = self.solver.step()
        
        self.current_state_data = state_data 
        self.update_ui_from_state(state_data)

    def previous_step(self):
        """Hàm xử lý quay ngược lại bước trước đó của thuật toán"""
        if not self.ui_history:
            return

        # Pop lấy dữ liệu mới nhất từ Stack lịch sử ra (LIFO)
        prev_step_count, prev_solver_state, prev_state_data = self.ui_history.pop()
        
        # Đè bộ nhớ cũ vào lại hệ thống
        self.step_count = prev_step_count
        self.solver = prev_solver_state  # Trả bộ giải về đúng quá khứ của nó
        self.current_state_data = prev_state_data
        
        # 3. Khôi phục giao diện vẽ trên màn hình
        if prev_state_data is None:
            # Nếu lùi về tận bước xuất phát ban đầu (khi chưa có data expand nào)
            self.reset_environment()
            return
        else:
            self.update_ui_from_state(prev_state_data)
        
        # Nếu đã lùi về hết cỡ thì khóa nút bấm lại
        if not self.ui_history:
            self.btn_prev.config(state=tk.DISABLED)
            
        # Mở khóa lại các nút bấm đề phòng trường hợp trước đó đã kết thúc thành công/thất bại
        self.btn_next.config(state=tk.NORMAL)
        self.btn_auto.config(state=tk.NORMAL)

    def colorize_node(self, widget, move_name, children_info):
        if move_name not in children_info:
            widget.update_board(None) 
            widget.config(bg="#2c3e50") 
            return
            
        info = children_info[move_name]
        board_data = info["node"].board
        widget.update_board(board_data)
        
        if info["type"] == "new":
            widget.config(bg="#2ecc71")      
        elif info["type"] == "reached":
            widget.config(bg="#e74c3c")      
        elif info["type"] == "success":
            widget.config(bg="#f1c40f")

    def update_ui_from_state(self, data):
        if data is None:
            return
            
        current_board = data["current"].board
        self.node_center.update_board(current_board, highlight=True)
        self.node_center.config(bg="#a55b00")

        if data["status"] == "next_depth":
            for widget in [self.node_up, self.node_down, self.node_left, self.node_right]:
                widget.update_board(None)
                widget.config(bg="#2c3e50")
            self.lbl_stats.config(text=f"TĂNG GIỚI HẠN LÊN l = {data['current_l']}!", fg="#f1c40f")
            return

        if "children_info" in data:
            info = data["children_info"]
            self.colorize_node(self.node_up, 'UP', info)
            self.colorize_node(self.node_down, 'DOWN', info)
            self.colorize_node(self.node_left, 'LEFT', info)
            self.colorize_node(self.node_right, 'RIGHT', info)

        if data["status"] == "success":
            self.is_auto_playing = False
            self.btn_next.config(state=tk.DISABLED)
            self.btn_auto.config(state=tk.DISABLED, text="Auto Play", bg="#2980b9")
            self.lbl_stats.config(text="ĐÃ TÌM THẤY ĐÍCH!!!", fg="#2ecc71")
            
            current_board = data["solution_node"].board
            self.node_center.update_board(current_board, highlight=True)
            self.node_center.config(bg="#f1c40f")
            
            for widget in [self.node_up, self.node_down, self.node_left, self.node_right]:
                widget.update_board(None)
                widget.config(bg="#2c3e50")
            
            self.solution_path = data["path"]
            self.path_listbox.delete(0, tk.END)
            for idx, node in enumerate(self.solution_path):
                move_val = getattr(node, 'move')
                move_str = f"Step {idx}: " + (str(move_val) if move_val else "START")
                if hasattr(self.solver, 'node_costs'):
                    cost_val = self.solver.node_costs.get(node.board, 0)
                    move_str += f" (Cost: {cost_val})"
                self.path_listbox.insert(tk.END, move_str)
            return

        if data["status"] == "failure":
            self.lbl_stats.config(text="KHÔNG TÌM THẤY ĐƯỜNG ĐI!!!", fg="#e74c3c")
            self.btn_next.config(state=tk.DISABLED)
            self.btn_auto.config(state=tk.DISABLED)
            return

        frontier_list = data["frontier_preview"]
        for i in range(5):
            if i < len(frontier_list):
                self.frontier_boards[i].update_board(frontier_list[i])
            else:
                self.frontier_boards[i].update_board(None)

        # Định dạng thống kê hiển thị khác nhau tùy vào thuật toán (Có l hay không có l)
        if "current_l" in data:
            # IDS
            self.lbl_stats.config(text=f"Limit: {data['current_l']} | Step: {self.step_count} | Frontier: {data['frontier_count']}", fg="#bdc3c7")
        elif hasattr(self.solver, 'node_costs'):
            # UCS
            current_cost = self.solver.node_costs.get(current_board, 0)
            self.lbl_stats.config(text=f"Step: {self.step_count} | Reached: {data['reached_count']} | Frontier: {data['frontier_count']} | Current Cost: {current_cost}", fg="#bdc3c7")
        else:
            # BFS, DFS
            self.lbl_stats.config(text=f"Step: {self.step_count} | Reached: {data['reached_count']} | Frontier: {data['frontier_count']}", fg="#bdc3c7")

    def on_path_select(self, event):
        selection = self.path_listbox.curselection()
        if selection:
            index = selection[0]
            selected_node = self.solution_path[index]
            self.node_center.update_board(selected_node.board, highlight=True)
            self.node_center.config(bg="#f1c40f") 
            
            for widget in [self.node_up, self.node_down, self.node_left, self.node_right]:
                widget.update_board(None)
                widget.config(bg="#2c3e50")

    def toggle_auto_play(self):
        if not self.is_auto_playing:
            self.is_auto_playing = True
            self.btn_auto.config(text="Stop Auto", bg="#c0392b") 
            self.btn_next.config(state=tk.DISABLED) 
            self.run_auto_step()
        else:
            self.is_auto_playing = False
            self.btn_auto.config(text="Auto Play", bg="#2980b9") 
            self.btn_next.config(state=tk.NORMAL) 

    def run_auto_step(self):
        if self.is_auto_playing:
            self.step_count += 1
            state_data = self.solver.step()
            self.update_ui_from_state(state_data)
            
            if state_data and state_data["status"] not in ["success", "failure"]:
                self.root.after(500, self.run_auto_step)
            else:
                self.toggle_auto_play()
    
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("780x560") 
    app = MainWindow(root)
    root.mainloop()