"""Configuration file for the Nox test runner.

This instantiates the specified sessions in isolated environments and runs the tests.
This allows for locally mirroring the testing occuring with GitHub-actions.
Be careful that the general setup of tests is left to pyproject.toml.
"""


import nox
from nox import Session, session

# from nox_poetry import Session, session

nox.options.stop_on_first_error = True
nox.options.error_on_missing_interpreters = True


# # Test code quality: linting
# @session
# def lint(session: Session) -> None:
#     """Ensure the code is formatted as expected."""
#     session.install("ruff")
#     session.run("ruff", "--format=github", "--config=pyproject.toml", ".")


# Test code compatiblity and coverage
@session(python=["3.9", "3.10", "3.11"])  # missing versions can be installed with `pyenv install ...`
# do not forget check / set the versions with `pyenv global`, or `pyenv local` in case of virtual environment
def tests(session: Session) -> None:
    """Run the tests for the specified Python versions."""
    # session.install(".[test]")
    # session.install("pytest", ".")
    # session.poetry.installroot(distribution_format="sdist")
    session.run("pytest")
