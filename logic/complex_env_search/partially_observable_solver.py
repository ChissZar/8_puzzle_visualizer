from logic.complex_env_search.common import ACTION_ORDER, apply_move, manhattan_distance, normalize_belief


class BeliefNode:
    def __init__(self, boards, parent=None, move=None):
        self.boards = frozenset(normalize_belief(boards))
        self.parent = parent
        self.move = move
        self.f = 0

class PartiallyObservableSolver:
    def __init__(self, initial_boards_list, goal_board=(1, 2, 3, 4, 5, 6, 7, 8, 0), max_depth=8):
        self.goal_board = tuple(goal_board)
        self.initial_state = frozenset(normalize_belief(initial_boards_list))
        self.initial_node = BeliefNode(self.initial_state)
        self.max_depth = max_depth
        self.failed_beliefs = set()
        self.solved_plans = {}

        self.is_finished = False
        self.generator = self.partially_observable_search()

    def apply_move(self, board, move):
        return apply_move(board, move)
    
    def get_observations(self, belief_state, action):
        predicted_boards = set(self.apply_move(b, action) for b in belief_state)
        groups = {}
        for b in predicted_boards:
            empty_idx = b.index(0) # Nhánh AND: Môi trường đọc cảm biến vị trí ô trống
            if empty_idx not in groups:
                groups[empty_idx] = set()
            groups[empty_idx].add(b)
        return [frozenset(g) for g in groups.values()] # Trả về các nhánh Belief State bị tách ra

    def ordered_actions(self, belief_state):
        def action_score(action):
            percepts = self.get_observations(belief_state, action)
            worst_branch_size = max(len(percept) for percept in percepts)
            total_distance = sum(
                manhattan_distance(board, self.goal_board)
                for percept in percepts
                for board in percept
            )
            return (worst_branch_size, len(percepts), total_distance)

        return sorted(ACTION_ORDER, key=action_score)

    def partially_observable_search(self):
        plan = yield from self.or_search(self.initial_state, [], self.initial_node, 0)

        if plan == "failure":
            yield {"status": "failure", "current": self.initial_node}
        else:
            yield {"status": "success", "current": self.initial_node, "solution_node": self.initial_node, "path": [self.initial_node], "frontier_preview": sorted(self.initial_state), "frontier_count": 0, "plan": plan, "goal_board": self.goal_board}

    def or_search(self, belief_state, path, parent_node, depth):
        current_node = BeliefNode(belief_state, parent=parent_node)

        preview = sorted(belief_state) + ["SEPARATOR"]
        yield {"status": "running", "current": current_node, "frontier_preview": preview[:10], "frontier_count": len(path), "goal_board": self.goal_board}

        if len(belief_state) == 1 and self.goal_board in belief_state:
            return []

        if belief_state in self.solved_plans:
            return self.solved_plans[belief_state]

        if belief_state in path or belief_state in self.failed_beliefs or depth >= self.max_depth:
            return "failure"

        for action in self.ordered_actions(belief_state):
            current_node.move = action
            
            percepts = self.get_observations(belief_state, action)
            children_info = {
                action: {
                    "node": BeliefNode(frozenset().union(*percepts), current_node, action),
                    "type": "new",
                    "belief_size": sum(len(percept) for percept in percepts),
                    "percepts": percepts
                }
            }
            yield {
                "status": "running",
                "current": current_node,
                "children_info": children_info,
                "selected_action": action,
                "frontier_preview": preview[:10],
                "frontier_count": len(path),
                "goal_board": self.goal_board
            }

            plan = yield from self.and_search(percepts, path + [belief_state], current_node, depth + 1)

            if plan != "failure":
                final_plan = [action, plan]
                self.solved_plans[belief_state] = final_plan
                return final_plan

        self.failed_beliefs.add(belief_state)
        return "failure"

    def and_search(self, percepts, path, parent_node, depth):
        plans = {}
        for percept in percepts:
            plan_s = yield from self.or_search(percept, path, parent_node, depth)
            if plan_s == "failure":
                return "failure"
            plans[percept] = plan_s
        return plans

    def step(self):
        if self.is_finished:
            return {"status": "failure", "current": getattr(self, 'current_node', self.initial_node)}
        try:
            data = next(self.generator)
            self.current_node = data.get("current", self.initial_node)
            if data["status"] in ["success", "failure"]:
                self.is_finished = True
            return data
        except StopIteration:
            self.is_finished = True
            return {"status": "failure", "current": getattr(self, 'current_node', self.initial_node)}
