from logic.complex_env_search.common import ACTION_ORDER, apply_move, normalize_board, normalize_belief


class AndOrNode:
    def __init__(self, board, parent=None, move=None):
        self.board = normalize_board(board)
        self.parent = parent
        self.move = move
        self.f = 0

class AndOrGraphSearchSolver:
    def __init__(self, initial_boards_list, goal_board=(1, 2, 3, 4, 5, 6, 7, 8, 0), max_depth=8):
        self.goal_board = tuple(goal_board)
        # Lấy ma trận đầu tiên làm trạng thái xuất phát:
        self.initial_state = normalize_belief(initial_boards_list)[0]
        self.initial_node = AndOrNode(self.initial_state)
        self.max_depth = max_depth
        self.failed_searches = set()
        self.solved_plans = {}
        self.last_tree_snapshot = self.make_tree_snapshot(self.initial_state)

        self.is_finished = False
        self.generator = self.and_or_graph_search()

    def apply_move(self, board, move):
        return apply_move(board, move)

    def heuristic_manhattan(self, board):
        goal_positions = {
            value: divmod(index, 3)
            for index, value in enumerate(self.goal_board)
        }
        distance = 0
        for index, value in enumerate(board):
            if value == 0:
                continue
            row, col = divmod(index, 3)
            goal_row, goal_col = goal_positions[value]
            distance += abs(row - goal_row) + abs(col - goal_col)
        return distance

    def ordered_actions(self, state):
        return sorted(
            ACTION_ORDER,
            key=lambda action: self.heuristic_manhattan(self.apply_move(state, action))
        )

    # ĐÂY LÀ TRÁI TIM CỦA MÔI TRƯỜNG KHÔNG TẤT ĐỊNH
    def get_results(self, board, action):
        intended = self.apply_move(board, action)
        if intended == board:
            return [board]

        # Mô hình demo: hành động có thể thành công hoặc bị trượt và giữ nguyên trạng thái.
        # Nhánh giữ nguyên được xử lý như một vòng lặp retry trong conditional plan.
        return [intended, board]

    def make_tree_snapshot(self, state, action=None, outcomes=None, depth=0, note=""):
        return {
            "root": tuple(state),
            "action": action,
            "outcomes": [tuple(board) for board in outcomes] if outcomes else [],
            "depth": depth,
            "note": note
        }

    def build_response(self, status, current_node, path, tree_snapshot=None):
        if tree_snapshot is not None:
            self.last_tree_snapshot = tree_snapshot

        preview = [current_node.board, "SEPARATOR"]
        if self.last_tree_snapshot.get("outcomes"):
            preview += self.last_tree_snapshot["outcomes"][:8]

        return {
            "status": status,
            "current": current_node,
            "frontier_preview": preview[:10],
            "frontier_count": len(path),
            "tree_snapshot": self.last_tree_snapshot
        }
    
    def and_or_graph_search(self):
        search_result = yield from self.or_search(self.initial_state, [], self.initial_node, 0)

        if search_result == "failure":
            yield {
                "status": "failure",
                "current": self.initial_node,
                "tree_snapshot": self.last_tree_snapshot
            }
        else:
            yield {
                "status": "success",
                "current": self.initial_node,
                "solution_node": self.initial_node,
                "path": [self.initial_node],
                "frontier_preview": [self.initial_state],
                "frontier_count": 0,
                "plan": search_result["plan"],
                "tree_snapshot": self.last_tree_snapshot
            }

    def or_search(self, state, path, parent_node, depth):
        current_node = AndOrNode(state, parent=parent_node)

        # Trả state hiện tại ra UI để vẽ màn hình
        tree = self.make_tree_snapshot(state, depth=depth, note="OR node: AI chooses one action.")
        yield self.build_response("running", current_node, path, tree)

        # Kiểm tra đích
        if state == self.goal_board:
            return {"plan": [], "has_goal": True}

        if state in self.solved_plans:
            return self.solved_plans[state]

        if state in path:
            return {"plan": f"RETRY_FROM_DEPTH_{path.index(state)}", "has_goal": False}

        search_key = (state, self.max_depth - depth)
        if search_key in self.failed_searches or depth >= self.max_depth:
            return "failure"

        # Lượt của AI (Nhánh OR)
        for action in self.ordered_actions(state):
            current_node.move = action
            
            # Lượt của Môi trường (Nhánh AND) - Nhận về nhiều kết quả khó lường
            result_states = self.get_results(state, action)
            if all(result_state == state for result_state in result_states):
                continue

            tree = self.make_tree_snapshot(
                state,
                action=action,
                outcomes=result_states,
                depth=depth,
                note="AND node: every outcome must be solved."
            )
            yield self.build_response("running", current_node, path, tree)

            plan = yield from self.and_search(result_states, path + [state], current_node, depth + 1)

            if plan != "failure" and plan["has_goal"]:
                final_result = {
                    "plan": [action, plan["plan"]],
                    "has_goal": True
                }
                self.solved_plans[state] = final_result
                return final_result

        self.failed_searches.add(search_key)
        return "failure"

    def and_search(self, states, path, parent_node, depth):
        plans = {}
        has_goal_branch = False
        for s in states:
            # Phải đệ quy tìm đường cho TẤT CẢ kịch bản xảy ra
            plan_s = yield from self.or_search(s, path, parent_node, depth)

            # Nếu có 1 kịch bản nào đó đâm vào ngõ cụt -> Kế hoạch thất bại toàn tập
            if plan_s == "failure":
                return "failure" 

            plans[s] = plan_s["plan"]
            has_goal_branch = has_goal_branch or plan_s["has_goal"]

        return {"plan": plans, "has_goal": has_goal_branch}

    def step(self):
        if self.is_finished:
            return {"status": "failure", "current": getattr(self, 'current_node', self.initial_node)}
        
        try:
            data = next(self.generator)
            self.current_node = data.get("current", self.initial_node)
            
            if data["status"] in ["success", "failure"]:
                self.is_finished = True
                if data["status"] == "success":
                    print("TÌM THẤY KẾ HOẠCH CÓ ĐIỀU KIỆN (CONDITIONAL PLAN):", data["plan"])
            return data
            
        except StopIteration:
            self.is_finished = True
            return {"status": "failure", "current": getattr(self, 'current_node', self.initial_node)}
