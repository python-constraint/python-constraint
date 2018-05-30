|Build Status| |Code Health| |Code Coverage|

python-constraint
=================

Introduction
------------
The Python constraint module offers solvers for `Constraint Satisfaction Problems (CSPs) <https://en.wikipedia.org/wiki/Constraint_satisfaction_problem>`_ over finite domains in simple and pure Python. CSP is class of problems which may be represented in terms of variables (a, b, ...), domains (a in [1, 2, 3], ...), and constraints (a < b, ...).

Examples
--------

Basics
~~~~~~

This interactive Python session demonstrates the module basic operation:

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
- Recursive backtracking solver
- Minimum conflicts solver


.. role:: python(code)
   :language: python

Predefined constraint types currently available:

- :python:`FunctionConstraint`
- :python:`AllDifferentConstraint`
- :python:`AllEqualConstraint`
- :python:`ExactSumConstraint`
- :python:`MaxSumConstraint`
- :python:`MinSumConstraint`
- :python:`InSetConstraint`
- :python:`NotInSetConstraint`
- :python:`SomeInSetConstraint`
- :python:`SomeNotInSetConstraint`

API documentation
-----------------
Documentation for the module is available at: http://labix.org/doc/constraint/

Download and install
--------------------

.. code-block:: shell

    $ pip install python-constraint

Roadmap
-------

This GitHub organization and repository is a global effort to help to
maintain python-constraint which was written by Gustavo Niemeyer
and originaly located at https://labix.org/python-constraint

- Create some unit tests - DONE
- Enable continuous integration - DONE
- Port to Python 3 (Python 2 being also supported) - DONE
- Respect Style Guide for Python Code (PEP8) - DONE
- Improve code coverage writting more unit tests - ToDo
- Move doc to Sphinx or MkDocs - https://readthedocs.org/ - ToDo

Contact
-------
- `Gustavo Niemeyer <https://github.com/niemeyer/>`_ <gustavo@niemeyer.net>
- `Sébastien Celles <https://github.com/scls19fr/>`_ <s.celles@gmail.com>

But it's probably better to `open an issue <https://github.com/python-constraint/python-constraint/issues>`_.


.. |Build Status| image:: https://travis-ci.org/python-constraint/python-constraint.svg?branch=master
   :target: https://travis-ci.org/python-constraint/python-constraint
.. |Code Health| image:: https://landscape.io/github/python-constraint/python-constraint/master/landscape.svg?style=flat
   :target: https://landscape.io/github/python-constraint/python-constraint/master
   :alt: Code Health
.. |Code Coverage| image:: https://coveralls.io/repos/github/python-constraint/python-constraint/badge.svg
   :target: https://coveralls.io/github/python-constraint/python-constraint
