import random

class StochasticHCNode:
    def __init__(self, board, parent=None, move=None, h=0):
        self.board = tuple(board)
        self.parent = parent
        self.move = move
        self.h = h
        self.f = h # Mượn biến f để UI tự động in chữ h(n) ra

class StochasticHillClimbingSolver:
    def __init__(self, initial_board, goal_board=(1, 2, 3, 4, 5, 6, 7, 8, 0)):
        self.initial_board = tuple(initial_board)
        self.goal_board = tuple(goal_board)
        
        start_h = self.calculate_manhattan(self.initial_board)
        self.initial_node = StochasticHCNode(self.initial_board, parent=None, move=None, h=start_h)
        
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

        # Nếu Current_State == Goal: Trả về
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
                "frontier_count": 0,
                "frontier_preview": [n.board for n in self.frontier]
            }

        children_info = {}
        all_successors = []
        better_neighbors = []
        candidates = []
        chosen_move = None
        chosen_node = None
        
        # Sinh tất cả các trạng thái lân cận
        for move, m_board in self.get_successors(current_node):
            h_m = self.calculate_manhattan(m_board)
            m_node = StochasticHCNode(m_board, parent=current_node, move=move, h=h_m)
            all_successors.append((move, m_node))
            candidates.append({"move": move, "h": h_m, "marker": ""})
            
            # Lọc ra tập Better_Neighbors
            if h_m < current_node.h:
                better_neighbors.append((move, m_node))

        # Nếu Better_Neighbors rỗng
        if not better_neighbors:
            for move, m_node in all_successors:
                children_info[move] = {"node": m_node, "type": "reached"} # Đỏ (Từ chối hết)
            for item in candidates:
                item["marker"] = " not better"
            accepted = False
            reason = "Không có better neighbor nên Stochastic Hill Climbing bị kẹt."
        else:
            # Ngược lại: Chọn ngẫu nhiên một trạng thái từ tập Better_Neighbors
            chosen_move, chosen_node = random.choice(better_neighbors)
            self.frontier.append(chosen_node) # Next_State cho vòng lặp sau
            
            # Đổ màu UI: Được chọn thì Xanh, còn lại Đỏ hết
            for move, m_node in all_successors:
                if m_node == chosen_node:
                    children_info[move] = {"node": m_node, "type": "new"}
                else:
                    children_info[move] = {"node": m_node, "type": "reached"}
            better_moves = {move for move, _ in better_neighbors}
            for item in candidates:
                if item["move"] == chosen_move:
                    item["marker"] = " <- random pick"
                elif item["move"] in better_moves:
                    item["marker"] = " better"
                else:
                    item["marker"] = " rejected"
            accepted = True
            reason = "Lọc các neighbor có h nhỏ hơn current, rồi chọn ngẫu nhiên một neighbor trong tập đó."

        return {
            "status": "running",
            "current": current_node,
            "children_info": children_info,
            "frontier_preview": [n.board for n in self.frontier],
            "reached_count": 0,
            "frontier_count": len(better_neighbors), # Trả về số lượng Better_Neighbors 
            "local_decision": {
                "algo": "Stochastic Hill Climbing",
                "current_h": current_node.h,
                "selected_move": chosen_move,
                "selected_h": chosen_node.h if chosen_node else None,
                "accepted": accepted,
                "stuck": not accepted,
                "better_count": len(better_neighbors),
                "candidates": candidates,
                "reason": reason
            }
        }
