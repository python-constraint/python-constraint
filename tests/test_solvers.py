from constraint import Problem, MinConflictsSolver


def test_min_conflicts_solver():
    problem = Problem(MinConflictsSolver())
    problem.addVariable("x", [0, 1])
    problem.addVariable("y", [0, 1])
    solution = problem.getSolution()

    assert solution == {'x': 0, 'y': 0}
