import random
import math

class SANode:
    def __init__(self, board, parent=None, move=None, h=0):
        self.board = tuple(board)
        self.parent = parent
        self.move = move
        self.h = h
        self.f = h # Để UI hiển thị chung hàm

class SimulatedAnnealingSolver:
    # T0: Nhiệt độ ban đầu, Tmin: Nhiệt độ đóng băng, alpha: Tốc độ hạ nhiệt
    def __init__(self, initial_board, goal_board=(1, 2, 3, 4, 5, 6, 7, 8, 0), T0=100.0, Tmin=0.01, alpha=0.95):
        self.initial_board = tuple(initial_board)
        self.goal_board = tuple(goal_board)
        self.T = T0
        self.Tmin = Tmin
        self.alpha = alpha
        
        start_h = self.calculate_manhattan(self.initial_board)
        self.initial_node = SANode(self.initial_board, parent=None, move=None, h=start_h)
        self.current_node = self.initial_node
        
        self.is_finished = False

    def calculate_manhattan(self, board):
        dist = 0
        for i in range(9):
            val = board[i]
            if val != 0:
                goal_idx = self.goal_board.index(val)
                dist += abs(i // 3 - goal_idx // 3) + abs(i % 3 - goal_idx % 3)
        return dist

    def get_successors(self, node):
        successors = []
        empty_idx = node.board.index(0)
        row, col = empty_idx // 3, empty_idx % 3
        moves = [('LEFT', 0, -1), ('RIGHT', 0, 1), ('UP', -1, 0), ('DOWN', 1, 0)]
        for move, dr, dc in moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 3 and 0 <= new_col < 3:
                new_idx = new_row * 3 + new_col
                new_board = list(node.board)
                new_board[empty_idx], new_board[new_idx] = new_board[new_idx], new_board[empty_idx]
                successors.append((move, tuple(new_board)))
        return successors

    def step(self):
        if self.is_finished:
            return None
            
        # 1. Kiểm tra Đích
        if self.current_node.board == self.goal_board:
            self.is_finished = True
            path = []
            curr = self.current_node
            while curr:
                path.append(curr)
                curr = curr.parent
            path.reverse()
            return {
                "status": "success",
                "current": self.current_node,
                "solution_node": self.current_node,
                "path": path,
                "frontier_count": 0,
                "frontier_preview": [],
                "sa_T": self.T
            }

        # 2. Kiểm tra đóng băng (T <= Tmin) -> Thất bại
        if self.T <= self.Tmin:
            self.is_finished = True
            return {
                "status": "failure",
                "current": self.current_node,
                "sa_T": self.T
            }

        children_info = {}
        all_successors = self.get_successors(self.current_node)
        
        chosen_move, chosen_board = random.choice(all_successors)
        h_next = self.calculate_manhattan(chosen_board)
        next_node = SANode(chosen_board, parent=self.current_node, move=chosen_move, h=h_next)

        # Tính Delta = h(next state) - h(current state)
        delta = next_node.h - self.current_node.h
        
        is_accepted = False
        p = 0.0

        if delta < 0:
            # Δ < 0: Trạng thái TỐT HƠN -> Nhận
            is_accepted = True
            children_info[chosen_move] = {"node": next_node, "type": "new"} # Xanh lá
        else:
            # Δ >= 0: Trạng thái TỆ HƠN -> Thử vận may bằng xác suất
            p = math.exp(-delta / self.T)
            rand_val = random.random() # Trả về số thực từ 0.0 đến 1.0
            
            if rand_val < p:
                is_accepted = True
                children_info[chosen_move] = {"node": next_node, "type": "success"} 
            else:
                is_accepted = False
                children_info[chosen_move] = {"node": next_node, "type": "reached"} # Đỏ (Từ chối)

        # Đóng gói dữ liệu TRƯỚC KHI cập nhật biến T
        state_data = {
            "status": "running",
            "current": self.current_node,
            "children_info": children_info,
            "frontier_count": 0,
            "frontier_preview": [],
            "sa_T": self.T,
            "sa_delta": delta,
            "sa_p": p,
            "sa_accepted": is_accepted
        }

        # Nếu chấp nhận, di chuyển sang trạng thái mới
        if is_accepted:
            self.current_node = next_node
            
        # Hạ nhiệt độ (T = α * T)
        self.T = self.alpha * self.T
        
        return state_data