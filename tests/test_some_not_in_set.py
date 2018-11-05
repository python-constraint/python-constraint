from constraint import Domain, Variable, SomeNotInSetConstraint


def test_empty_constraint():
    constrainer = SomeNotInSetConstraint(set())
    v1, v2 = variables = [Variable("v1"), Variable("v2")]
    assignments = {v1: "a", v2: "b"}

    assert constrainer(variables, {}, assignments)


def test_no_overlap():
    constrainer = SomeNotInSetConstraint(set("zy"))
    v1, v2 = variables = [Variable("v1"), Variable("v2")]
    assignments = {v1: "a", v2: "b"}

    assert constrainer(variables, {}, assignments)


def test_some_overlap():
    constrainer = SomeNotInSetConstraint(set("b"))
    v1, v2 = variables = [Variable("v1"), Variable("v2")]
    assignments = {v1: "a", v2: "b"}

    assert constrainer(variables, {}, assignments)


def test_too_much_overlap():
    constrainer = SomeNotInSetConstraint(set("ab"))
    v1, v2 = variables = [Variable("v1"), Variable("v2")]
    assignments = {v1: "a", v2: "b"}

    assert not constrainer(variables, {}, assignments)


def test_exact():
    constrainer = SomeNotInSetConstraint(set("abc"), n=2, exact=True)
    v1, v2, v3 = variables = [Variable("v1"), Variable("v2"), Variable("v3")]

    assignments = {v1: "a", v2: "y", v3: "z"}
    assert constrainer(variables, {}, assignments)

    assignments = {v1: "a", v2: "y"}
    assert constrainer(variables, {}, assignments)

    assignments = {v1: "a", v2: "b", v3: "z"}
    assert not constrainer(variables, {}, assignments)

    assignments = {v1: "a", v2: "b"}
    assert not constrainer(variables, {}, assignments)

    assignments = {v1: "a", v2: "b", v3: "c"}
    assert not constrainer(variables, {}, assignments)

    assignments = {v1: "x", v2: "y", v3: "z"}
    assert not constrainer(variables, {}, assignments)


def test_forwardcheck():
    constrainer = SomeNotInSetConstraint(set("abc"), n=2)
    v1, v2, v3 = variables = [Variable("v1"), Variable("v2"), Variable("v3")]

    domains = {v1: Domain(["a"]), v2: Domain(["b", "y"]), v3: Domain(["c", "z"])}
    assert constrainer(variables, domains, {v1: "a"})
    assert ["a"] == list(domains[v1])
    assert ["b", "y"] == list(domains[v2])
    assert ["c", "z"] == list(domains[v3])

    assert constrainer(variables, domains, {v1: "a"}, True)
    assert ["a"] == list(domains[v1])
    assert ["y"] == list(domains[v2])
    assert ["z"] == list(domains[v3])


def test_forwardcheck_empty_domain():
    constrainer = SomeNotInSetConstraint(set("abc"))
    v1, v2 = variables = [Variable("v1"), Variable("v2")]

    domains = {v1: Domain(["a"]), v2: Domain(["b"])}
    assert constrainer(variables, domains, {v1: "a"})
    assert not constrainer(variables, domains, {v1: "a"}, True)


def test_forwardcheck_exact():
    constrainer = SomeNotInSetConstraint(set("abc"), n=2, exact=True)
    v1, v2, v3 = variables = [Variable("v1"), Variable("v2"), Variable("v3")]
    assignments = {v1: "a"}

    domains = {v1: Domain(["a", "x"]), v2: Domain(["b", "y"]), v3: Domain(["c", "z"])}
    assert constrainer(variables, domains, assignments)
    assert constrainer(variables, domains, assignments, True)
    assert "b" not in domains[v2]
    assert "y" in domains[v2]
    assert "c" not in domains[v3]
    assert "z" in domains[v3]

    domains = {v1: Domain(["a", "x"]), v2: Domain(["b", "y"]), v3: Domain(["c"])}
    assert constrainer(variables, domains, assignments)
    assert not constrainer(variables, domains, assignments, True)
