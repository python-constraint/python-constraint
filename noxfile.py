"""Configuration file for the Nox test runner.

This instantiates the specified sessions in isolated environments and runs the tests.
These tests are ran on GitHub, and can be executed locally by running `nox`.
Be aware that the general setup of tests is left to pyproject.toml.
"""

import nox
from nox import Session, session
from pathlib import Path

# from nox_poetry import Session, session   # nox_poetry is a better option, but <=1.0.3 has a bug with filename-URLs

python_versions_to_test = [
    "3.9",
    "3.10",
    "3.11",
    "3.12",
    "3.13",
    # "3.14"  # 3.14 has not yet been officially released
]
nox.options.stop_on_first_error = True
nox.options.error_on_missing_interpreters = True

# create the benchmark folder
Path(".benchmarks").mkdir(exist_ok=True)


# Test code quality: linting
@session
def lint(session: Session) -> None:
    """Ensure the code is formatted as expected."""
    session.install("ruff")
    session.run("ruff", "--config=pyproject.toml", "check", ".")


# Test code compatiblity and coverage
@session(python=python_versions_to_test)  # missing versions can be installed with `pyenv install ...`
# do not forget check / set the versions with `pyenv global`, or `pyenv local` in case of virtual environment
def tests(session: Session) -> None:
    """Run the tests for the specified Python versions."""
    # get command line arguments
    if session.posargs:
        os_name = session.posargs[0]
    else:
        os_name = 'local'

    # install the dev-dependencies and build the package
    session.install("poetry")
    session.run("poetry", "install", "--with", "dev,test", external=True)
    # session.poetry.installroot(distribution_format="sdist")

    # run pytest on the package with C-extensions, disable required coverage percentage
    session.run("pytest", "--no-cov", "--benchmark-json", f".benchmarks/benchmark_{os_name}_{session.python}.json")

    # for the last Python version session:
    if session.python == python_versions_to_test[-1]:
        # run pytest again on the package, this time without C-extensions to generate the correct coverage report
        session.run("python", "tests/setup_teardown.py", "--no-enable_extensions")
        session.run("pytest")

        # re-enable C-extensions
        session.run("python", "tests/setup_teardown.py", "--enable_extensions")
