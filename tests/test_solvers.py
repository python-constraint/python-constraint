from constraint import Problem, MinConflictsSolver, LeastConflictsSolver
import itertools

def test_min_conflicts_solver():
    problem = Problem(MinConflictsSolver())
    problem.addVariable("x", [0, 1])
    problem.addVariable("y", [0, 1])
    solution = problem.getSolution()

    possible_solutions = [
        {"x": 0, "y": 0},
        {"x": 0, "y": 1},
        {"x": 1, "y": 0},
        {"x": 1, "y": 1},
    ]

    assert solution in possible_solutions


def test_least_conflicts_solver():
    problem = Problem(LeastConflictsSolver())
    problem.addVariable("x", [0,1,2])
    problem.addVariable("y", [1,2])
    problem.addVariable("z", [0,1])
    problem.addVariable("w", [2])
    for first, sec in itertools.combinations('xyzw', 2) :
        problem.addConstraint(lambda a, b: b != a, [first, sec])


    solution = problem.getSolution()

    # possible_solutions =
    #     {"x": 0, "y": 0},
    #     {"x": 0, "y": 1},
    #     {"x": 1, "y": 0},
    #     {"x": 1, "y": 1},
    # ]

    print(solution)

    problem = Problem(LeastConflictsSolver())


    result = [[('a', 1), ('b', 2), ('c', 1)], [('a', 2), ('b', 1), ('c', 1)]]

    problem.addVariables(["a", "b"], [1, 2])
    problem.addVariable("c", [1])
    problem.addConstraint(lambda a, b: b != a, ["a", "b"])
    problem.addConstraint(lambda a, b: b != a, ["a", "c"])
    problem.addConstraint(lambda a, b: b != a, ["b", "c"])

    solution = problem.getSolution()
    print(solution)
    print(sorted(solution.items()) in result)

test_least_conflicts_solver()