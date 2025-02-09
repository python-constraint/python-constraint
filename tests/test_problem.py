from constraint import Constraint, Domain, Problem


def test_addVariable_support_domain_subclasses():
    class MyCustomDomain(Domain):
        pass

    class MyConstraint(Constraint):
        def __call__(self, variables, domains, assignments, forwardcheck=False):
            assert isinstance(domains["x"], Domain)
            assert isinstance(domains["y"], MyCustomDomain)
            return True

    problem = Problem()
    problem.addVariable("x", [0, 1])
    problem.addVariable("y", MyCustomDomain([0, 1]))
    problem.addConstraint(MyConstraint())
    solution = problem.getSolution()

    possible_solutions = [
        {"x": 0, "y": 0},
        {"x": 0, "y": 1},
        {"x": 1, "y": 0},
        {"x": 1, "y": 1},
    ]

    assert solution in possible_solutions


def test_addVariable_string_constraint():
    problem = Problem()
    problem.addVariable("x", [0, 1])
    problem.addVariable("y", [0, 1])
    problem.addConstraint("x != y")
    solutions = problem.getSolutions()

    possible_solutions = [
        {"x": 0, "y": 1},
        {"x": 1, "y": 0},
    ]

    assert len(solutions) == len(possible_solutions)
    for solution in solutions:
        assert solution in possible_solutions

    assert solution in possible_solutions

def test_addVariable_string_constraints():
    problem = Problem()
    problem.addVariable("x", [0, 1, 2])
    problem.addVariable("y", [0, 1, 2])
    problem.addConstraint(["x >= 1", "y > 0", "x != y"])
    solutions = problem.getSolutions()

    possible_solutions = [
        {"x": 1, "y": 2},
        {"x": 2, "y": 1},
    ]

    assert len(solutions) == len(possible_solutions)
    for solution in solutions:
        assert solution in possible_solutions

    assert solution in possible_solutions

