import math

class IDAStarNode:
    def __init__(self, board, parent=None, move=None, g=0, h=0):
        self.board = tuple(board)
        self.parent = parent
        self.move = move
        self.g = g
        self.h = h
        self.f = g + h

class IDAStarSolver:
    def __init__(self, initial_board, goal_board=(1, 2, 3, 4, 5, 6, 7, 8, 0)):
        self.initial_board = tuple(initial_board)
        self.goal_board = tuple(goal_board)
        
        # Khởi tạo g và h cho Start
        start_g = self.calculate_manhattan(self.initial_board)
        start_h = self.calculate_misplaced_tiles(self.initial_board, self.goal_board)
        
        self.initial_node = IDAStarNode(self.initial_board, parent=None, move=None, g=start_g, h=start_h)
        
        # Ngưỡng ban đầu chính là f của Start
        self.threshold = self.initial_node.f
        self.next_threshold = math.inf # Biến theo dõi ngưỡng nhỏ nhất cho vòng sau
        
        # Dùng Stack (LIFO) thay vì Priority Queue
        self.frontier = [self.initial_node]
        self.path_set = {self.initial_board} 
        
        self.is_finished = False

    def calculate_manhattan(self, board):
        dist = 0
        for i in range(9):
            val = board[i]
            if val != 0:
                goal_idx = self.goal_board.index(val)
                dist += abs(i // 3 - goal_idx // 3) + abs(i % 3 - goal_idx % 3)
        return dist

    def calculate_misplaced_tiles(self, board, goal):
        misplaced = 0
        for i in range(9):
            if board[i] != 0 and board[i] != goal[i]:
                misplaced += 1
        return misplaced

    def get_successors(self, node):
        successors = []
        empty_idx = node.board.index(0)
        row, col = empty_idx // 3, empty_idx % 3
        
        # Vì FRONTIER là Stack (LIFO: Vào sau ra trước), 
        # nên ta duyệt ngược [RIGHT, LEFT, DOWN, UP] để Lấy UP ra trước.
        moves = [('RIGHT', 0, 1), ('LEFT', 0, -1), ('DOWN', 1, 0), ('UP', -1, 0)]
        
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
            
        # HẾT VÒNG LẶP (Ngăn xếp rỗng)
        if not self.frontier:
            if self.next_threshold == math.inf:
                self.is_finished = True
                return {
                "status": "failure",
                "current": getattr(self, 'current_node', self.initial_node) # Gửi node cuối lên UI
            }
            
            # Tăng ngưỡng f_limit và chuẩn bị chạy lại từ đầu
            self.threshold = self.next_threshold
            self.next_threshold = math.inf
            self.frontier = [self.initial_node]
            
            # Trả về tín hiệu đổi Threshold để UI chớp chữ Vàng
            return {
                "status": "next_depth",
                "current_l": self.threshold,
                "current": self.initial_node
            }

        # POP NODE TRÊN ĐỈNH STACK 
        current_node = self.frontier.pop()
        self.current_node = current_node
        
        # Chống lặp vòng (Cycle Detection) bằng cách truy vết lại đường đi hiện tại
        self.path_set = set()
        curr = current_node
        while curr:
            self.path_set.add(curr.board)
            curr = curr.parent

        # KIỂM TRA ĐÍCH
        if current_node.board == self.goal_board:
            self.is_finished = True
            path = []
            curr = current_node
            while curr:
                path.append(curr)
                curr = curr.parent
            path.reverse()
            
            return {
                "status": "success",
                "current": current_node,
                "solution_node": current_node,
                "path": path,
                "reached_count": len(self.path_set),
                "frontier_count": len(self.frontier),
                "frontier_preview": [n.board for n in reversed(self.frontier)]
            }

        # SINH CON
        children_info = {}
        for move, m_board in self.get_successors(current_node):
            if m_board in self.path_set:
                continue # Nếu lùi lại Node cha thì bỏ qua
            
            g_new = current_node.g + self.calculate_manhattan(m_board)
            h_m = self.calculate_misplaced_tiles(m_board, self.goal_board)
            f_new = g_new + h_m
            
            m_node = IDAStarNode(m_board, parent=current_node, move=move, g=g_new, h=h_m)
            
            # NẾU VƯỢT NGƯỠNG -> CUTOFF
            if f_new > self.threshold:
                # Cập nhật lại ngưỡng nhỏ nhất cho vòng sau
                self.next_threshold = min(self.next_threshold, f_new)
                
                # Trả về màu Đỏ (Reached/Cutoff) trên UI
                children_info[move] = {"node": m_node, "type": "reached"} 
            else:
                # NẾU HỢP LỆ -> CHO VÀO STACK (Màu xanh lá)
                self.frontier.append(m_node)
                children_info[move] = {"node": m_node, "type": "new"}

        return {
            "status": "running",
            "current": current_node,
            "children_info": children_info,
            "frontier_preview": [n.board for n in reversed(self.frontier)],
            "reached_count": len(self.path_set),
            "frontier_count": len(self.frontier),
            "current_l": self.threshold # Gắn thêm current_l để UI hiện f_limit
        }