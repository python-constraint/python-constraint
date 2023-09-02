from pathlib import Path


def test_if_compiled():
    """Test whether C-extensions are succesfully ran, if enabled."""
    from constraint import check_if_compiled

    # check if the .so files are commented
    dir = Path("./constraint")
    assert dir.exists()
    files = list(dir.glob("_*.so"))

    # check if the code uses C-extensions
    if len(files) > 0:
        assert check_if_compiled() is False
    else:
        assert check_if_compiled()
