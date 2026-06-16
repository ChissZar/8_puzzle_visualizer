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
