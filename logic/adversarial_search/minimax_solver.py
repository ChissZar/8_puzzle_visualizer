class MinimaxNode:
    def __init__(self, node_id, board, player, parent_id=None, move=None, depth=0):
        self.id = node_id
        self.board = tuple(board)
        self.player = player
        self.parent_id = parent_id
        self.move = move
        self.depth = depth
        self.children = []
        self.value = None
        self.best_child_id = None
        self.is_terminal = False
        self.winner = None


class MinimaxSolver:
    def __init__(self, initial_board=None, goal_board=None):
        self.initial_board = (
            "X", "O", "X",
            "O", "O", "X",
            "", "", "",
        )
        self.root_player = "X"
        self.nodes = {}
        self.node_order = []
        self.next_id = 1
        self.initial_node = self.create_tree(self.initial_board, self.root_player)
        self.root_id = self.initial_node.id
        self.current_node = self.initial_node
        self.events = []
        self.is_finished = False
        self.solution_path = []
        self.plan_minimax(self.initial_node)
        self.events.append({
            "kind": "success",
            "node_id": self.root_id,
            "message": "MINIMAX DONE: MAX chọn nhánh có utility tốt nhất.",
        })
        self.event_index = 0

    def new_node(self, board, player, parent_id=None, move=None, depth=0):
        node = MinimaxNode(self.next_id, board, player, parent_id, move, depth)
        self.next_id += 1
        self.nodes[node.id] = node
        self.node_order.append(node.id)
        return node

    def create_tree(self, board, player, parent_id=None, move=None, depth=0):
        node = self.new_node(board, player, parent_id, move, depth)
        winner = self.get_winner(board)
        if winner or self.is_full(board):
            node.is_terminal = True
            node.winner = winner
            return node

        next_player = "O" if player == "X" else "X"
        for index, cell in enumerate(board):
            if cell == "":
                child_board = list(board)
                child_board[index] = player
                child = self.create_tree(child_board, next_player, node.id, index + 1, depth + 1)
                node.children.append(child.id)
        return node

    def get_winner(self, board):
        lines = (
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6),
        )
        for a, b, c in lines:
            if board[a] and board[a] == board[b] == board[c]:
                return board[a]
        return None

    def is_full(self, board):
        return all(cell != "" for cell in board)

    def utility(self, board):
        winner = self.get_winner(board)
        if winner == "X":
            return 10
        if winner == "O":
            return -10
        return 0

    def plan_minimax(self, node):
        role = "MAX" if node.player == "X" else "MIN"
        self.events.append({
            "kind": "visit",
            "node_id": node.id,
            "message": f"Visit Node {node.id}: {role} đang xét trạng thái này.",
        })

        if node.is_terminal:
            value = self.utility(node.board)
            result = "X thắng" if value == 10 else "O thắng" if value == -10 else "Hòa"
            self.events.append({
                "kind": "terminal",
                "node_id": node.id,
                "value": value,
                "message": f"Terminal Node {node.id}: {result}, utility = {value}.",
            })
            return value

        child_values = []
        for child_id in node.children:
            child = self.nodes[child_id]
            value = self.plan_minimax(child)
            child_values.append((child_id, value))
            self.events.append({
                "kind": "return",
                "node_id": node.id,
                "child_id": child_id,
                "message": f"Node {child_id} trả về {value} cho Node {node.id}.",
            })

        if node.player == "X":
            best_child_id, best_value = max(child_values, key=lambda item: item[1])
        else:
            best_child_id, best_value = min(child_values, key=lambda item: item[1])

        chooser = "MAX lấy max" if node.player == "X" else "MIN lấy min"
        self.events.append({
            "kind": "choose",
            "node_id": node.id,
            "child_id": best_child_id,
            "value": best_value,
            "message": f"{chooser} tại Node {node.id}: chọn Node {best_child_id}, value = {best_value}.",
        })
        return best_value

    def apply_event(self, event):
        kind = event.get("kind")
        node = self.nodes.get(event.get("node_id"))
        if not node:
            return

        if kind == "terminal":
            node.value = event["value"]
        elif kind == "choose":
            node.value = event["value"]
            node.best_child_id = event["child_id"]
        elif kind == "success":
            self.solution_path = self.get_best_path_ids()

    def get_best_path_ids(self):
        path = []
        current = self.nodes[self.root_id]
        while current:
            path.append(current.id)
            if current.best_child_id is None:
                break
            current = self.nodes[current.best_child_id]
        return path

    def make_snapshot(self, event=None):
        active_node_id = event.get("node_id") if event else self.root_id
        active_child_id = event.get("child_id") if event else None
        self.current_node = self.nodes.get(active_node_id, self.initial_node)

        return {
            "nodes": [
                {
                    "id": node.id,
                    "board": node.board,
                    "player": node.player,
                    "parent_id": node.parent_id,
                    "move": node.move,
                    "depth": node.depth,
                    "children": list(node.children),
                    "value": node.value,
                    "best_child_id": node.best_child_id,
                    "is_terminal": node.is_terminal,
                    "winner": node.winner,
                }
                for node in self.nodes.values()
            ],
            "root_id": self.root_id,
            "active_node_id": active_node_id,
            "active_child_id": active_child_id,
            "best_path_ids": list(self.solution_path),
            "message": event.get("message") if event else "MINIMAX starts at the root MAX node.",
            "event_kind": event.get("kind") if event else "start",
        }

    def initial_snapshot(self):
        return self.make_snapshot()

    def build_response(self, status, snapshot):
        return {
            "status": status,
            "current": self.current_node,
            "minimax_snapshot": snapshot,
            "frontier_count": 0,
            "frontier_preview": [],
        }

    def step(self):
        if self.is_finished:
            return self.build_response("success", self.make_snapshot({
                "kind": "success",
                "node_id": self.root_id,
                "message": "MINIMAX DONE: MAX chọn nhánh có utility tốt nhất.",
            }))

        event = self.events[self.event_index]
        self.event_index += 1
        self.apply_event(event)
        snapshot = self.make_snapshot(event)
        status = "success" if event["kind"] == "success" else "running"
        if status == "success":
            self.is_finished = True
        return self.build_response(status, snapshot)
