
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

- :any:`FunctionConstraint`
- :any:`AllDifferentConstraint`
- :any:`AllEqualConstraint`
- :any:`ExactSumConstraint`
- :any:`MaxSumConstraint`
- :any:`MinSumConstraint`
- :any:`InSetConstraint`
- :any:`NotInSetConstraint`
- :any:`SomeInSetConstraint`
- :any:`SomeNotInSetConstraint`

 
Download and install
--------------------

.. code-block:: shell

    $ pip install python-constraint
