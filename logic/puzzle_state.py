class PuzzleState:

    # THÊM THAM SỐ goal_board VÀO HÀM KHỞI TẠO 
    def __init__(self, board, parent=None, move=None, goal_board=(1, 2, 3, 4, 5, 6, 7, 8, 0)):
        self.board = tuple(board)
        self.goal_board = tuple(goal_board) # Lưu lại đích đến để tính toán
        self.parent = parent
        self.move = move  
        self.depth = 0 if parent is None else parent.depth + 1

    def is_goal(self):
        return self.board == self.goal_board

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
                
                # TRUYỀN CẢ GOAL BOARD CHO CÁC NODE CON ĐỂ NÓ NHỚ ĐÍCH LÀ GÌ
                children[move_name] = PuzzleState(new_board, self, move_name, self.goal_board)
                
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
        """Hàm Heuristic h(n): Tính tổng khoảng cách Manhattan linh hoạt theo Đích Tùy Chỉnh"""
        # TỰ ĐỘNG QUÉT VÀ TẠO TỌA ĐỘ ĐÍCH MỚI DỰA TRÊN THÔNG SỐ NHẬP VÀO
        goal_positions = {}
        for i in range(9):
            val = self.goal_board[i]
            goal_positions[val] = (i // 3, i % 3) # Lưu (row, col) của từng giá trị ở bảng Đích
        
        total_distance = 0
        
        # Duyệt qua 9 vị trí trên ma trận hiện tại của Node này
        for i in range(9):
            val = self.board[i]
            if val != 0:  # Không tính ô trống
                # Tọa độ hiện tại 
                current_row = i // 3
                current_col = i % 3
                
                # Tọa độ đúng ở trạng thái đích (lấy từ dict vừa tạo)
                goal_row, goal_col = goal_positions[val]
                total_distance += abs(current_row - goal_row) + abs(current_col - goal_col)
                
        return total_distance