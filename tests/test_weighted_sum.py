"""Compare weighted sum constraints with exhaustive enumeration."""

import operator
from itertools import product

import pytest

from constraint import (
    BacktrackingSolver,
    ExactSumConstraint,
    MaxSumConstraint,
    MinSumConstraint,
    OptimizedBacktrackingSolver,
    Problem,
)


@pytest.mark.parametrize(
    "constraint_type, predicate",
    [(ExactSumConstraint, operator.eq), (MinSumConstraint, operator.ge), (MaxSumConstraint, operator.le)],
)
@pytest.mark.parametrize("multipliers", [(-1, 1), (-1, -2), (-0.5, 1), (0, -1), (1, 2)])
@pytest.mark.parametrize("bound", [-2, 0, 2])
@pytest.mark.parametrize("solver_type", [BacktrackingSolver, OptimizedBacktrackingSolver])
@pytest.mark.parametrize("forwardcheck", [False, True])
def test_weighted_sum_matches_exhaustive_search(constraint_type, predicate, multipliers, bound, solver_type, forwardcheck):
    values = [-2, 0, 1, 2]
    problem = Problem(solver_type(forwardcheck=forwardcheck))
    problem.addVariables(["x", "y"], values)
    problem.addConstraint(constraint_type(bound, multipliers), ["x", "y"])

    expected = {
        (x, y) for x, y in product(values, repeat=2) if predicate(x * multipliers[0] + y * multipliers[1], bound)
    }
    actual = {(solution["x"], solution["y"]) for solution in problem.getSolutions()}
    assert actual == expected
