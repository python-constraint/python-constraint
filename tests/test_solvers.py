from constraint import Problem, MinConflictsSolver


def test_min_conflicts_solver():
    problem = Problem(MinConflictsSolver())
    problem.addVariable("x", [0, 1])
    problem.addVariable("y", [0, 1])
    solution = problem.getSolution()

    possible_solutions = [
        {'x': 0, 'y': 0},
        {'x': 0, 'y': 1},
        {'x': 1, 'y': 0},
        {'x': 1, 'y': 1}
    ]

    assert solution in possible_solutions
