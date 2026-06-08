class LBSNode:
    def __init__(self, board, parent=None, move=None, h=0):
        self.board = tuple(board)
        self.parent = parent
        self.move = move
        self.h = h
        self.f = h

class LocalBeamSearchSolver:
    def __init__(self, initial_board, goal_board=(1, 2, 3, 4, 5, 6, 7, 8, 0), k=2):
        self.initial_board = tuple(initial_board)
        self.goal_board = tuple(goal_board)
        self.k = k
        
        start_h = self.calculate_manhattan(self.initial_board)
        self.initial_node = LBSNode(self.initial_board, parent=None, move=None, h=start_h)
        
        self.frontier = [self.initial_node] 
        
        # [MỚI] Lưu lại cố định k node của thế hệ hiện tại để hiển thị
        self.current_beam = [self.initial_node] 
        self.next_beam_candidates = []      
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
            
        if not self.frontier:
            if not self.next_beam_candidates:
                self.is_finished = True
                return {
                    "status": "failure",
                    "current": getattr(self, 'current_node', self.initial_node)
                }
            
            self.next_beam_candidates.sort(key=lambda x: x.h)
            
            # Cập nhật chùm mới và LƯU LẠI BẢN SAO vào current_beam
            self.frontier = self.next_beam_candidates[:self.k]
            self.current_beam = list(self.frontier) 
            self.next_beam_candidates = [] 

        self.current_node = self.frontier.pop(0)
        current_node = self.current_node

        if current_node.board == self.goal_board:
            self.is_finished = True
            path = []
            curr = current_node
            while curr:
                path.append(curr)
                curr = curr.parent
            path.reverse()
            
            preview = [n.board for n in self.current_beam] + [None] + [n.board for n in self.next_beam_candidates]
            return {
                "status": "success",
                "current": current_node,
                "solution_node": current_node,
                "path": path,
                "reached_count": 0,
                "frontier_count": len(self.next_beam_candidates),
                "frontier_preview": preview
            }

        children_info = {}
        
        for move, m_board in self.get_successors(current_node):
            h_m = self.calculate_manhattan(m_board)
            m_node = LBSNode(m_board, parent=current_node, move=move, h=h_m)
            
            is_duplicate = any(c.board == m_node.board for c in self.next_beam_candidates)
            if not is_duplicate:
                self.next_beam_candidates.append(m_node)
                children_info[move] = {"node": m_node, "type": "new"} 
            else:
                children_info[move] = {"node": m_node, "type": "reached"} 

        # Ghép mảng: Chùm hiện tại + [1 Ô Trống] + Tập lân cận mới
        preview = [n.board for n in self.current_beam] + [None] + [n.board for n in self.next_beam_candidates]

        return {
            "status": "running",
            "current": current_node,
            "children_info": children_info,
            "frontier_preview": preview,
            "reached_count": 0,
            "frontier_count": len(self.next_beam_candidates),
            "beam_k": self.k 
        }