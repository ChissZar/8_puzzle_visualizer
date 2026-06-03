import heapq

class AStarNode:
    def __init__(self, board, parent=None, move=None, g=0, h=0):
        self.board = tuple(board)
        self.parent = parent
        self.move = move
        self.g = g
        self.h = h
        self.f = g + h # f(n) = Số nghịch thế + Số ô sai

    def __lt__(self, other):
        return self.f < other.f

class AStarSolver:
    def __init__(self, initial_board, goal_board=(1, 2, 3, 4, 5, 6, 7, 8, 0)):
        self.initial_board = tuple(initial_board)
        self.goal_board = tuple(goal_board)
        
        # Tính g và h cho nút Start theo ĐÚNG YÊU CẦU CỦA TRIẾT
        start_g = self.calculate_inversions(self.initial_board)
        start_h = self.calculate_misplaced_tiles(self.initial_board, self.goal_board)
        
        self.initial_node = AStarNode(self.initial_board, parent=None, move=None, g=start_g, h=start_h)
        
        self.frontier = []
        heapq.heappush(self.frontier, self.initial_node)
        
        self.state_costs = {self.initial_board: start_g}
        self.is_finished = False

    # Hàm đếm số cặp nghịch thế (g)
    def calculate_inversions(self, board):
        flat_state = [x for x in board if x != 0]
        inversions = 0
        n = len(flat_state)
        for i in range(n):
            for j in range(i + 1, n):
                if flat_state[i] > flat_state[j]:
                    inversions += 1
        return inversions

    # Hàm đếm số ô sai vị trí (h)
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
        
        moves = [('UP', -1, 0), ('DOWN', 1, 0), ('LEFT', 0, -1), ('RIGHT', 0, 1)]
        
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

        current_node = heapq.heappop(self.frontier)

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
                "reached_count": len(self.state_costs),
                "frontier_count": len(self.frontier),
                "frontier_preview": [n.board for n in self.frontier]
            }

        children_info = {}
        for move, m_board in self.get_successors(current_node):
            
            # Đếm số cặp nghịch thế của trạng thái mới
            inversions_m = self.calculate_inversions(m_board)
            
            # g_new = g_cũ + nghịch thế mới
            g_new = current_node.g + inversions_m
            
            if m_board not in self.state_costs or g_new < self.state_costs[m_board]:
                self.state_costs[m_board] = g_new
                h_m = self.calculate_misplaced_tiles(m_board, self.goal_board)
                
                # Nạp vào Node mới, Node sẽ tự động tính f = g + h
                m_node = AStarNode(m_board, parent=current_node, move=move, g=g_new, h=h_m)
                
                heapq.heappush(self.frontier, m_node)
                children_info[move] = {"node": m_node, "type": "new"}
            else:
                dummy = AStarNode(m_board) 
                children_info[move] = {"node": dummy, "type": "reached"}

        return {
            "status": "running",
            "current": current_node,
            "children_info": children_info,
            "frontier_preview": [n.board for n in self.frontier],
            "reached_count": len(self.state_costs),
            "frontier_count": len(self.frontier)
        }