from constraint import Problem, MinConflictsSolver, BacktrackingSolver, OptimizedBacktrackingSolver, MaxProdConstraint, MinProdConstraint, MinSumConstraint


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

def test_optimized_backtracking_solver():
    # setup the solvers
    problem_og = Problem(BacktrackingSolver())
    problem_opt = Problem(OptimizedBacktrackingSolver())
    problems = [problem_og, problem_opt]

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
    solution = problem_og.getSolution()
    solution_tuple = tuple(solution[key] for key in order)
    solutions_list, solutions_dict, size = problem_opt.getSolutionsAsListDict(order=order)

    # validate the solutions
    assert size == len(true_solutions)
    assert solution_tuple in solutions_list
    assert solution_tuple in solutions_dict
    assert all(sol in solutions_list for sol in true_solutions)
