from logic.puzzle_state import PuzzleState

class IDSSolver:
    def __init__(self, initial_board):
        self.initial_node = PuzzleState(initial_board)
        self.is_solved = False
        self.failure = False
        
        # Bắt đầu với giới hạn độ sâu l = 0
        self.current_l = 0
        
        # Khởi tạo trạng thái cho lượt chạy DLS(l = 0) ban đầu
        self.reset_dls(self.current_l)

    def reset_dls(self, limit):
        """Khởi động lại Frontier Stack và trạng thái cho một tầng độ sâu mới"""
        self.limit = limit
        self.frontier = [self.initial_node]
        self.cutoff_occurred = False

    def get_path(self, node):
        path = []
        current = node
        while current is not None:
            path.append(current)
            current = current.parent
        return path[::-1] 
    
    def step(self):
        """
        Thực hiện một bước chuyển đổi trạng thái (1 lần pop và expand).
        """
        if self.is_solved or self.failure:
            return None

        # Trường hợp Frontier của tầng hiện tại trống (Hết node để xét ở độ sâu l)
        if not self.frontier:
            if self.cutoff_occurred:
                # Nếu trong quá trình duyệt có node bị chặn bởi cutoff -> tăng l lên 1 và quét lại
                self.current_l += 1
                self.reset_dls(self.current_l)
                # Trả về trạng thái thông báo hệ thống chuyển tầng để UI hiển thị thông tin
                return {
                    "status": "next_depth",
                    "current": self.initial_node,
                    "children_info": {},
                    "frontier_preview": [self.initial_node.board],
                    "reached_count": 0,
                    "frontier_count": 1,
                    "current_l": self.current_l
                }
            else:
                # Nếu không có cutoff nào xảy ra mà vẫn trống -> Vét cạn toàn bộ cây đồ thị nhưng không thấy đích
                self.failure = True
                return {"status": "failure"}

        # node <- POP(frontier)
        current_node = self.frontier.pop()
        
        # if problem.IS-GOAL(node.STATE) then return node
        if current_node.is_goal():
            self.is_solved = True
            return {
                "status": "success",
                "current": current_node,
                "solution_node": current_node,
                "path": self.get_path(current_node)
            }
        
        children_info = {}
        
        # if DEPTH(node) >= l then result <- cutoff
        if current_node.depth >= self.limit:
            self.cutoff_occurred = True
            # Không phát triển thêm khi chạm hoặc vượt giới hạn tầng l
        else:
            # else if not IS-CYCLE(node) do
            if not current_node.is_cycle():
                children_dict = current_node.get_children()
                
                for move, child_node in children_dict.items():
                    # Thêm tất cả con hợp lệ vào frontier stack
                    self.frontier.append(child_node)
                    children_info[move] = {"node": child_node, "type": "new"}

        # Chuẩn bị dữ liệu hiển thị
        frontier_preview_list = [node.board for node in self.frontier][-5:][::-1]

        return {
            "status": "expanding",
            "current": current_node,
            "children_info": children_info, 
            "frontier_preview": frontier_preview_list, 
            "reached_count": 0, 
            "frontier_count": len(self.frontier),
            "current_l": self.limit
        }