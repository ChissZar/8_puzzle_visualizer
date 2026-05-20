from logic.puzzle_state import PuzzleState

class DFSSolver:
    def __init__(self, initial_board):
        self.initial_node = PuzzleState(initial_board)
        
        # frontier <- a LIFO stack, with node as an element
        self.frontier = [self.initial_node]
        
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
        if self.is_solved or self.failure:
            return None

        # while not IS-EMPTY(frontier)
        if not self.frontier:
            self.failure = True
            return {"status": "failure"}

        # node <- POP(frontier) (Dùng LIFO Stack nên lấy ở cuối)
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
        
        # for each child in EXPAND(problem, node)
        children_dict = current_node.get_children()
        children_info = {}

        for move, child_node in children_dict.items():
            s = child_node.board
            
            # if problem.IS-GOAL(s) then return child 
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

        # Hiển thị các node mới nhất lên Frontier
        frontier_preview_list = [node.board for node in self.frontier][-5:][::-1]

        return {
            "status": "expanding",
            "current": current_node,
            "children_info": children_info, 
            "frontier_preview": frontier_preview_list, 
            "reached_count": len(self.reached),
            "frontier_count": len(self.frontier)
        }