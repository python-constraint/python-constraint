"""General setup and teardown for the tests, and module-level tests."""
from pathlib import Path
import argparse


def unuse_extensions():
    """Make sure C-extensions are not used by adding an underscore to .so files."""
    dir = Path("./constraint")
    assert dir.exists()
    files = dir.glob("*.so")
    for file in files:
        if file.name[0] != "_":
            # add a leading underscore
            file.rename(f"{dir}/_{file.name}")


def use_extensions():
    """Make sure C-extensions are used by removing the underscore to .so files."""
    dir = Path("./constraint")
    assert dir.exists()
    files = dir.glob("_*.so")
    for file in files:
        if file.name[0] == "_":
            # remove the leading underscore
            file.rename(f"{dir}/{file.name[1:]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--enable_extensions", action="store_true")
    parser.add_argument("--no-enable_extensions", dest="enable_extensions", action="store_false")
    parser.set_defaults(enable_extensions=True)
    args = parser.parse_args()
    enable_extensions = args.enable_extensions
    if enable_extensions is True:
        use_extensions()
    elif enable_extensions is False:
        unuse_extensions()
    else:
        raise ValueError(f"Invalid value for {enable_extensions=}")
