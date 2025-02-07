from constraint import compile_restrictions, parse_restrictions, MinProdConstraint, MaxProdConstraint

def test_parse_restrictions():
    tune_params = {"x": [50, 100], "y": [0, 1]}
    restrict = ["x != 320"]
    restrictions = ["x != 320", "y == 0 or x % 32 != 0", "50 <= x * y < 100"]

    # test the monolithic parsed function
    parsed = parse_restrictions(restrict, tune_params, monolithic=True)[0]
    expected = "params[params_index['x']] != 320"
    assert expected in parsed[0]

    # test the split parsed function
    parsed_multi = parse_restrictions(restrictions, tune_params, try_to_constraint=False)
    assert isinstance(parsed_multi, list) and isinstance(parsed_multi[0], tuple)
    assert len(parsed_multi) == 3
    parsed, params = parsed_multi[0]
    assert restrictions[0] in parsed
    assert params == ["x"]
    parsed, params = parsed_multi[1]
    assert restrictions[1] in parsed
    assert all(param in tune_params for param in params)
    parsed, params = parsed_multi[2]
    assert restrictions[2] in parsed
    assert all(param in tune_params for param in params)

    # test the conversion to constraints
    parsed_multi_constraints = parse_restrictions(restrictions, tune_params, try_to_constraint=True)
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
    parsed_constraint, params_constraint = parse_restrictions(["x*y<30"], rw_tune_params, try_to_constraint=True)[0]
    assert all(param in rw_tune_params for param in params_constraint)
    assert isinstance(parsed_constraint, MaxProdConstraint)
    assert parsed_constraint._maxprod == 29
    parsed_constraint, params_constraint = parse_restrictions(["30<x*y"], rw_tune_params, try_to_constraint=True)[0]
    assert all(param in rw_tune_params for param in params_constraint)
    assert isinstance(parsed_constraint, MinProdConstraint)
    assert parsed_constraint._minprod == 31
