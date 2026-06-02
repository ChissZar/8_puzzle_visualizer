class SAHCNode:
    def __init__(self, board, parent=None, move=None, h=0):
        self.board = tuple(board)
        self.parent = parent
        self.move = move
        self.h = h
        self.f = h # Mượn biến f để UI tự động in chữ h(n) ra màn hình

class SteepestAscentHillClimbingSolver:
    def __init__(self, initial_board):
        self.initial_board = tuple(initial_board)
        self.goal_board = (1, 2, 3, 4, 5, 6, 7, 8, 0)
        
        # Tính h(n) cho Start bằng khoảng cách Manhattan
        start_h = self.calculate_manhattan(self.initial_board)
        self.initial_node = SAHCNode(self.initial_board, parent=None, move=None, h=start_h)
        
        self.frontier = [self.initial_node]
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
        
        # THỨ TỰ DUYỆT: L -> R -> U -> D
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
            
        if not self.frontier:
            self.is_finished = True
            return {"status": "failure"}

        current_node = self.frontier.pop(0)

        # KIỂM TRA GOAL
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
                "reached_count": 0,
                "frontier_count": len(self.frontier),
                "frontier_preview": [n.board for n in self.frontier]
            }

        children_info = {}
        all_successors = []
        best_node = None
        min_h = float('inf') # Đặt min ban đầu là vô cùng lớn
        
        for move, m_board in self.get_successors(current_node):
            h_m = self.calculate_manhattan(m_board)
            m_node = SAHCNode(m_board, parent=current_node, move=move, h=h_m)
            all_successors.append((move, m_node))
            
            # Tìm lân cận có h nhỏ nhất
            if h_m < min_h:
                min_h = h_m
                best_node = m_node

        if min_h < current_node.h:
            # Nếu tốt hơn -> Chấp nhận best_node
            self.frontier.append(best_node)
            
            # Đổ màu cho UI: Tốt nhất màu Xanh, những node không được chọn màu Đỏ
            for move, m_node in all_successors:
                if m_node == best_node:
                    children_info[move] = {"node": m_node, "type": "new"}
                else:
                    children_info[move] = {"node": m_node, "type": "reached"}
        else:
            # Nếu không có thằng nào tốt hơn -> Đạt cực đại cục bộ, từ chối TẤT CẢ
            self.is_finished = True
            for move, m_node in all_successors:
                children_info[move] = {"node": m_node, "type": "reached"}

        return {
            "status": "running",
            "current": current_node,
            "children_info": children_info,
            "frontier_preview": [n.board for n in self.frontier],
            "reached_count": 0,
            "frontier_count": len(self.frontier)
        }