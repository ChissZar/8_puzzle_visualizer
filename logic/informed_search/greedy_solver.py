import heapq
from logic.puzzle_state import PuzzleState

class GreedySolver:
    def __init__(self, initial_board, goal_board=(1, 2, 3, 4, 5, 6, 7, 8, 0)):

        self.initial_node = PuzzleState(initial_board, goal_board=goal_board)
        # Frontier dùng Priority Queue
        self.frontier = []
        self.counter = 0  # Bộ đếm phụ giúp phân định khi 2 Node có cùng chi phí Manhattan
        
        # Lấy chi phí Manhattan ban đầu của Node gốc
        h_cost = self.initial_node.heuristic_manhattan()
        
        # Đẩy vào Queue theo cấu trúc: (Chi_phí_Manhattan, Số_thứ_tự_sinh, Node)
        heapq.heappush(self.frontier, (h_cost, self.counter, self.initial_node))
        
        # Quản lý chi phí trực tiếp bằng dictionary để UI lấy ra hiển thị
        self.node_costs = {self.initial_node.board: h_cost}
        
        self.reached = set()
        self.is_solved = False
        self.failure = False

        # Kiểm tra đích sớm cho Node gốc ngay khi khởi tạo
        if self.initial_node.is_goal():
            self.is_solved = True

    def get_path(self, node):
        path = []
        current = node
        while current is not None:
            path.append(current)
            current = current.parent
        return path[::-1] 
    
    def step(self):
        if self.is_solved or self.failure:
            return None

        # Frontier không rỗng
        if not self.frontier:
            self.failure = True
            return {
                "status": "failure",
                "current": getattr(self, 'current_node', self.initial_node) # Gửi node cuối lên UI
            }

        # Chọn trạng thái có chi phí nhỏ nhất (Manhattan)
        current_cost, _, current_node = heapq.heappop(self.frontier)
        self.current_node = current_node
        current_board = current_node.board
        
        # Bỏ qua các node đã nằm trong reached
        if current_board in self.reached:
            return self.step()

        # Nếu n == Goal -> "Thành công" 
        if current_node.is_goal():
            self.is_solved = True
            return {
                "status": "success",
                "current": current_node,
                "solution_node": current_node,
                "path": self.get_path(current_node)
            }

        # Thêm n vào reached
        self.reached.add(current_board)
        
        children_dict = current_node.get_children()
        children_info = {}

        # Trích xuất danh sách các ma trận hiện đang nằm chờ trong frontier để phục vụ kiểm tra điều kiện 
        frontier_boards = {item[2].board for item in self.frontier}

        for move, child_node in children_dict.items():
            s = child_node.board
            
            # Nếu m chưa có trong cả frontier và reached:
            if s not in frontier_boards and s not in self.reached:
                # Tính giá trị heuristic h(m) bằng khoảng cách Manhattan
                h_cost = child_node.heuristic_manhattan()
                self.node_costs[s] = h_cost
                self.counter += 1
                
                # Thêm m vào frontier
                heapq.heappush(self.frontier, (h_cost, self.counter, child_node))
                children_info[move] = {"node": child_node, "type": "new"} 
            else:
                # Nếu m đã có trong frontier hoặc reached -> Bỏ qua m
                children_info[move] = {"node": child_node, "type": "reached"}

        # Sắp xếp và hiển thị 10 Node có chi phí Manhattan thấp nhất lên thanh Frontier của UI
        sorted_frontier = sorted(self.frontier, key=lambda x: x[0])
        frontier_preview_list = [item[2].board for item in sorted_frontier][:10]

        return {
            "status": "expanding",
            "current": current_node,
            "children_info": children_info, 
            "frontier_preview": frontier_preview_list, 
            "reached_count": len(self.reached),
            "frontier_count": len(self.frontier)
        }