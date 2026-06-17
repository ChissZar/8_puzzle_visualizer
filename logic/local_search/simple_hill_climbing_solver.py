class HCNode:
    def __init__(self, board, parent=None, move=None, h=0):
        self.board = tuple(board)
        self.parent = parent
        self.move = move
        self.h = h
        self.f = h 

class SimpleHillClimbingSolver:
    def __init__(self, initial_board, goal_board=(1, 2, 3, 4, 5, 6, 7, 8, 0)):
        self.initial_board = tuple(initial_board)
        self.goal_board = tuple(goal_board)
        
        # Tính h(n) cho Start bằng khoảng cách Manhattan
        start_h = self.calculate_manhattan(self.initial_board)
        self.initial_node = HCNode(self.initial_board, parent=None, move=None, h=start_h)
        
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
        
        # Nếu frontier rỗng, chính thức báo Failure
        if not self.frontier:
            self.is_finished = True
            return {
                "status": "failure",
                "current": getattr(self, 'current_node', self.initial_node)
            }

        # Lưu vết lại node hiện tại trước khi xử lý
        self.current_node = self.frontier.pop(0)
        current_node = self.current_node

        # KIỂM TRA GOAL NGAY TỪ ĐẦU
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
        candidates = []
        selected_move = None
        selected_h = None
        
        # SINH LẦN LƯỢT CÁC LÂN CẬN
        for move, m_board in self.get_successors(current_node):
            h_m = self.calculate_manhattan(m_board)
            m_node = HCNode(m_board, parent=current_node, move=move, h=h_m)
            marker = ""
            
            # KIỂM TRA ĐIỀU KIỆN "TỐT HƠN" (h nhỏ hơn)
            if h_m < current_node.h:
                self.frontier.append(m_node)
                children_info[move] = {"node": m_node, "type": "new"} # Màu xanh lá
                selected_move = move
                selected_h = h_m
                marker = " <- first better"
                candidates.append({"move": move, "h": h_m, "marker": marker})
                break 
            else:
                # Nếu không tốt hơn, đánh dấu đỏ (từ chối)
                children_info[move] = {"node": m_node, "type": "reached"}
                candidates.append({"move": move, "h": h_m, "marker": " rejected"})

        accepted = selected_move is not None
        reason = (
            "Simple Hill Climbing duyệt theo thứ tự LEFT, RIGHT, UP, DOWN và nhận neighbor đầu tiên có h nhỏ hơn current."
            if accepted
            else "Không có neighbor đã xét nào tốt hơn current, thuật toán bị kẹt tại local maximum."
        )

        return {
            "status": "running",
            "current": current_node,
            "children_info": children_info,
            "frontier_preview": [n.board for n in self.frontier],
            "reached_count": 0,
            "frontier_count": len(self.frontier),
            "local_decision": {
                "algo": "Simple Hill Climbing",
                "current_h": current_node.h,
                "selected_move": selected_move,
                "selected_h": selected_h,
                "accepted": accepted,
                "stuck": not accepted,
                "candidates": candidates,
                "reason": reason
            }
        }
