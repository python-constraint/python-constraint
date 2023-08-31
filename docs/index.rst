:tocdepth: 2

python-constraint
=================

| The `python-constraint` module offers efficient solvers for Constraint Satisfaction Problems (CSPs) over finite domains in an accessible package.
| All it takes is a few lines of code:

>>> from constraint import *
>>> problem = Problem()
>>> problem.addVariable("a", [1,2])
>>> problem.addVariable("b", [3,4])
>>> problem.getSolutions()
[{'a': 2, 'b': 4}, {'a': 2, 'b': 3}, {'a': 1, 'b': 4}, {'a': 1, 'b': 3}]
>>> problem.addConstraint(lambda a, b: a*2 == b, ("a", "b"))
>>> problem.getSolutions()
[{'a': 2, 'b': 4}]

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   intro
   reference


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
