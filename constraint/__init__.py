"""File for obtaining top-level imports from submodules.

For example: constraint.all.Problem can be imported as `from constraint import Problem`.
Please be aware that all.py dictates what is exportable via the `__all__` variable.
"""

from .all import *  # noqa: F403
