from constraint import Constraint, Domain, Problem


def test_addVariable_support_domain_subclasses():
    class MyCustomDomain(Domain):
        pass

    class MyConstraint(Constraint):
        def __call__(self, variables, domains,
                     assignments, forwardcheck=False):
            print(variables)
            assert isinstance(domains[variables[0]], Domain)
            assert isinstance(domains[variables[1]], MyCustomDomain)
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
