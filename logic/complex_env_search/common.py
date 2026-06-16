ACTION_ORDER = ("UP", "DOWN", "LEFT", "RIGHT")


def is_single_board(value):
    return (
        isinstance(value, (list, tuple))
        and len(value) == 9
        and all(isinstance(x, int) for x in value)
    )


def normalize_board(board):
    normalized = tuple(board)
    if len(normalized) != 9 or set(normalized) != set(range(9)):
        raise ValueError("Board must contain exactly the numbers 0-8.")
    return normalized


def normalize_belief(boards):
    if is_single_board(boards):
        return [normalize_board(boards)]
    return [normalize_board(board) for board in boards]


def apply_move(board, move):
    board = normalize_board(board)
    empty_idx = board.index(0)
    row, col = divmod(empty_idx, 3)

    dr, dc = 0, 0
    if move == "LEFT":
        dc = -1
    elif move == "RIGHT":
        dc = 1
    elif move == "UP":
        dr = -1
    elif move == "DOWN":
        dr = 1

    new_row, new_col = row + dr, col + dc
    if not (0 <= new_row < 3 and 0 <= new_col < 3):
        return board

    new_idx = new_row * 3 + new_col
    new_board = list(board)
    new_board[empty_idx], new_board[new_idx] = new_board[new_idx], new_board[empty_idx]
    return tuple(new_board)


def manhattan_distance(board, goal_board):
    board = normalize_board(board)
    goal_board = normalize_board(goal_board)
    goal_positions = {
        value: divmod(index, 3)
        for index, value in enumerate(goal_board)
    }

    distance = 0
    for index, value in enumerate(board):
        if value == 0:
            continue
        row, col = divmod(index, 3)
        goal_row, goal_col = goal_positions[value]
        distance += abs(row - goal_row) + abs(col - goal_col)
    return distance


def make_auto_belief(anchor_board):
    """Small deterministic belief set for demos with no observed initial state."""
    anchor_board = normalize_board(anchor_board)
    boards = [anchor_board]
    seen = {anchor_board}

    for action in ACTION_ORDER:
        candidate = apply_move(anchor_board, action)
        if candidate != anchor_board and candidate not in seen:
            boards.append(candidate)
            seen.add(candidate)

    return boards


def representative_board(boards):
    return sorted(boards)[0]


def build_path(node):
    path = []
    current = node
    while current:
        path.append(current)
        current = current.parent
    return path[::-1]
