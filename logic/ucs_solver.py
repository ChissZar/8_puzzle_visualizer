import heapq
from logic.puzzle_state import PuzzleState

class UCSSolver:
    def __init__(self, initial_board, goal_board=(1, 2, 3, 4, 5, 6, 7, 8, 0)):
        self.goal_board = tuple(goal_board)
        self.initial_node = PuzzleState(initial_board, goal_board=self.goal_board)
        
        # Priority Queue
        self.frontier = []
        self.counter = 0 # Tránh trùng lặp khi so sánh tuple trong heapq
        
        # Hàm tính số ô sai vị trí so với đích
        def get_misplaced_count(board_tuple):
            count = 0
            for i in range(9):
                if board_tuple[i] != 0 and board_tuple[i] != self.goal_board[i]:
                    count += 1
            return count

        # Lưu chi phí tích lũy trực tiếp vào một dictionary quản lý cost
        # Trạng thái đầu tiên có chi phí bằng số ô sai của chính nó
        self.node_costs = {self.initial_node.board: get_misplaced_count(self.initial_node.board)}
        
        initial_cost = self.node_costs[self.initial_node.board]
        heapq.heappush(self.frontier, (initial_cost, self.counter, self.initial_node))
        
        self.reached = {self.initial_node.board}
        self.is_solved = False
        self.failure = False

        # Kiểm tra đích ngay cho node gốc
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

        if not self.frontier:
            self.failure = True
            return {"status": "failure"}

        # Lấy Node có tổng chi phí thấp nhất ra khỏi Queue
        current_cost, _, current_node = heapq.heappop(self.frontier)

        if current_node.is_goal():
            self.is_solved = True
            return {
                "status": "success",
                "current": current_node,
                "solution_node": current_node,
                "path": self.get_path(current_node)
            }
        
        children_dict = current_node.get_children()
        children_info = {}

        # Hàm tính số ô sai của node con
        def get_misplaced_count(board_tuple):
            count = 0
            for i in range(9):
                if board_tuple[i] != 0 and board_tuple[i] != self.goal_board[i]:
                    count += 1
            return count

        for move, child_node in children_dict.items():
            s = child_node.board
            
            # Tính chi phí tích lũy = Chi phí cha + Số ô sai của con
            child_misplaced = get_misplaced_count(s)
            accumulated_cost = current_cost + child_misplaced

            if s not in self.reached:
                self.reached.add(s)
                self.node_costs[s] = accumulated_cost
                self.counter += 1
                
                # Đẩy vào Priority Queue với tổng chi phí mới
                heapq.heappush(self.frontier, (accumulated_cost, self.counter, child_node))
                children_info[move] = {"node": child_node, "type": "new"} 
            else:
                children_info[move] = {"node": child_node, "type": "reached"}

        # Sắp xếp hiển thị 10 Node có tổng chi phí thấp nhất lên thanh Frontier trên UI
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