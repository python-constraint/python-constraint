from pathlib import Path


def test_if_compiled():
    """Test whether C-extensions are succesfully ran, if enabled."""
    import constraint

    # check if the .so files are commented
    dir = Path(constraint.__file__).resolve().parent
    assert dir.exists()
    files = list(dir.glob("_*.so"))

    # check if the code uses C-extensions
    if len(files) > 0:
        assert constraint.check_if_compiled() is False
    else:
        assert constraint.check_if_compiled()
