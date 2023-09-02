|License| |Build Status| |Docs| |Python Versions| |Downloads| |Status| |Code Coverage|

.. image:: docs/assets/logo/N-Queens_problem_Python.svg
    :align: center
    :width: 50%

python-constraint
=================

| This software is now back to active development / maintainance status.
| For an overview of recent changes, visit the `Changelog <https://github.com/python-constraint/python-constraint/blob/main/CHANGELOG.md>`_.
| The complete documentation can be found `here <http://python-constraint.github.io/python-constraint/>`_.

.. contents::
    :local:
    :depth: 1

Introduction
------------
The :code:`python-constraint` module offers efficient solvers for `Constraint Satisfaction Problems (CSPs) <https://en.wikipedia.org/wiki/Constraint_satisfaction_problem>`_ over finite domains in an accessible Python package.
CSP is class of problems which may be represented in terms of variables (a, b, ...), domains (a in [1, 2, 3], ...), and constraints (a < b, ...).

Examples
--------

Basics
~~~~~~

This interactive Python session demonstrates basic operations:

.. code-block:: python

    >>> from constraint import *
    >>> problem = Problem()
    >>> problem.addVariable("a", [1,2,3])
    >>> problem.addVariable("b", [4,5,6])
    >>> problem.getSolutions()
    [{'a': 3, 'b': 6}, {'a': 3, 'b': 5}, {'a': 3, 'b': 4},
     {'a': 2, 'b': 6}, {'a': 2, 'b': 5}, {'a': 2, 'b': 4},
     {'a': 1, 'b': 6}, {'a': 1, 'b': 5}, {'a': 1, 'b': 4}]

    >>> problem.addConstraint(lambda a, b: a*2 == b,
                              ("a", "b"))
    >>> problem.getSolutions()
    [{'a': 3, 'b': 6}, {'a': 2, 'b': 4}]

    >>> problem = Problem()
    >>> problem.addVariables(["a", "b"], [1, 2, 3])
    >>> problem.addConstraint(AllDifferentConstraint())
    >>> problem.getSolutions()
    [{'a': 3, 'b': 2}, {'a': 3, 'b': 1}, {'a': 2, 'b': 3},
     {'a': 2, 'b': 1}, {'a': 1, 'b': 2}, {'a': 1, 'b': 3}]

Rooks problem
~~~~~~~~~~~~~

The following example solves the classical Eight Rooks problem:

.. code-block:: python

    >>> problem = Problem()
    >>> numpieces = 8
    >>> cols = range(numpieces)
    >>> rows = range(numpieces)
    >>> problem.addVariables(cols, rows)
    >>> for col1 in cols:
    ...     for col2 in cols:
    ...         if col1 < col2:
    ...             problem.addConstraint(lambda row1, row2: row1 != row2,
    ...                                   (col1, col2))
    >>> solutions = problem.getSolutions()
    >>> solutions
    >>> solutions
    [{0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1, 7: 0},
     {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 0, 7: 1},
     {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 1, 6: 2, 7: 0},
     {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 1, 6: 0, 7: 2},
     ...
     {0: 7, 1: 5, 2: 3, 3: 6, 4: 2, 5: 1, 6: 4, 7: 0},
     {0: 7, 1: 5, 2: 3, 3: 6, 4: 1, 5: 2, 6: 0, 7: 4},
     {0: 7, 1: 5, 2: 3, 3: 6, 4: 1, 5: 2, 6: 4, 7: 0},
     {0: 7, 1: 5, 2: 3, 3: 6, 4: 1, 5: 4, 6: 2, 7: 0},
     {0: 7, 1: 5, 2: 3, 3: 6, 4: 1, 5: 4, 6: 0, 7: 2},
     ...]


Magic squares
~~~~~~~~~~~~~

This example solves a 4x4 magic square:

