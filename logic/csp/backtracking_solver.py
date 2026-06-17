import random


class CSPNode:
    def __init__(self, assignment, variables, parent=None, move=None):
        self.assignment = dict(assignment)
        self.variables = variables
        self.parent = parent
        self.move = move
        self.board = self.assignment_to_board()
        self.f = 0

    def assignment_to_board(self):
        board = []
        for var in self.variables:
            board.append(self.assignment.get(var, None))
        return tuple(board)


class BacktrackingCSPSolver:
    def __init__(self, initial_board=None, goal_board=(1, 2, 3, 4, 5, 6, 7, 8, 0)):
        self.goal_board = tuple(goal_board)
        self.variables = [f"x{i}" for i in range(1, 10)]
        self.positions = {
            var: divmod(index, 3)
            for index, var in enumerate(self.variables)
        }
        self.domains = {
            var: list(range(9))
            for var in self.variables
        }
        self.fixed_values = {
            var: self.goal_board[index]
            for index, var in enumerate(self.variables)
        }

        self.initial_node = CSPNode({}, self.variables)
        self.current_node = self.initial_node
        self.is_finished = False
        self.generator = self.backtracking_search()

    def is_complete(self, assignment):
        return len(assignment) == len(self.variables)

    def select_unassigned_variable(self, assignment):
        for var in self.variables:
            if var not in assignment:
                return var
        return None

    def order_domain_values(self, var, assignment):
        values = list(self.domains[var])
        random.shuffle(values)
        return values

    def consistent(self, var, value, assignment):
        if value in assignment.values():
            return False, f"{value} already appears in another cell"

        fixed_value = self.fixed_values[var]
        if value != fixed_value:
            row, col = self.positions[var]
            return False, f"cell ({row},{col}) must be {fixed_value}"

        return True, "unique value and fixed cell constraint satisfied"

    def get_path(self, node):
        path = []
        current = node
        while current:
            path.append(current)
            current = current.parent
        return path[::-1]

    def assignment_to_board(self, assignment):
        return tuple(assignment.get(var, None) for var in self.variables)

    def make_snapshot(self, assignment, stage, selected_var=None, trying_value=None, domain_order=None, message=""):
        return {
            "variables": self.variables,
            "domains": self.domains,
            "current_domains": {
                var: list(values)
                for var, values in self.domains.items()
            },
            "positions": self.positions,
            "fixed_values": self.fixed_values,
            "assignment": dict(assignment),
            "board": self.assignment_to_board(assignment),
            "stage": stage,
            "selected_var": selected_var,
            "trying_value": trying_value,
            "domain_order": list(domain_order) if domain_order else [],
            "message": message
        }

    def build_response(self, status, node, snapshot):
        return {
            "status": status,
            "current": node,
            "csp_snapshot": snapshot,
            "frontier_count": len(node.assignment),
            "frontier_preview": []
        }

    def backtracking_search(self):
        result = yield from self.backtrack({}, self.initial_node)

        if result == "failure":
            yield self.build_response(
                "failure",
                self.current_node,
                self.make_snapshot(
                    self.current_node.assignment,
                    "failure",
                    message="No assignment satisfies the 8-puzzle CSP constraints."
                )
            )
        else:
            yield {
                "status": "success",
                "current": result,
                "solution_node": result,
                "path": self.get_path(result),
                "frontier_count": len(result.assignment),
                "frontier_preview": [],
                "csp_snapshot": self.make_snapshot(
                    result.assignment,
                    "success",
                    message="Assignment is complete. Every cell has its goal value and no value repeats."
                )
            }

    def backtrack(self, assignment, current_node):
        self.current_node = current_node

        if self.is_complete(assignment):
            return current_node

        var = self.select_unassigned_variable(assignment)
        row, col = self.positions[var]
        ordered_values = self.order_domain_values(var, assignment)
        yield self.build_response(
            "running",
            current_node,
            self.make_snapshot(
                assignment,
                "select",
                selected_var=var,
                domain_order=ordered_values,
                message=f"SELECT-UNASSIGNED-VARIABLE -> {var} at cell ({row},{col}); random domain order = {ordered_values}"
            )
        )

        for value in ordered_values:
            is_consistent, reason = self.consistent(var, value, assignment)
            stage = "consistent" if is_consistent else "reject"
            message = (
                f"CONSISTENT({var}, {value}) = TRUE. Add {var} = {value}."
                if is_consistent
                else f"CONSISTENT({var}, {value}) = FALSE: {reason}."
            )

            trial_assignment = dict(assignment)
            trial_assignment[var] = value
            trial_node = CSPNode(trial_assignment, self.variables, current_node, f"{var} = {value}")

            yield self.build_response(
                "running",
                trial_node,
                self.make_snapshot(
                    trial_assignment,
                    stage,
                    selected_var=var,
                    trying_value=value,
                    domain_order=ordered_values,
                    message=message
                )
            )

            if is_consistent:
                result = yield from self.backtrack(trial_assignment, trial_node)
                if result != "failure":
                    return result

                yield self.build_response(
                    "running",
                    current_node,
                    self.make_snapshot(
                        assignment,
                        "backtrack",
                        selected_var=var,
                        trying_value=value,
                        domain_order=ordered_values,
                        message=f"Remove {var} = {value}. Backtrack to previous assignment."
                    )
                )

        return "failure"

    def initial_snapshot(self):
        return self.make_snapshot(
            {},
            "start",
            message="BACKTRACKING-SEARCH starts with an empty assignment for x1...x9."
        )

    def step(self):
        if self.is_finished:
            return self.build_response(
                "failure",
                self.current_node,
                self.make_snapshot(self.current_node.assignment, "failure")
            )

        try:
            data = next(self.generator)
            self.current_node = data.get("current", self.current_node)
            if data["status"] in ["success", "failure"]:
                self.is_finished = True
            return data
        except StopIteration:
            self.is_finished = True
            return self.build_response(
                "failure",
                self.current_node,
                self.make_snapshot(self.current_node.assignment, "failure")
            )


