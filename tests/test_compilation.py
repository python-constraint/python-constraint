"""Tests the compiled C-extensions."""


def test_if_compiled():
    """Test whether C-extensions are succesfully ran."""
    from constraint import check_if_compiled

    is_compiled = check_if_compiled()
    assert is_compiled
