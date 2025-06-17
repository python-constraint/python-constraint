from constraint import (
    compile_to_constraints, 
    parse_restrictions, 
    Constraint, 
    FunctionConstraint, 
    CompilableFunctionConstraint, 
    ExactSumConstraint, 
    MinSumConstraint,
    MaxSumConstraint,
    ExactProdConstraint, 
    MinProdConstraint, 
    MaxProdConstraint, 
    VariableExactSumConstraint, 
    VariableExactProdConstraint, 
    VariableMinProdConstraint, 
    VariableMaxProdConstraint, 
)
from collections.abc import Iterable

def test_parse_restrictions():
    domains = {"x": [50, 100], "y": [0, 1]}
    constraints = ["x != 320", "y == 0 or x % 32 != 0", "50 <= x * y < 100"]

    # test the conversion to constraints
    parsed_multi_constraints = parse_restrictions(constraints, domains)
    assert isinstance(parsed_multi_constraints, list) and isinstance(parsed_multi_constraints[0], tuple)
    assert len(parsed_multi_constraints) == 4
    parsed, params = parsed_multi_constraints[0]
    assert isinstance(parsed, str)
    assert params == ["x"]
    parsed, params = parsed_multi_constraints[1]
    assert isinstance(parsed, str)
    assert all(param in domains for param in params)
    parsed, params = parsed_multi_constraints[2]
    assert isinstance(parsed, MinProdConstraint)
    assert all(param in domains for param in params)
    parsed, params = parsed_multi_constraints[3]
    assert isinstance(parsed, MaxProdConstraint)
    assert all(param in domains for param in params)

    # test the conversion to constraints with a real-world edge-case
    rw_domains = dict()
    rw_domains["x"] = [1, 2, 3, 4, 5, 6, 7, 8]
    rw_domains["y"] = [1, 2, 3, 4, 5, 6, 7, 8]
    parsed_constraint, params_constraint = parse_restrictions(["x*y<30"], rw_domains)[0]
    assert all(param in rw_domains for param in params_constraint)
    assert isinstance(parsed_constraint, MaxProdConstraint)
    assert 29 < parsed_constraint._maxprod < 30
    parsed_constraint, params_constraint = parse_restrictions(["30<x*y"], rw_domains)[0]
    assert all(param in rw_domains for param in params_constraint)
    assert isinstance(parsed_constraint, MinProdConstraint)
    assert 30 < parsed_constraint._minprod < 31

def test_compile_to_constraints():
    domains = {"x": [50, 100], "y": [0, 1]}
    constraints = [
        "x != 320",             # FunctionConstraint
        "y == 0 or x % 32 != 0",# FunctionConstraint
        "x == 100",             # ExactSumConstraint
        "100 == x + y",         # ExactSumConstraint  # TODO why is this parsed to a FunctionConstraint?
        "x == 100+y",           # VariableExactSumConstraint
        "x == x+y",             # VariableExactSumConstraint
        "51 <= x+y",            # MinSumConstraint
        "50 < x+y",             # MinSumConstraint
        "100-y >= x",           # MaxSumConstraint
        "100 == x-y",           # VariableExactSumConstraint
        "x / y == 100",         # VariableExactProdConstraint
        "x / y == x",           # VariableExactProdConstraint
        "x / y <= x",           # VariableMinProdConstraint
        "x / y >= x",           # VariableMaxProdConstraint
        "50 <= x * y < 100",    # becomes splitted MinProdConstraint and MaxProdConstraint
    ]
    expected_constraint_types = [
        FunctionConstraint, 
        FunctionConstraint, 
        ExactSumConstraint,
        ExactSumConstraint,
        VariableExactSumConstraint,
        VariableExactSumConstraint,
        MinSumConstraint,
        MinSumConstraint,
        MaxSumConstraint,               # with rewriting "100-y >= x" becomes "100 >= x+y"
        VariableExactSumConstraint,     # with rewriting "100 == x-y" becomes "100+y == x"
        VariableExactProdConstraint,    # with rewriting "x / y == 100" becomes "x==100 * y"
        VariableExactProdConstraint,
        VariableMinProdConstraint,
        VariableMaxProdConstraint,
        MinProdConstraint, 
        MaxProdConstraint,
    ]

    compiled = compile_to_constraints(constraints, domains, picklable=False)
    # assert len(compiled) == len(expected_constraint_types)
    for r, vals, r_str in compiled:
        assert isinstance(r, Constraint)
        assert isinstance(vals, Iterable) and all(isinstance(v, str) for v in vals)
        if isinstance(r, (FunctionConstraint, CompilableFunctionConstraint)):
            assert isinstance(r_str, str)
        else:
            assert r_str is None

    # check whether the expected types match (may have to be adjusted to be order independent in future)
    for i, (r, _, cons) in enumerate(compiled):
        expected = expected_constraint_types[i]
        assert isinstance(r, expected), f"Expected {expected} but got {type(r)} for constraint {constraints[i]}"  # the constraint lookup is correct until there are split restrictions
        if callable(expected):
            assert callable(r)

def test_compile_to_constraints_picklable():
    domains = {"x": [50, 100], "y": [0, 1]}
    constraints = [
        "x != 320", 
        "y == 0 or x % 32 != 0", 
        "50 <= x * y < 100"
    ]
    expected_constraint_types = [
        CompilableFunctionConstraint, 
        CompilableFunctionConstraint, 
        MinProdConstraint, 
        MaxProdConstraint
    ]

    compiled = compile_to_constraints(constraints, domains, picklable=True)
    assert len(compiled) == len(expected_constraint_types)
    for r, vals, r_str in compiled:
        assert isinstance(r, Constraint)
        assert isinstance(vals, Iterable) and all(isinstance(v, str) for v in vals)
        if isinstance(r, (FunctionConstraint, CompilableFunctionConstraint)):
            assert isinstance(r_str, str)
        else:
            assert r_str is None

    # check whether the expected types match (may have to be adjusted to be order independent in future)
    for i, (r, _, _) in enumerate(compiled):
        expected = expected_constraint_types[i]
        if callable(expected):
            assert callable(r)
        else:
            assert isinstance(r, expected)