class ForwardCheckingCSPSolver(BacktrackingCSPSolver):
    def __init__(self, initial_board=None, goal_board=(1, 2, 3, 4, 5, 6, 7, 8, 0)):
        super().__init__(initial_board, goal_board)
        self.generator = self.backtracking_search()

    def make_snapshot(self, assignment, stage, selected_var=None, trying_value=None, domain_order=None, current_domains=None, message=""):
        active_domains = current_domains if current_domains is not None else self.domains
        return {
            "variables": self.variables,
            "domains": self.domains,
            "current_domains": {
                var: list(values)
                for var, values in active_domains.items()
            },
            "positions": self.positions,
            "fixed_values": self.fixed_values,
            "assignment": dict(assignment),
            "board": self.assignment_to_board(assignment),
            "stage": stage,
            "selected_var": selected_var,
            "trying_value": trying_value,
            "domain_order": list(domain_order) if domain_order else [],
            "message": message
        }

    def order_domain_values(self, var, assignment, current_domains=None):
        domains = current_domains if current_domains is not None else self.domains
        values = list(domains[var])
        random.shuffle(values)
        return values

    def revise_domains(self, var, value, assignment, current_domains):
        new_domains = {
            candidate: list(values)
            for candidate, values in current_domains.items()
        }
        pruned = {}

        for other_var in self.variables:
            if other_var == var or other_var in assignment:
                continue
            if value in new_domains[other_var]:
                new_domains[other_var].remove(value)
                pruned.setdefault(other_var, []).append(value)

        return new_domains, pruned

    def has_empty_domain(self, assignment, current_domains):
        for var in self.variables:
            if var not in assignment and not current_domains[var]:
                return var
        return None

    def format_pruned(self, pruned):
        if not pruned:
            return "no domain pruning needed"
        parts = []
        for var, values in pruned.items():
            parts.append(f"{var}: remove {values}")
        return "; ".join(parts)

    def backtracking_search(self):
        initial_domains = {
            var: list(values)
            for var, values in self.domains.items()
        }
        result = yield from self.backtrack({}, self.initial_node, initial_domains)

        if result == "failure":
            yield self.build_response(
                "failure",
                self.current_node,
                self.make_snapshot(
                    self.current_node.assignment,
                    "failure",
                    current_domains=initial_domains,
                    message="No assignment satisfies the 8-puzzle CSP constraints."
                )
            )
        else:
            yield {
                "status": "success",
                "current": result,
                "solution_node": result,
                "path": self.get_path(result),
                "frontier_count": len(result.assignment),
                "frontier_preview": [],
                "csp_snapshot": self.make_snapshot(
                    result.assignment,
                    "success",
                    current_domains=initial_domains,
                    message="Assignment is complete. Forward checking preserved all constraints."
                )
            }

    def backtrack(self, assignment, current_node, current_domains):
        self.current_node = current_node

        if self.is_complete(assignment):
            return current_node

        var = self.select_unassigned_variable(assignment)
        row, col = self.positions[var]
        ordered_values = self.order_domain_values(var, assignment, current_domains)
        yield self.build_response(
            "running",
            current_node,
            self.make_snapshot(
                assignment,
                "select",
                selected_var=var,
                domain_order=ordered_values,
                current_domains=current_domains,
                message=f"SELECT-UNASSIGNED-VARIABLE -> {var} at cell ({row},{col}); random D({var}) = {ordered_values}"
            )
        )

        for value in ordered_values:
            is_consistent, reason = self.consistent(var, value, assignment)
            trial_assignment = dict(assignment)
            trial_assignment[var] = value
            trial_node = CSPNode(trial_assignment, self.variables, current_node, f"{var} = {value}")

            if not is_consistent:
                yield self.build_response(
                    "running",
                    trial_node,
                    self.make_snapshot(
                        trial_assignment,
                        "reject",
                        selected_var=var,
                        trying_value=value,
                        domain_order=ordered_values,
                        current_domains=current_domains,
                        message=f"CONSISTENT({var}, {value}) = FALSE: {reason}."
                    )
                )
                continue

            reduced_domains, pruned = self.revise_domains(var, value, assignment, current_domains)
            empty_var = self.has_empty_domain(trial_assignment, reduced_domains)
            message = (
                f"Add {var} = {value}. Forward checking -> {self.format_pruned(pruned)}."
            )
            stage = "consistent" if empty_var is None else "reject"
            if empty_var is not None:
                message += f" Failure because D({empty_var}) becomes empty."

            yield self.build_response(
                "running",
                trial_node,
                self.make_snapshot(
                    trial_assignment,
                    stage,
                    selected_var=var,
                    trying_value=value,
                    domain_order=ordered_values,
                    current_domains=reduced_domains,
                    message=message
                )
            )

            if empty_var is not None:
                continue

            result = yield from self.backtrack(trial_assignment, trial_node, reduced_domains)
            if result != "failure":
                return result

            yield self.build_response(
                "running",
                current_node,
                self.make_snapshot(
                    assignment,
                    "backtrack",
                    selected_var=var,
                    trying_value=value,
                    domain_order=ordered_values,
                    current_domains=current_domains,
                    message=f"Remove {var} = {value}. Restore domains and backtrack."
                )
            )

        return "failure"

    def initial_snapshot(self):
        return self.make_snapshot(
            {},
            "start",
            current_domains=self.domains,
            message="BACKTRACKING + FORWARD CHECKING starts with D(x1)...D(x9) = {0...8}."
        )


