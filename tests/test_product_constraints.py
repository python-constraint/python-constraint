"""Regression coverage for fixed-bound product pruning."""

from itertools import product
from math import prod

import pytest

from constraint import (
    BacktrackingSolver,
    Domain,
    ExactProdConstraint,
    MaxProdConstraint,
    MinProdConstraint,
    OptimizedBacktrackingSolver,
    Problem,
    RecursiveBacktrackingSolver,
    VariableExactProdConstraint,
)


CASES = [
    ([[-2, -1], [1, 2]], -2),
    ([[-1], [2]], -2),
    ([[-2, -1], [1, 2], [1, 2]], -4),
    ([[-2, -1, 0], [1, 2]], 0),
    ([[-2, 0, 2], [-1, 1], [0, 2]], -4),
    ([[0.5, 1, 2], [1, 2], [2, 3]], 3),
    ([[-0.5, 0, 0.5], [1, 2], [1, 2]], -1),
    ([[0, 1], [1, 2], [2, 3]], 0),
    ([[1, 2, 3], [1, 2]], 2),
    ([[1, 2], [1, 2]], -2),
]


@pytest.mark.parametrize('values,target', CASES)
@pytest.mark.parametrize('constraint_type', [ExactProdConstraint, MaxProdConstraint])
@pytest.mark.parametrize('solver_type', [BacktrackingSolver, OptimizedBacktrackingSolver, RecursiveBacktrackingSolver])
@pytest.mark.parametrize('forwardcheck', [False, True])
@pytest.mark.parametrize('reverse', [False, True])
@pytest.mark.parametrize('reverse_constraint', [False, True])
def test_product_solutions(values, target, constraint_type, solver_type, forwardcheck, reverse, reverse_constraint):
    expected = {
        assignment
        for assignment in product(*values)
        if (prod(assignment) == target if constraint_type is ExactProdConstraint else prod(assignment) <= target)
    }
    variables = list(range(len(values)))
    ordered = variables[::-1] if reverse else variables

    def make_problem():
        problem = Problem(solver_type(forwardcheck=forwardcheck))
        for variable in ordered:
            problem.addVariable(variable, values[variable])
        problem.addConstraint(constraint_type(target), variables[::-1] if reverse_constraint else variables)
        return problem

    def as_tuple(solution):
        return tuple(solution[variable] for variable in variables)

    assert {as_tuple(solution) for solution in make_problem().getSolutions()} == expected
    assert {as_tuple(solution) for solution in make_problem().getSolutionIter()} == expected
    solution = make_problem().getSolution()
    if expected:
        assert solution is not None
        assert as_tuple(solution) in expected
    else:
        assert solution is None


@pytest.mark.parametrize('constraint_type', [ExactProdConstraint, MaxProdConstraint])
@pytest.mark.parametrize('forwardcheck', [False, True])
def test_negative_partial_product(constraint_type, forwardcheck):
    domains = {'adjustment': Domain([-1]), 'quantity': Domain([2])}
    constraint = constraint_type(-2)
    assert constraint(list(domains), domains, {'adjustment': -1}, forwardcheck)
    assert domains['quantity'] == [2]
    assert constraint(list(domains), domains, {'adjustment': -1, 'quantity': 2}, forwardcheck)


@pytest.mark.parametrize('constraint_type', [ExactProdConstraint, MaxProdConstraint])
@pytest.mark.parametrize('remaining', [0, 0.5])
def test_forward_check_keeps_values_reduced_by_another_factor(constraint_type, remaining):
    domains = {'a': Domain([2]), 'b': Domain([3]), 'c': Domain([remaining])}
    target = 6 * remaining
    assert constraint_type(target)(list(domains), domains, {'a': 2}, True)
    assert domains['b'] == [3]
    assert domains['c'] == [remaining]


@pytest.mark.parametrize('constraint_type', [ExactProdConstraint, MaxProdConstraint])
def test_positive_product_pruning(constraint_type):
    variables = ['a', 'b']
    domains = {variable: Domain([1, 2, 3]) for variable in variables}
    constraint = constraint_type(2)
    constraint.preProcess(variables, domains, [], {})
    assert domains == {'a': [1, 2], 'b': [1, 2]}
    assert constraint(variables, domains, {'a': 2}, True)
    assert domains['b'] == [1]
    assert not constraint(variables, domains, {'a': 3})


def test_signed_product_sibling_controls():
    problem = Problem()
    problem.addVariable('a', [-2, -1])
    problem.addVariable('b', [1, 2])
    problem.addVariable('target', [-2])
    problem.addConstraint(VariableExactProdConstraint('target', ['a', 'b']))
    assert {(solution['a'], solution['b']) for solution in problem.getSolutions()} == {(-2, 1), (-1, 2)}
    problem = Problem()
    problem.addVariable('a', [-2, -1])
    problem.addVariable('b', [1, 2])
    problem.addConstraint(MinProdConstraint(-2))
    assert {(solution['a'], solution['b']) for solution in problem.getSolutions()} == {(-2, 1), (-1, 1), (-1, 2)}
