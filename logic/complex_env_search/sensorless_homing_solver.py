from logic.complex_env_search.common import ACTION_ORDER, apply_move, build_path, normalize_belief, representative_board


class BeliefNode:
    def __init__(self, boards, parent=None, move=None):
        self.boards = frozenset(normalize_belief(boards))
        self.parent = parent
        self.move = move
        self.f = 0 

class SensorlessHomingSolver:
    def __init__(self, initial_boards_list, goal_board=None):
        # Vẫn để goal_board vào cho đúng cấu trúc hệ thống
        self.initial_node = BeliefNode(normalize_belief(initial_boards_list))
        
        self.frontier = [self.initial_node]
        self.explored = set()
        self.explored.add(self.initial_node.boards)
        self.is_finished = False

    def apply_move(self, board, move):
        return apply_move(board, move)

    def ordered_actions(self, belief_state):
        def action_score(action):
            next_belief = frozenset(self.apply_move(board, action) for board in belief_state)
            repeated_states = len(belief_state) - len(next_belief)
            return (len(next_belief), -repeated_states)

        return sorted(ACTION_ORDER, key=action_score)

    def step(self):
        if self.is_finished or not self.frontier:
            self.is_finished = True
            return {"status": "failure", "current": getattr(self, 'current_node', self.initial_node)}
        
        self.current_node = self.frontier.pop(0)
        current_node = self.current_node

        # Dừng lại ngay khi kích thước Belief State bị ép xuống còn đúng 1 ma trận!
        if len(current_node.boards) == 1:
            self.is_finished = True
            path = build_path(current_node)
            
            preview = sorted(current_node.boards) + ["SEPARATOR"]
            return {
                "status": "success",
                "current": current_node,
                "solution_node": current_node,
                "path": path,
                "frontier_count": len(self.frontier),
                "frontier_preview": preview[:10]
            }

        children_info = {}
        for move in self.ordered_actions(current_node.boards):
            new_boards = set()
            for b in current_node.boards:
                new_boards.add(self.apply_move(b, move))
            
            frozen_new = frozenset(new_boards)
            child_node = BeliefNode(frozen_new, current_node, move)
            
            if frozen_new not in self.explored:
                self.explored.add(frozen_new)
                self.frontier.append(child_node)
                children_info[move] = {
                    "node": child_node,
                    "type": "success" if len(frozen_new) == 1 else "new",
                    "belief_size": len(frozen_new)
                }
            else:
                children_info[move] = {
                    "node": BeliefNode(frozen_new),
                    "type": "reached",
                    "belief_size": len(frozen_new)
                }

        frontier_reps = [representative_board(node.boards) for node in self.frontier]
        preview = sorted(current_node.boards) + ["SEPARATOR"] + frontier_reps
        return {
            "status": "running",
            "current": current_node,
            "children_info": children_info,
            "frontier_preview": preview[:10],
            "frontier_count": len(self.frontier)
        }