class AC3CSPSolver(BacktrackingCSPSolver):
    def __init__(self, initial_board=None, goal_board=(1, 2, 3, 4, 5, 6, 7, 8, 0)):
        super().__init__(initial_board, goal_board)
        self.arcs = [
            (xi, xj)
            for xi in self.variables
            for xj in self.variables
            if xi != xj
        ]
        self.generator = self.ac3_search()

    def binary_consistent(self, xi, x, xj, y):
        return (
            x == self.fixed_values[xi]
            and y == self.fixed_values[xj]
            and x != y
        )

    def neighbors(self, var):
        return [candidate for candidate in self.variables if candidate != var]

    def singleton_assignment(self, domains):
        return {
            var: values[0]
            for var, values in domains.items()
            if len(values) == 1
        }

    def make_snapshot(
        self,
        assignment,
        stage,
        selected_var=None,
        trying_value=None,
        domain_order=None,
        current_domains=None,
        current_arc=None,
        removed_values=None,
        queue_preview=None,
        queue_size=0,
        message=""
    ):
        active_domains = current_domains if current_domains is not None else self.domains
        return {
            "variables": self.variables,
            "domains": self.domains,
            "current_domains": {
                var: list(values)
                for var, values in active_domains.items()
            },
            "positions": self.positions,
            "fixed_values": self.fixed_values,
            "assignment": dict(assignment),
            "board": self.assignment_to_board(assignment),
            "stage": stage,
            "selected_var": selected_var,
            "peer_var": current_arc[1] if current_arc else None,
            "trying_value": trying_value,
            "domain_order": list(domain_order) if domain_order else [],
            "current_arc": current_arc,
            "removed_values": list(removed_values) if removed_values else [],
            "queue_preview": list(queue_preview) if queue_preview else [],
            "queue_size": queue_size,
            "message": message
        }

    def format_arc(self, arc):
        return f"({arc[0]}, {arc[1]})"

    def format_queue_preview(self, queue):
        if not queue:
            return "[]"
        shown = ", ".join(self.format_arc(arc) for arc in queue[:6])
        if len(queue) > 6:
            shown += f", ... +{len(queue) - 6}"
        return shown

    def revise(self, xi, xj, domains):
        removed = []
        for x in list(domains[xi]):
            has_support = any(
                self.binary_consistent(xi, x, xj, y)
                for y in domains[xj]
            )
            if not has_support:
                domains[xi].remove(x)
                removed.append(x)
        return removed

    def ac3_search(self):
        domains = {
            var: list(values)
            for var, values in self.domains.items()
        }
        queue = list(self.arcs)
        self.current_node = CSPNode(self.singleton_assignment(domains), self.variables)

        yield self.build_response(
            "running",
            self.current_node,
            self.make_snapshot(
                self.current_node.assignment,
                "start",
                current_domains=domains,
                queue_preview=queue,
                queue_size=len(queue),
                message=f"AC-3 starts. Queue initially contains all {len(queue)} directed arcs."
            )
        )

        while queue:
            xi, xj = queue.pop(0)
            removed = self.revise(xi, xj, domains)
            stage = "revise" if removed else "check"

            if removed:
                message = (
                    f"RM-INCONSISTENT-VALUES{self.format_arc((xi, xj))}: "
                    f"remove {removed} from D({xi})."
                )
            else:
                message = (
                    f"RM-INCONSISTENT-VALUES{self.format_arc((xi, xj))}: "
                    f"no value removed from D({xi})."
                )

            if not domains[xi]:
                self.current_node = CSPNode(self.singleton_assignment(domains), self.variables, self.current_node, f"Revise {self.format_arc((xi, xj))}")
                yield self.build_response(
                    "failure",
                    self.current_node,
                    self.make_snapshot(
                        self.current_node.assignment,
                        "failure",
                        selected_var=xi,
                        current_domains=domains,
                        current_arc=(xi, xj),
                        removed_values=removed,
                        queue_preview=queue,
                        queue_size=len(queue),
                        message=message + f" Failure: D({xi}) is empty."
                    )
                )
                return

            if removed:
                added_arcs = []
                for xk in self.neighbors(xi):
                    if xk == xj:
                        continue
                    arc = (xk, xi)
                    queue.append(arc)
                    added_arcs.append(arc)

                if added_arcs:
                    message += " Add related arcs back to queue: "
                    message += ", ".join(self.format_arc(arc) for arc in added_arcs[:5])
                    if len(added_arcs) > 5:
                        message += f", ... +{len(added_arcs) - 5}"

            self.current_node = CSPNode(
                self.singleton_assignment(domains),
                self.variables,
                self.current_node,
                f"Revise {self.format_arc((xi, xj))}"
            )
            yield self.build_response(
                "running",
                self.current_node,
                self.make_snapshot(
                    self.current_node.assignment,
                    stage,
                    selected_var=xi,
                    current_domains=domains,
                    current_arc=(xi, xj),
                    removed_values=removed,
                    queue_preview=queue,
                    queue_size=len(queue),
                    message=message
                )
            )

        result = CSPNode(
            self.singleton_assignment(domains),
            self.variables,
            self.current_node,
            "AC-3 complete"
        )
        self.current_node = result
        yield {
            "status": "success",
            "current": result,
            "solution_node": result,
            "path": self.get_path(result),
            "frontier_count": 0,
            "frontier_preview": [],
            "csp_snapshot": self.make_snapshot(
                result.assignment,
                "success",
                current_domains=domains,
                queue_preview=[],
                queue_size=0,
                message="Queue is empty. CSP is arc-consistent; every domain is reduced to the goal value."
            )
        }

    def initial_snapshot(self):
        return self.make_snapshot(
            {},
            "start",
            current_domains=self.domains,
            queue_preview=self.arcs,
            queue_size=len(self.arcs),
            message=f"AC-3 initializes queue with all {len(self.arcs)} arcs (Xi, Xj)."
        )


