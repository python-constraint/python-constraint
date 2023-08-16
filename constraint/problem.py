# cython: profile=True
"""Module containing the code for problem definitions."""

import copy

from .solvers import BacktrackingSolver
from .domain import Domain
from .constraints import Constraint, FunctionConstraint
from operator import itemgetter
from typing import Any, Optional
import cython

class Problem(object):
    """Class used to define a problem and retrieve solutions."""

    def __init__(self, solver=None):
        """Initialization method.

        @param solver: Problem solver used to find solutions
                       (default is L{BacktrackingSolver})
        @type solver:  instance of a L{Solver} subclass
        """
        self._solver = solver or BacktrackingSolver()
        self._constraints: list[tuple[Constraint, Optional[cython.int]]] = []
        self._variables: dict[cython.int, list] = {}
        self._map_external_variables_to_internal: dict[Any, cython.int] = dict()
        self._map_internal_variables_to_external: dict[cython.int, Any] = dict()
        self._map_variables_counter: cython.int = 0

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

        @param solver: New problem solver
        @type  solver: instance of a C{Solver} subclass
        """
        self._solver = solver

    def getSolver(self):
        """Obtain the problem solver currently in use.

        Example:
        >>> solver = BacktrackingSolver()
        >>> problem = Problem(solver)
        >>> problem.getSolver() is solver
        True

        @return: Solver currently in use
        @rtype: instance of a L{Solver} subclass
        """
        return self._solver

    def addVariable(self, variable, domain):
        """Add a variable to the problem.

        Example:
        >>> problem = Problem()
        >>> problem.addVariable("a", [1, 2])
        >>> problem.getSolution() in ({'a': 1}, {'a': 2})
        True

        @param variable: Object representing a problem variable
        @type  variable: hashable object
        @param domain: Set of items defining the possible values that
                       the given variable may assume
        @type  domain: list, tuple, or instance of C{Domain}
        """
        variable = self._set_variable_to_internal(variable)
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

    def _set_variable_to_internal(self, variable: Any) -> cython.int:
        if variable in self._map_external_variables_to_internal:
            raise ValueError(f"Tried to insert duplicate variable {variable}")
        internal_variable = self._map_variables_counter
        self._map_external_variables_to_internal[variable] = internal_variable
        self._map_internal_variables_to_external[internal_variable] = variable
        self._map_variables_counter += 1
        return internal_variable

    def _get_variable_from_internal(self, variable: cython.int) -> Any:
        return self._map_internal_variables_to_external[variable]

    def _get_variables_from_internal(self, variables: list[cython.int]) -> list[Any]:
        return list(self._map_internal_variables_to_external[v] for v in variables)

    def _get_variable_from_external(self, variable: Any) -> cython.int:
        return self._map_external_variables_to_internal[variable]

    def _get_variables_from_external(self, variables: list[Any]) -> list[cython.int]:
        return list(self._map_external_variables_to_internal[v] for v in variables)

    def addVariables(self, variables, domain):
        """Add one or more variables to the problem.

        Example:
        >>> problem = Problem()
        >>> problem.addVariables(["a", "b"], [1, 2, 3])
        >>> solutions = problem.getSolutions()
        >>> len(solutions)
        9
        >>> {'a': 3, 'b': 1} in solutions
        True

        @param variables: Any object containing a sequence of objects
                          represeting problem variables
        @type  variables: sequence of hashable objects
        @param domain: Set of items defining the possible values that
                       the given variables may assume
        @type  domain: list, tuple, or instance of C{Domain}
        """
        for variable in variables:
            self.addVariable(variable, domain)

    def addConstraint(self, constraint, variables=None):
        """Add a constraint to the problem.

        Example:
        >>> problem = Problem()
        >>> problem.addVariables(["a", "b"], [1, 2, 3])
        >>> problem.addConstraint(lambda a, b: b == a+1, ["a", "b"])
        >>> solutions = problem.getSolutions()
        >>>

        @param constraint: Constraint to be included in the problem
        @type  constraint: instance a L{Constraint} subclass or a
                           function to be wrapped by L{FunctionConstraint}
        @param variables: Variables affected by the constraint (default to
                          all variables). Depending on the constraint type
                          the order may be important.
        @type  variables: set or sequence of variables
        """
        if variables is not None:
            variables = self._get_variables_from_external(variables)
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

        @return: Solution for the problem
        @rtype: dictionary mapping variables to values
        """
        domains, constraints, vconstraints = self._getArgs()
        if not domains:
            return None
        solution = self._solver.getSolution(domains, constraints, vconstraints)
        if solution is not None:
            solution = dict(zip(self._get_variables_from_internal(list(solution.keys())), solution.values()))
        return solution

    def getSolutions(self):
        """Find and return all solutions to the problem.

        Example:
        >>> problem = Problem()
        >>> problem.getSolutions() == []
        True
        >>> problem.addVariables(["a"], [42])
        >>> problem.getSolutions()
        [{'a': 42}]

        @return: All solutions for the problem
        @rtype: list of dictionaries mapping variables to values
        """
        domains, constraints, vconstraints = self._getArgs()
        if not domains:
            return []
        solutions = self._solver.getSolutions(domains, constraints, vconstraints)
        if solutions is not None and len(solutions) > 0:
            variables = self._get_variables_from_internal(list(solutions[0].keys()))
            solutions = list(dict(zip(variables, solution.values())) for solution in solutions)
        return solutions

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
          File "<stdin>", line 1, in ?
        StopIteration
        """
        domains, constraints, vconstraints = self._getArgs()
        if not domains:
            return iter(())
        return self._solver.getSolutionIter(domains, constraints, vconstraints)

    def getSolutionsOrderedList(self, order: list[str] = None) -> list[tuple]:
        """Returns the solutions as a list of tuple, with each solution tuple ordered according to `order`."""
        solutions: list[dict[str, list]] = self.getSolutions()
        if order is None:
            return list(tuple(params) for params in solutions.values())
        if len(order) > 1:
            return list(itemgetter(*order)(params) for params in solutions)
        return list(params[order[0]] for params in solutions)
        # return list((tuple(params[param_name] for param_name in order)) for params in self.getSolutions())

    def getSolutionsAsListDict(self, order: list[str] = None, validate: bool = True) -> tuple[list[tuple], dict[tuple, int], int]:
        """Returns a tuple of the searchspace as a list of tuples, a dict of the searchspace for fast lookups and the size."""
        solutions_list = self.getSolutionsOrderedList(order)
        size_list = len(solutions_list)
        solutions_dict: dict[tuple, int] = dict(zip(solutions_list, range(size_list)))
        if validate:
            # check for duplicates
            size_dict = len(solutions_dict)
            if size_list != size_dict:
                raise ValueError(
                    f"{size_list - size_dict} duplicate parameter configurations in the searchspace, this should not happen."
                )
        return (
            solutions_list,
            solutions_dict,
            size_list,
        )

    def _getArgs(self):
        domains: dict[cython.int, list] = self._variables.copy()
        allvariables = domains.keys()
        constraints: list[tuple[Constraint, Optional[list[cython.int]]]] = []
        for constraint, variables in self._constraints:
            if not variables:
                variables = list(allvariables)
            constraints.append((constraint, variables))
        vconstraints: dict[cython.int, list[tuple[Constraint, Optional[list[cython.int]]]]] = {}
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