.. code-block:: python

    >>> problem = Problem()
    >>> problem.addVariables(range(0, 16), range(1, 16 + 1))
    >>> problem.addConstraint(AllDifferentConstraint(), range(0, 16))
    >>> problem.addConstraint(ExactSumConstraint(34), [0, 5, 10, 15])
    >>> problem.addConstraint(ExactSumConstraint(34), [3, 6, 9, 12])
    >>> for row in range(4):
    ...     problem.addConstraint(ExactSumConstraint(34),
                                  [row * 4 + i for i in range(4)])
    >>> for col in range(4):
    ...     problem.addConstraint(ExactSumConstraint(34),
                                  [col + 4 * i for i in range(4)])
    >>> solutions = problem.getSolutions()

Features
--------

The following solvers are available:

- Backtracking solver
- Optimized backtracking solver
- Recursive backtracking solver
- Minimum conflicts solver

.. role:: python(code)
   :language: python

Predefined constraint types currently available:

- :python:`FunctionConstraint`
- :python:`AllDifferentConstraint`
- :python:`AllEqualConstraint`
- :python:`MaxSumConstraint`
- :python:`ExactSumConstraint`
- :python:`MinSumConstraint`
- :python:`MaxProdConstraint`
- :python:`MinProdConstraint`
- :python:`InSetConstraint`
- :python:`NotInSetConstraint`
- :python:`SomeInSetConstraint`
- :python:`SomeNotInSetConstraint`

API documentation
-----------------
Documentation for the module is available at: http://python-constraint.github.io/python-constraint/.
It can be built locally by running :code:`make clean html` from the `docs` folder.
For viewing RST files locally, `restview <https://pypi.org/project/restview/>`_ is recommended.

Download and install
--------------------

.. code-block:: shell

    $ pip install python-constraint

Testing
-------

Run :code:`nox` (tests for all supported Python versions in own virtual environment).

To test against your local Python version: make sure you have the development dependencies installed.
Run :code:`pytest` (optionally add :code:`--no-cov` if you have the C-extensions enabled).

Contributing
------------

Feel free to contribute by `submitting pull requests <https://github.com/python-constraint/python-constraint/pulls>`_ or `opening issues <https://github.com/python-constraint/python-constraint/issues>`_.
Please refer to the `contribution guidelines <https://github.com/python-constraint/python-constraint/contribute>`_ before doing so.

Roadmap
-------

This GitHub organization and repository is a global effort to help to maintain :code:`python-constraint`, which was written by Gustavo Niemeyer and originaly located at https://labix.org/python-constraint.
For an overview of recent changes, visit the `Changelog <https://github.com/python-constraint/python-constraint/blob/main/CHANGELOG.md>`_.

Planned development:

- Add a string parser for constraints
- Add parallel-capable solver
- Versioned documentation

Contact
-------
- `Gustavo Niemeyer <https://github.com/niemeyer/>`_ <gustavo@niemeyer.net>
- `Sébastien Celles <https://github.com/scls19fr/>`_ <s.celles@gmail.com>
- `Floris-Jan Willemsen <https://github.com/fjwillemsen>`_

But it's probably better to `open an issue <https://github.com/python-constraint/python-constraint/issues>`_.

.. |License| image:: https://img.shields.io/pypi/l/python-constraint
    :alt: PyPI - License

.. |Build Status| image:: https://github.com/python-constraint/python-constraint/actions/workflows/build-test-python-package.yml/badge.svg
   :target: https://github.com/python-constraint/python-constraint/actions/workflows/build-test-python-package.yml
   :alt: Build Status

.. |Docs| image:: https://img.shields.io/github/actions/workflow/status/python-constraint/python-constraint/publish-documentation.yml?label=Docs
   :target: http://python-constraint.github.io/python-constraint/
   :alt: Documentation Status

.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/python-constraint
    :alt: PyPI - Python Versions

.. |Downloads| image:: https://img.shields.io/pypi/dm/python-constraint
    :alt: PyPI - Downloads

.. |Status| image:: https://img.shields.io/pypi/status/python-constraint
    :alt: PyPI - Status

.. |Code Coverage| image:: https://coveralls.io/repos/github/python-constraint/python-constraint/badge.svg
   :target: https://coveralls.io/github/python-constraint/python-constraint
   :alt: Code Coverage

.. |Code Health| image:: https://landscape.io/github/python-constraint/python-constraint/master/landscape.svg?style=flat
   :target: https://landscape.io/github/python-constraint/python-constraint/master
   :alt: Code Health
