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
    
    def heuristic_manhattan(self):
        """Hàm Heuristic h(n): Tính tổng khoảng cách Manhattan của các ô từ 1 đến 8 về đích"""
        # Định nghĩa tọa độ (hàng, cột) đúng của các số từ 0 đến 8 ở trạng thái ĐÍCH
        # Đích chuẩn: (1, 2, 3, 4, 5, 6, 7, 8, 0)
        goal_positions = {
            1: (0, 0), 2: (0, 1), 3: (0, 2),
            4: (1, 0), 5: (1, 1), 6: (1, 2),
            7: (2, 0), 8: (2, 1), 0: (2, 2)  # Ô trống số 0 sẽ bỏ qua không tính
        }
        
        total_distance = 0
        
        # Duyệt qua 9 vị trí trên ma trận hiện tại của Node này
        for i in range(9):
            val = self.board[i]
            if val != 0:  # Không tính ô trống
                # Tọa độ hiện tại 
                current_row = i // 3
                current_col = i % 3
                
                # Tọa độ đúng ở trạng thái đích
                goal_row, goal_col = goal_positions[val]
                
                # Áp dụng công thức trị tuyệt đối: |x1 - x2| + |y1 - y2|
                total_distance += abs(current_row - goal_row) + abs(current_col - goal_col)
                
        return total_distance