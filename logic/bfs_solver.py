from collections import deque
from logic.puzzle_state import PuzzleState

class BFSSolver:
    def __init__(self, initial_board):
        self.initial_node = PuzzleState(initial_board)
        
        # frontier <- a FIFO queue
        self.frontier = deque([self.initial_node])
        
        # reached <- {problem.INITIAL}
        self.reached = {self.initial_node.board}
        
        self.is_solved = False
        self.failure = False

        if self.initial_node.is_goal():
            self.is_solved = True

    def get_path(self, node):
        """Hàm truy vết ngược từ Node đích về Node gốc để lấy danh sách các bước đi"""
        path = []
        current = node
        while current is not None:
            path.append(current)
            current = current.parent
        return path[::-1] 
    
    def step(self):
        """
        Hàm này tương đương với 1 vòng lặp "while not IS-EMPTY(frontier)".
        Trả về một Dictionary chứa đầy đủ dữ liệu để UI lấy ra vẽ.
        """
        if self.is_solved or self.failure:
            return None

        # if IS-EMPTY(frontier)
        if not self.frontier:
            self.failure = True
            return {"status": "failure"}

        # node <- POP(frontier)
        current_node = self.frontier.popleft()
        
        # for each child in EXPAND(problem, node)
        children_dict = current_node.get_children()
        children_info = {}

        for move, child_node in children_dict.items():
            s = child_node.board
            
            # if child_node.IS-GOAL(s) then return child
            if child_node.is_goal():
                self.is_solved = True
                return {
                    "status": "success",
                    "current": current_node,
                    "solution_node": child_node,
                    "path": self.get_path(child_node)
                }
        
            # if s is not in reached then
            if s not in self.reached:
                self.reached.add(s)         # add s to reached
                self.frontier.append(child_node) # add child to frontier
                children_info[move] = {"node": child_node, "type": "new"} 
            else:
                children_info[move] = {"node": child_node, "type": "reached"}

        # Trả về các thông số hiện tại để giao diện update
        return {
            "status": "expanding",
            "current": current_node,
            "children_info": children_info, # Thông tin để vẽ 4 ô xung quanh
            "frontier_preview": [node.board for node in self.frontier][:5], # Lấy 5 phần tử đầu cho Queue trên UI
            "reached_count": len(self.reached),
            "frontier_count": len(self.frontier)
        }