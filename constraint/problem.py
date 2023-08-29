"""Module containing the code for problem definitions."""

import copy

from constraint.solvers import BacktrackingSolver
from constraint.domain import Domain
from constraint.constraints import Constraint, FunctionConstraint
from operator import itemgetter
from typing import List, Optional, Union, Sequence, Tuple, Dict, Callable

class Problem(object):
    """Class used to define a problem and retrieve solutions."""

    def __init__(self, solver=None):
        """Initialization method.

        Args:
            solver (instance of a :py:class:`Solver`): Problem solver to use (default is :py:class:`BacktrackingSolver`)
        """
        self._solver = solver or BacktrackingSolver()
        self._constraints = []
        self._variables = {}

    def reset(self):
        """Reset the current problem definition.

        Example:
            >>> problem = Problem()
            >>> problem.addVariable("a", [1, 2])
            >>> problem.reset()
            >>> problem.getSolution()
            >>>
        """
        del self._constraints[:]
        self._variables.clear()

    def setSolver(self, solver):
        """Change the problem solver currently in use.

        Example:
            >>> solver = BacktrackingSolver()
            >>> problem = Problem(solver)
            >>> problem.getSolver() is solver
            True

        Args:
            solver (instance of a :py:class:`Solver`): New problem
                solver
        """
        self._solver = solver

    def getSolver(self):
        """Obtain the problem solver currently in use.

        Example:
            >>> solver = BacktrackingSolver()
            >>> problem = Problem(solver)
            >>> problem.getSolver() is solver
            True

        Returns:
            instance of a :py:class:`Solver` subclass: Solver currently in use
        """
        return self._solver

    def addVariable(self, variable, domain):
        """Add a variable to the problem.

        Example:
            >>> problem = Problem()
            >>> problem.addVariable("a", [1, 2])
            >>> problem.getSolution() in ({'a': 1}, {'a': 2})
            True

        Args:
            variable (hashable object): Object representing a problem
                variable
            domain (list, tuple, or instance of :py:class:`Domain`): Set of items
                defining the possible values that the given variable may
                assume
        """
        if variable in self._variables:
            msg = "Tried to insert duplicated variable %s" % repr(variable)
            raise ValueError(msg)
        if isinstance(domain, Domain):
            domain = copy.deepcopy(domain)
        elif hasattr(domain, "__getitem__"):
            domain = Domain(domain)
        else:
            msg = "Domains must be instances of subclasses of the Domain class"
            raise TypeError(msg)
        if not domain:
            raise ValueError("Domain is empty")
        self._variables[variable] = domain

    def addVariables(self, variables: Sequence, domain):
        """Add one or more variables to the problem.

        Example:
            >>> problem = Problem()
            >>> problem.addVariables(["a", "b"], [1, 2, 3])
            >>> solutions = problem.getSolutions()
            >>> len(solutions)
            9
            >>> {'a': 3, 'b': 1} in solutions
            True

        Args:
            variables (sequence of hashable objects): Any object
                containing a sequence of objects represeting problem
                variables
            domain (list, tuple, or instance of :py:class:`Domain`): Set of items
                defining the possible values that the given variables
                may assume
        """
        for variable in variables:
            self.addVariable(variable, domain)

    def addConstraint(self, constraint: Union[Constraint, Callable], variables: Optional[Sequence] = None):
        """Add a constraint to the problem.

        Example:
            >>> problem = Problem()
            >>> problem.addVariables(["a", "b"], [1, 2, 3])
            >>> problem.addConstraint(lambda a, b: b == a+1, ["a", "b"])
            >>> solutions = problem.getSolutions()
            >>>

        Args:
            constraint (instance of :py:class:`Constraint` or function to be wrapped by :py:class:`FunctionConstraint`):
                Constraint to be included in the problem
            variables (set or sequence of variables): :py:class:`Variables` affected
                by the constraint (default to all variables). Depending
                on the constraint type the order may be important.
        """
        if not isinstance(constraint, Constraint):
            if callable(constraint):
                constraint = FunctionConstraint(constraint)
            else:
                msg = "Constraints must be instances of subclasses " "of the Constraint class"
                raise ValueError(msg)
        self._constraints.append((constraint, variables))

    def getSolution(self):
        """Find and return a solution to the problem.

        Example:
            >>> problem = Problem()
            >>> problem.getSolution() is None
            True
            >>> problem.addVariables(["a"], [42])
            >>> problem.getSolution()
            {'a': 42}

        Returns:
            dictionary mapping variables to values: Solution for the
            problem
        """
        domains, constraints, vconstraints = self._getArgs()
        if not domains:
            return None
        return self._solver.getSolution(domains, constraints, vconstraints)

    def getSolutions(self):
        """Find and return all solutions to the problem.

        Example:
            >>> problem = Problem()
            >>> problem.getSolutions() == []
            True
            >>> problem.addVariables(["a"], [42])
            >>> problem.getSolutions()
            [{'a': 42}]

        Returns:
            list of dictionaries mapping variables to values: All
            solutions for the problem
        """
        domains, constraints, vconstraints = self._getArgs()
        if not domains:
            return []
        return self._solver.getSolutions(domains, constraints, vconstraints)

    def getSolutionIter(self):
        """Return an iterator to the solutions of the problem.

        Example:
            >>> problem = Problem()
            >>> list(problem.getSolutionIter()) == []
            True
            >>> problem.addVariables(["a"], [42])
            >>> iter = problem.getSolutionIter()
            >>> next(iter)
            {'a': 42}
            >>> next(iter)
            Traceback (most recent call last):
                ...
            StopIteration
        """
        domains, constraints, vconstraints = self._getArgs()
        if not domains:
            return iter(())
        return self._solver.getSolutionIter(domains, constraints, vconstraints)

    def getSolutionsOrderedList(self, order: List[str] = None) -> List[tuple]:
        """Returns the solutions as a list of tuples, with each solution tuple ordered according to `order`."""
        solutions: List[dict] = self.getSolutions()
        if order is None or len(order) == 1:
            return list(tuple(solution.values()) for solution in solutions)
        get_in_order = itemgetter(*order)
        return list(get_in_order(params) for params in solutions)

    def getSolutionsAsListDict(self, order: List[str] = None, validate: bool = True) -> Tuple[List[tuple], Dict[tuple, int], int]:  # noqa: E501
        """Returns the searchspace as a list of tuples, a dict of the searchspace for fast lookups and the size."""
        solutions_list = self.getSolutionsOrderedList(order)
        size_list = len(solutions_list)
        solutions_dict: dict = dict(zip(solutions_list, range(size_list)))
        if validate:
            # check for duplicates
            size_dict = len(solutions_dict)
            if size_list != size_dict:
                raise ValueError(
                    f"{size_list - size_dict} duplicate parameter configurations in searchspace, should not happen."
                )
        return (
            solutions_list,
            solutions_dict,
            size_list,
        )

    def _getArgs(self):
        domains = self._variables.copy()
        allvariables = domains.keys()
        constraints = []
        for constraint, variables in self._constraints:
            if not variables:
                variables = list(allvariables)
            constraints.append((constraint, variables))
        vconstraints = {}
        for variable in domains:
            vconstraints[variable] = []
        for constraint, variables in constraints:
            for variable in variables:
                vconstraints[variable].append((constraint, variables))
        for constraint, variables in constraints[:]:
            constraint.preProcess(variables, domains, constraints, vconstraints)
        for domain in domains.values():
            domain.resetState()
            if not domain:
                return None, None, None
        # doArc8(getArcs(domains, constraints), domains, {})
        return domains, constraints, vconstraints
