from constraint import Problem, MinConflictsSolver, BacktrackingSolver, OptimizedBacktrackingSolver, RecursiveBacktrackingSolver, MaxProdConstraint, MinProdConstraint, MinSumConstraint, FunctionConstraint


def test_min_conflicts_solver():
    problem = Problem(MinConflictsSolver())
    problem.addVariable("x", [0, 1])
    problem.addVariable("y", [0, 1])

    possible_solutions = [
        {"x": 0, "y": 0},
        {"x": 0, "y": 1},
        {"x": 1, "y": 0},
        {"x": 1, "y": 1},
    ]

    # test if all solutions are eventually found by iteration and adding the last solutions as a constraint
    for _ in possible_solutions:
        solution = problem.getSolution()
        assert solution in possible_solutions
        problem.addConstraint(FunctionConstraint(lambda x, y: (lambda x, y, xs, ys: x != xs or y != ys)(x, y, solution['x'], solution['y'])))

def test_optimized_backtracking_solver():
    # setup the solvers
    problem_bt = Problem(BacktrackingSolver())
    problem_opt = Problem(OptimizedBacktrackingSolver())
    problem_opt_nfwd = Problem(OptimizedBacktrackingSolver(forwardcheck=False))
    problems = [problem_bt, problem_opt, problem_opt_nfwd]

    # define the problem for all solvers
    for problem in problems:
        problem.addVariable("x", [-1, 0, 1, 2])
        problem.addVariable("y", [1, 2])
        problem.addConstraint(MaxProdConstraint(2), ["x", "y"])
        problem.addConstraint(MinProdConstraint(1), ["x", "y"])
        problem.addConstraint(MinSumConstraint(0), ["x"])

    # get the solutions
    true_solutions = [(2, 1), (1, 2), (1, 1)]
    order = ["x", "y"]
    solution = problem_bt.getSolution()
    solution_tuple = tuple(solution[key] for key in order)

    # validate a single solution
    solution_opt = problem_opt.getSolution()
    assert tuple(solution_opt[key] for key in order) in true_solutions

    # validate all solutions
    def validate(solutions_list, solutions_dict, size):
        assert size == len(true_solutions)
        assert solution_tuple in solutions_list
        assert solution_tuple in solutions_dict
        assert all(sol in solutions_list for sol in true_solutions)

    validate(*problem_opt.getSolutionsAsListDict(order=order))
    validate(*problem_opt_nfwd.getSolutionsAsListDict(order=order))

def test_recursive_backtracking_solver():
    problem = Problem(RecursiveBacktrackingSolver())
    problem.addVariable("x", [0, 1])
    problem.addVariable("y", [0, 1])
    solution = problem.getSolution()
    solutions = problem.getSolutions()

    possible_solutions = [
        {"x": 0, "y": 0},
        {"x": 0, "y": 1},
        {"x": 1, "y": 0},
        {"x": 1, "y": 1},
    ]

    assert solution in possible_solutions
    assert all(sol in possible_solutions for sol in solutions)