class MinConflictsCSPSolver(BacktrackingCSPSolver):
    def __init__(self, initial_board=None, goal_board=(1, 2, 3, 4, 5, 6, 7, 8, 0), max_steps=100):
        super().__init__(initial_board, goal_board)
        self.max_steps = max_steps
        self.initial_assignment = self.make_initial_assignment(initial_board)
        self.initial_node = CSPNode(self.initial_assignment, self.variables)
        self.current_node = self.initial_node
        self.generator = self.min_conflicts_search()

    def make_initial_assignment(self, initial_board):
        if initial_board is not None:
            board = tuple(initial_board)
            if len(board) == 9 and set(board) == set(range(9)):
                return {
                    var: board[index]
                    for index, var in enumerate(self.variables)
                }

        values = list(range(9))
        random.shuffle(values)
        return {
            var: values[index]
            for index, var in enumerate(self.variables)
        }

    def total_conflicts(self, assignment):
        conflicts = 0

        for var in self.variables:
            if assignment[var] != self.fixed_values[var]:
                conflicts += 1

        for left_index, left_var in enumerate(self.variables):
            for right_var in self.variables[left_index + 1:]:
                if assignment[left_var] == assignment[right_var]:
                    conflicts += 1

        return conflicts

    def conflicts_for_value(self, var, value, assignment):
        conflicts = 0

        if value != self.fixed_values[var]:
            conflicts += 1

        for other_var in self.variables:
            if other_var == var:
                continue
            if assignment[other_var] == value:
                conflicts += 1

        return conflicts

    def conflicted_variables(self, assignment):
        conflicted = []

        for var in self.variables:
            has_conflict = assignment[var] != self.fixed_values[var]

            if not has_conflict:
                for other_var in self.variables:
                    if other_var != var and assignment[other_var] == assignment[var]:
                        has_conflict = True
                        break

            if has_conflict:
                conflicted.append(var)

        return conflicted

    def choose_min_conflict_value(self, var, assignment):
        scores = {
            value: self.conflicts_for_value(var, value, assignment)
            for value in self.domains[var]
        }
        best_score = min(scores.values())
        best_values = [
            value
            for value, score in scores.items()
            if score == best_score
        ]

        goal_value = self.fixed_values[var]
        if goal_value in best_values:
            return goal_value, scores

        return random.choice(best_values), scores

    def choose_repair_move(self, conflicted, assignment):
        current_total = self.total_conflicts(assignment)
        moves = []

        for var in conflicted:
            scores = {
                value: self.conflicts_for_value(var, value, assignment)
                for value in self.domains[var]
            }
            best_score = min(scores.values())
            best_values = [
                value
                for value, score in scores.items()
                if score == best_score
            ]

            for value in best_values:
                trial = dict(assignment)
                trial[var] = value
                total_after = self.total_conflicts(trial)
                moves.append({
                    "var": var,
                    "value": value,
                    "scores": scores,
                    "total_after": total_after,
                    "changed": value != assignment[var],
                    "improves": total_after < current_total
                })

        improving_moves = [move for move in moves if move["changed"] and move["improves"]]
        candidate_moves = improving_moves
        if not candidate_moves:
            candidate_moves = [move for move in moves if move["changed"]]
        if not candidate_moves:
            candidate_moves = moves

        best_total = min(move["total_after"] for move in candidate_moves)
        best_moves = [
            move
            for move in candidate_moves
            if move["total_after"] == best_total
        ]

        goal_moves = [
            move
            for move in best_moves
            if move["value"] == self.fixed_values[move["var"]]
        ]
        if goal_moves:
            return random.choice(goal_moves)

        return random.choice(best_moves)

    def make_snapshot(
        self,
        assignment,
        stage,
        selected_var=None,
        trying_value=None,
        candidate_scores=None,
        conflicted_vars=None,
        local_step=0,
        message=""
    ):
        return {
            "variables": self.variables,
            "domains": self.domains,
            "current_domains": {
                var: list(values)
                for var, values in self.domains.items()
            },
            "positions": self.positions,
            "fixed_values": self.fixed_values,
            "assignment": dict(assignment),
            "board": self.assignment_to_board(assignment),
            "stage": stage,
            "selected_var": selected_var,
            "trying_value": trying_value,
            "chosen_value": trying_value,
            "domain_order": list(self.domains[selected_var]) if selected_var else [],
            "candidate_scores": dict(candidate_scores) if candidate_scores else {},
            "conflicted_vars": list(conflicted_vars) if conflicted_vars else [],
            "local_step": local_step,
            "max_steps": self.max_steps,
            "total_conflicts": self.total_conflicts(assignment),
            "message": message
        }

    def min_conflicts_search(self):
        current = dict(self.initial_assignment)
        current_node = self.initial_node
        self.current_node = current_node

        yield self.build_response(
            "running",
            current_node,
            self.make_snapshot(
                current,
                "start",
                conflicted_vars=self.conflicted_variables(current),
                local_step=0,
                message="MIN-CONFLICTS starts with a complete assignment from CUSTOM INITIAL BOARD."
            )
        )

        for step in range(1, self.max_steps + 1):
            conflicted = self.conflicted_variables(current)

            if not conflicted:
                result = CSPNode(current, self.variables, current_node, "solution")
                self.current_node = result
                yield {
                    "status": "success",
                    "current": result,
                    "solution_node": result,
                    "path": self.get_path(result),
                    "frontier_count": 0,
                    "frontier_preview": [],
                    "csp_snapshot": self.make_snapshot(
                        current,
                        "success",
                        conflicted_vars=[],
                        local_step=step,
                        message="Current assignment is a solution: no fixed-cell or all-different conflict remains."
                    )
                }
                return

            move = self.choose_repair_move(conflicted, current)
            var = move["var"]
            value = move["value"]
            candidate_scores = move["scores"]
            old_value = current[var]

            yield self.build_response(
                "running",
                current_node,
                self.make_snapshot(
                    current,
                    "select_conflicted",
                    selected_var=var,
                    candidate_scores={},
                    conflicted_vars=conflicted,
                    local_step=step,
                    message=(
                        f"Step {step}: choose conflicted variable {var} "
                        f"from {conflicted}. Now evaluate every value in D({var})."
                    )
                )
            )

            evaluated_scores = {}
            for candidate_value in self.domains[var]:
                evaluated_scores[candidate_value] = candidate_scores[candidate_value]
                yield self.build_response(
                    "running",
                    current_node,
                    self.make_snapshot(
                        current,
                        "evaluate_conflict",
                        selected_var=var,
                        trying_value=candidate_value,
                        candidate_scores=evaluated_scores,
                        conflicted_vars=conflicted,
                        local_step=step,
                        message=(
                            f"Try {var} = {candidate_value}: "
                            f"CONFLICTS({var}, {candidate_value}) = {candidate_scores[candidate_value]}."
                        )
                    )
                )

            current[var] = value
            current_node = CSPNode(
                current,
                self.variables,
                current_node,
                f"{var}: {old_value} -> {value}"
            )
            self.current_node = current_node

            next_conflicted = self.conflicted_variables(current)
            yield self.build_response(
                "running",
                current_node,
                self.make_snapshot(
                    current,
                    "min_conflicts",
                    selected_var=var,
                    trying_value=value,
                    candidate_scores=candidate_scores,
                    conflicted_vars=next_conflicted,
                    local_step=step,
                    message=(
                        f"Step {step}: choose conflicted variable {var}; "
                        f"set {var}: {old_value} -> {value}. "
                        f"Total conflicts becomes {move['total_after']}."
                    )
                )
            )

        yield self.build_response(
            "failure",
            self.current_node,
            self.make_snapshot(
                self.current_node.assignment,
                "failure",
                conflicted_vars=self.conflicted_variables(self.current_node.assignment),
                local_step=self.max_steps,
                message=f"MIN-CONFLICTS reached max_steps = {self.max_steps} before finding a solution."
            )
        )

    def initial_snapshot(self):
        return self.make_snapshot(
            self.initial_assignment,
            "start",
            conflicted_vars=self.conflicted_variables(self.initial_assignment),
            local_step=0,
            message="MIN-CONFLICTS starts with a complete assignment, then repairs conflicted variables."
        )
