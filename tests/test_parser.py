from constraint import compile_to_constraints, parse_restrictions, Constraint, FunctionConstraint, CompilableFunctionConstraint, MinProdConstraint, MaxProdConstraint
from collections.abc import Iterable

def test_parse_restrictions():
    tune_params = {"x": [50, 100], "y": [0, 1]}
    restrictions = ["x != 320", "y == 0 or x % 32 != 0", "50 <= x * y < 100"]

    # test the conversion to constraints
    parsed_multi_constraints = parse_restrictions(restrictions, tune_params)
    assert isinstance(parsed_multi_constraints, list) and isinstance(parsed_multi_constraints[0], tuple)
    assert len(parsed_multi_constraints) == 4
    parsed, params = parsed_multi_constraints[0]
    assert isinstance(parsed, str)
    assert params == ["x"]
    parsed, params = parsed_multi_constraints[1]
    assert isinstance(parsed, str)
    assert all(param in tune_params for param in params)
    parsed, params = parsed_multi_constraints[2]
    assert isinstance(parsed, MinProdConstraint)
    assert all(param in tune_params for param in params)
    parsed, params = parsed_multi_constraints[3]
    assert isinstance(parsed, MaxProdConstraint)
    assert all(param in tune_params for param in params)

    # test the conversion to constraints with a real-world edge-case
    rw_tune_params = dict()
    rw_tune_params["x"] = [1, 2, 3, 4, 5, 6, 7, 8]
    rw_tune_params["y"] = [1, 2, 3, 4, 5, 6, 7, 8]
    parsed_constraint, params_constraint = parse_restrictions(["x*y<30"], rw_tune_params)[0]
    assert all(param in rw_tune_params for param in params_constraint)
    assert isinstance(parsed_constraint, MaxProdConstraint)
    assert parsed_constraint._maxprod == 29
    parsed_constraint, params_constraint = parse_restrictions(["30<x*y"], rw_tune_params)[0]
    assert all(param in rw_tune_params for param in params_constraint)
    assert isinstance(parsed_constraint, MinProdConstraint)
    assert parsed_constraint._minprod == 31

def test_compile_to_constraints():
    tune_params = {"x": [50, 100], "y": [0, 1]}
    restrictions = ["x != 320", "y == 0 or x % 32 != 0", "50 <= x * y < 100"]
    expected_constraint_types = [FunctionConstraint, FunctionConstraint, MinProdConstraint, MaxProdConstraint]

    compiled = compile_to_constraints(restrictions, tune_params, picklable=False)
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

def test_compile_to_constraints_picklable():
    tune_params = {"x": [50, 100], "y": [0, 1]}
    restrictions = ["x != 320", "y == 0 or x % 32 != 0", "50 <= x * y < 100"]
    expected_constraint_types = [
        CompilableFunctionConstraint, 
        CompilableFunctionConstraint, 
        MinProdConstraint, 
        MaxProdConstraint
    ]

    compiled = compile_to_constraints(restrictions, tune_params, picklable=True)
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
