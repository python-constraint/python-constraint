"""String division must keep the same semantics as a function constraint."""

from itertools import product

import pytest

from constraint import (
    BacktrackingSolver,
    CompilableFunctionConstraint,
    FunctionConstraint,
    OptimizedBacktrackingSolver,
    Problem,
    RecursiveBacktrackingSolver,
    compile_to_constraints,
)


@pytest.mark.parametrize("comparator", ["==", "<=", ">=", "<", ">"])
@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("solver_type", [BacktrackingSolver, OptimizedBacktrackingSolver, RecursiveBacktrackingSolver])
@pytest.mark.parametrize("forwardcheck", [False, True])
@pytest.mark.parametrize("values", [([-2, -1, 0, 1, 2], [-2, -1, 1, 2]), ([1.0, 2.0], [3.0, 49.0])])
def test_division_solution_sets(comparator, reverse, solver_type, forwardcheck, values):
    numerators, denominators = values
    quotients = [-2, -1, 0, 1, 2] + [x / y for x, y in product(numerators, denominators)]
    # Remove duplicate domain values without changing their order.
    quotients = list(dict.fromkeys(quotients))
    expression = f"z {comparator} x / y" if reverse else f"x / y {comparator} z"
    domains = {"x": numerators, "y": denominators, "z": quotients}
    expected = {
        (x, y, z)
        for x, y, z in product(numerators, denominators, quotients)
        if eval(expression, {}, {"x": x, "y": y, "z": z})
    }

    def make_problem(restriction):
        problem = Problem(solver_type(forwardcheck=forwardcheck))
        for name, domain in domains.items():
            problem.addVariable(name, domain)
        problem.addConstraint(restriction, ["x", "y", "z"])
        return problem

    def as_tuple(solution):
        return tuple(solution[name] for name in ("x", "y", "z"))

    function = lambda x, y, z: eval(expression, {}, {"x": x, "y": y, "z": z})
    assert {as_tuple(s) for s in make_problem(function).getSolutions()} == expected
    assert {as_tuple(s) for s in make_problem(expression).getSolutions()} == expected
    assert {as_tuple(s) for s in make_problem(expression).getSolutionIter()} == expected
    solution = make_problem(expression).getSolution()
    assert solution is not None
    assert as_tuple(solution) in expected


@pytest.mark.parametrize("expression", ["x / y == z", "x / y <= z", "x / y >= z", "z == x / y"])
def test_division_by_zero_matches_function_constraint(expression):
    def make_problem(restriction):
        problem = Problem()
        problem.addVariable("x", [0])
        problem.addVariable("y", [0])
        problem.addVariable("z", [0])
        problem.addConstraint(restriction, ["x", "y", "z"])
        return problem

    function = lambda x, y, z: eval(expression, {}, {"x": x, "y": y, "z": z})
    with pytest.raises(ZeroDivisionError):
        make_problem(function).getSolutions()
    with pytest.raises(ZeroDivisionError):
        make_problem(expression).getSolutions()


@pytest.mark.parametrize("picklable", [False, True])
def test_compiled_division_retains_source(picklable):
    expression = "x / y / z == target"
    domains = {"x": [1], "y": [3], "z": [7], "target": [1 / 3 / 7]}
    compiled, variables, source = compile_to_constraints([expression], domains, picklable=picklable)[0]
    expected_type = CompilableFunctionConstraint if picklable else FunctionConstraint
    assert isinstance(compiled, expected_type)
    assert set(variables) == set(domains)
    assert expression in source
