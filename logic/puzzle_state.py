class PuzzleState:
    def __init__(self, board, parent=None, move=None):
        self.board = tuple(board)
        self.parent = parent
        self.move = move  
        self.depth = 0 if parent is None else parent.depth + 1

    def is_goal(self):
        return self.board == (1, 2, 3, 
                              4, 5, 6, 
                              7, 8, 0)

    def get_children(self, is_lifo=False):
        children = {}
        idx = self.board.index(0)
        r, c = divmod(idx, 3)
        
        base_moves = [
            ('LEFT', (0, -1)),
            ('RIGHT', (0, 1)),
            ('UP', (-1, 0)),
            ('DOWN', (1, 0))
        ]
        
        for move_name, (dr, dc) in base_moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                new_idx = nr * 3 + nc
                new_board = list(self.board)
                new_board[idx], new_board[new_idx] = new_board[new_idx], new_board[idx]
                children[move_name] = PuzzleState(new_board, self, move_name)
                
        return children

    def is_cycle(self):
        """Dùng riêng cho IDS hoặc DFS để kiểm tra vòng lặp trên nhánh"""
        current = self.parent
        while current is not None:
            if current.board == self.board:
                return True
            current = current.parent
        return False