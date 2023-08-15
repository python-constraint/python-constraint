# cython: linetrace=True
"""Module containing the code for the problem solvers."""

import random
from multiprocessing import Queue, Manager, Pool, Lock

from itertools import product
import re
from math import prod
from .constraints import (
    AllDifferentConstraint,
    AllEqualConstraint,
    Constraint,
    ExactSumConstraint,
    FunctionConstraint,
    InSetConstraint,
    MaxSumConstraint,
    MinSumConstraint,
    NotInSetConstraint,
    SomeInSetConstraint,
    SomeNotInSetConstraint,
)

lock = Lock()


def getArcs(domains, constraints):
    """Return a dictionary mapping pairs (arcs) of constrained variables.

    @attention: Currently unused.
    """
    arcs = {}
    for x in constraints:
        constraint, variables = x
        if len(variables) == 2:
            variable1, variable2 = variables
            arcs.setdefault(variable1, {}).setdefault(variable2, []).append(x)
            arcs.setdefault(variable2, {}).setdefault(variable1, []).append(x)
    return arcs


def doArc8(arcs, domains, assignments):
    """Perform the ARC-8 arc checking algorithm and prune domains.

    @attention: Currently unused.
    """
    check = dict.fromkeys(domains, True)
    while check:
        variable, _ = check.popitem()
        if variable not in arcs or variable in assignments:
            continue
        domain = domains[variable]
        arcsvariable = arcs[variable]
        for othervariable in arcsvariable:
            arcconstraints = arcsvariable[othervariable]
            if othervariable in assignments:
                otherdomain = [assignments[othervariable]]
            else:
                otherdomain = domains[othervariable]
            if domain:
                # changed = False
                for value in domain[:]:
                    assignments[variable] = value
                    if otherdomain:
                        for othervalue in otherdomain:
                            assignments[othervariable] = othervalue
                            for constraint, variables in arcconstraints:
                                if not constraint(variables, domains, assignments, True):
                                    break
                            else:
                                # All constraints passed. Value is safe.
                                break
                        else:
                            # All othervalues failed. Kill value.
                            domain.hideValue(value)
                            # changed = True
                        del assignments[othervariable]
                del assignments[variable]
                # if changed:
                #     check.update(dict.fromkeys(arcsvariable))
            if not domain:
                return False
    return True


class Solver(object):
    """Abstract base class for solvers."""

    def getSolution(self, domains, constraints, vconstraints):
        """Return one solution for the given problem.

        @param domains: Dictionary mapping variables to their domains
        @type  domains: dict
        @param constraints: List of pairs of (constraint, variables)
        @type  constraints: list
        @param vconstraints: Dictionary mapping variables to a list of
                             constraints affecting the given variables.
        @type  vconstraints: dict
        """
        msg = "%s is an abstract class" % self.__class__.__name__
        raise NotImplementedError(msg)

    def getSolutions(self, domains, constraints, vconstraints):
        """Return all solutions for the given problem.

        @param domains: Dictionary mapping variables to domains
        @type  domains: dict
        @param constraints: List of pairs of (constraint, variables)
        @type  constraints: list
        @param vconstraints: Dictionary mapping variables to a list of
                             constraints affecting the given variables.
        @type  vconstraints: dict
        """
        msg = "%s provides only a single solution" % self.__class__.__name__
        raise NotImplementedError(msg)

    def getSolutionIter(self, domains, constraints, vconstraints):
        """Return an iterator for the solutions of the given problem.

        @param domains: Dictionary mapping variables to domains
        @type  domains: dict
        @param constraints: List of pairs of (constraint, variables)
        @type  constraints: list
        @param vconstraints: Dictionary mapping variables to a list of
                             constraints affecting the given variables.
        @type  vconstraints: dict
        """
        msg = "%s doesn't provide iteration" % self.__class__.__name__
        raise NotImplementedError(msg)


class BacktrackingSolver(Solver):
    """Problem solver with backtracking capabilities.

    Examples:
    >>> result = [[('a', 1), ('b', 2)],
    ...           [('a', 1), ('b', 3)],
    ...           [('a', 2), ('b', 3)]]

    >>> problem = Problem(BacktrackingSolver())
    >>> problem.addVariables(["a", "b"], [1, 2, 3])
    >>> problem.addConstraint(lambda a, b: b > a, ["a", "b"])

    >>> solution = problem.getSolution()
    >>> sorted(solution.items()) in result
    True

    >>> for solution in problem.getSolutionIter():
    ...     sorted(solution.items()) in result
    True
    True
    True

    >>> for solution in problem.getSolutions():
    ...     sorted(solution.items()) in result
    True
    True
    True
    """

    def __init__(self, forwardcheck=True):
        """Initialization method.

        @param forwardcheck: If false forward checking will not be requested
                             to constraints while looking for solutions
                             (default is true)
        @type  forwardcheck: bool
        """
        self._forwardcheck = forwardcheck

    def getSolutionIter(self, domains, constraints, vconstraints):  # noqa: D102
        forwardcheck = self._forwardcheck
        assignments = {}

        queue = []

        while True:
            # Mix the Degree and Minimum Remaing Values (MRV) heuristics
            lst = [(-len(vconstraints[variable]), len(domains[variable]), variable) for variable in domains]
            lst.sort()
            for item in lst:
                if item[-1] not in assignments:
                    # Found unassigned variable
                    variable = item[-1]
                    values = domains[variable][:]
                    if forwardcheck:
                        pushdomains = [domains[x] for x in domains if x not in assignments and x != variable]
                    else:
                        pushdomains = None
                    break
            else:
                # No unassigned variables. We've got a solution. Go back
                # to last variable, if there's one.
                yield assignments.copy()
                if not queue:
                    return
                variable, values, pushdomains = queue.pop()
                if pushdomains:
                    for domain in pushdomains:
                        domain.popState()

            while True:
                # We have a variable. Do we have any values left?
                if not values:
                    # No. Go back to last variable, if there's one.
                    del assignments[variable]
                    while queue:
                        variable, values, pushdomains = queue.pop()
                        if pushdomains:
                            for domain in pushdomains:
                                domain.popState()
                        if values:
                            break
                        del assignments[variable]
                    else:
                        return

                # Got a value. Check it.
                assignments[variable] = values.pop()

                if pushdomains:
                    for domain in pushdomains:
                        domain.pushState()

                for constraint, variables in vconstraints[variable]:
                    if not constraint(variables, domains, assignments, pushdomains):
                        # Value is not good.
                        break
                else:
                    break

                if pushdomains:
                    for domain in pushdomains:
                        domain.popState()

            # Push state before looking for next variable.
            queue.append((variable, values, pushdomains))

        raise RuntimeError("Can't happen")

    def getSolution(self, domains, constraints, vconstraints):  # noqa: D102
        iter = self.getSolutionIter(domains, constraints, vconstraints)
        try:
            return next(iter)
        except StopIteration:
            return None

    def getSolutions(self, domains, constraints, vconstraints):  # noqa: D102
        return list(self.getSolutionIter(domains, constraints, vconstraints))

def solve(id: int, assignments, queue: Queue, solutions, domains: dict[str, list], vconstraints: dict[str, list], lst: list):
    while True:
        # Mix the Degree and Minimum Remaing Values (MRV) heuristics
        for variable in lst:
            if variable not in assignments:
                # Found unassigned variable
                values = domains[variable][:]
                break
        else:
            # No unassigned variables. We've got a solution. Go back
            # to last variable, if there's one.
            with lock:
                solutions.append(assignments.copy())
            if queue.empty():
                return solutions
            variable, values = queue.get()

        while True:
            # We have a variable. Do we have any values left?
            if not values:
                # No. Go back to last variable, if there's one.
                with lock:
                    del assignments[variable]
                    while not queue.empty():
                        variable, values = queue.get()
                        if values:
                            break
                        del assignments[variable]
                    else:
                        return solutions

            # Got a value. Check it.
            with lock:
                assignments[variable] = values.pop()

            for constraint, variables in vconstraints[variable]:
                if not constraint(variables, domains, assignments, None):
                    # Value is not good.
                    break
            else:
                break

        # Push state before looking for next variable.
        with lock:
            queue.put((variable, values))
        # print(len(queue))

    raise RuntimeError("Can't happen")

class OptimizedBacktrackingSolver(Solver):
    """Problem solver with backtracking capabilities, implementing several optimizations for increased performance.

    Optimizations applied:
    - improved check on missing / unassigned parameters
    - several optimizations described here: https://github.com/python-constraint/python-constraint/issues/62

    To do:
    - profiling to check hotspots
    - further cythonizing
    - mapping variable names to integers internally
    - avoiding expensive dict.copy() where possible

    Examples:
    >>> result = [[('a', 1), ('b', 2)],
    ...           [('a', 1), ('b', 3)],
    ...           [('a', 2), ('b', 3)]]

    >>> problem = Problem(BacktrackingSolver())
    >>> problem.addVariables(["a", "b"], [1, 2, 3])
    >>> problem.addConstraint(lambda a, b: b > a, ["a", "b"])

    >>> solution = problem.getSolution()
    >>> sorted(solution.items()) in result
    True

    >>> for solution in problem.getSolutionIter():
    ...     sorted(solution.items()) in result
    True
    True
    True

    >>> for solution in problem.getSolutions():
    ...     sorted(solution.items()) in result
    True
    True
    True
    """

    def __init__(self, forwardcheck=True):
        """Initialization method.

        @param forwardcheck: If false forward checking will not be requested
                            to constraints while looking for solutions
                            (default is true)
        @type  forwardcheck: bool
        """
        self._forwardcheck = forwardcheck

    def getSolutionIter(self, domains, constraints, vconstraints, lst):  # noqa: D102
        forwardcheck = self._forwardcheck
        assignments = {}

        queue = []

        while True:
            # Mix the Degree and Minimum Remaing Values (MRV) heuristics
            for variable in lst:
                if variable not in assignments:
                    # Found unassigned variable
                    values = domains[variable][:]
                    if forwardcheck:
                        pushdomains = [domains[x] for x in domains if x not in assignments and x != variable]
                    else:
                        pushdomains = None
                    break
            else:
                # No unassigned variables. We've got a solution. Go back
                # to last variable, if there's one.
                yield assignments.copy()
                if not queue:
                    return
                variable, values, pushdomains = queue.pop()
                if pushdomains:
                    for domain in pushdomains:
                        domain.popState()

            while True:
                # We have a variable. Do we have any values left?
                if not values:
                    # No. Go back to last variable, if there's one.
                    del assignments[variable]
                    while queue:
                        variable, values, pushdomains = queue.pop()
                        if pushdomains:
                            for domain in pushdomains:
                                domain.popState()
                        if values:
                            break
                        del assignments[variable]
                    else:
                        return

                # Got a value. Check it.
                assignments[variable] = values.pop()

                if pushdomains:
                    for domain in pushdomains:
                        domain.pushState()

                for constraint, variables in vconstraints[variable]:
                    if not constraint(variables, domains, assignments, pushdomains):
                        # Value is not good.
                        break
                else:
                    break

                if pushdomains:
                    for domain in pushdomains:
                        domain.popState()

            # Push state before looking for next variable.
            queue.append((variable, values, pushdomains))

        raise RuntimeError("Can't happen")

    def getSolutionsList(self, domains: dict[str, list], vconstraints: dict[str, list], lst: list) -> list[dict]:  # noqa: D102
        # Does not do forwardcheck for simplicity
        assignments = {}
        queue: list[tuple] = []
        solutions: list[dict] = list()

        while True:
            # Mix the Degree and Minimum Remaing Values (MRV) heuristics
            for variable in lst:
                if variable not in assignments:
                    # Found unassigned variable
                    values = domains[variable][:]
                    break
            else:
                # No unassigned variables. We've got a solution. Go back
                # to last variable, if there's one.
                solutions.append(assignments.copy())
                if not queue:
                    return solutions
                variable, values = queue.pop()

            while True:
                # We have a variable. Do we have any values left?
                if not values:
                    # No. Go back to last variable, if there's one.
                    del assignments[variable]
                    while queue:
                        variable, values = queue.pop()
                        if values:
                            break
                        del assignments[variable]
                    else:
                        return solutions

                # Got a value. Check it.
                assignments[variable] = values.pop()

                for constraint, variables in vconstraints[variable]:
                    if not constraint(variables, domains, assignments, None):
                        # Value is not good.
                        break
                else:
                    break

            # Push state before looking for next variable.
            queue.append((variable, values))
            # print(len(queue))

        raise RuntimeError("Can't happen")

    def getSolutionsListParallel(self, domains: dict[str, list], vconstraints: dict[str, list], lst: list) -> list[dict]:  # noqa: D102
        # Does not do forwardcheck for simplicity
        # assignments = {}
        # queue: list[tuple] = []
        # solutions: list[dict] = list()

        # parallel version
        num_workers = 4
        manager = Manager()
        assignments = manager.dict(lock=True)
        queue = manager.Queue()
        solutions = manager.list()
        jobargs = [(id, assignments, queue, solutions, domains, vconstraints, lst) for i in range(num_workers)]

        p = Pool(num_workers)
        t = p.map(solve, jobargs)
        p.close()
        p.join()

        print(solutions)
        return solutions

    def getSolutionsBruteforce(self, domains, constraints, vconstraints) -> list:
        # TODO see how fast Cythonized bruteforced can be (optionally with prange)
        param_names = list(domains.keys())
        if constraints is not None and len(constraints) > 0:
            # shrink the domain by applying restrictions that only use one parameter
            restrictions, pruned_restrictions = convert_restrictions(constraints)
            for r, p in pruned_restrictions:
                param_name = p[0]
                domains[param_name] = filter(lambda v: check_converted_restrictions(r, dict(zip([param_name], [v])) ), domains[param_name])
            # make bounds on number-type parameters that have restrictions
            # TODO
            # apply all restrictions on the cartesian product
            parameter_space = filter(lambda p: check_converted_restrictions(restrictions, dict(zip(param_names, p))), product(*domains.values()))
        else:
            # compute cartesian product of all tunable parameters
            parameter_space = product(*domains.values())
        return list(dict(zip(param_names, sol)) for sol in parameter_space)


    def getSolutions(self, domains, constraints, vconstraints):  # noqa: D102
        return self.getSolutionsBruteforce(domains, constraints, vconstraints)
        # sort the list from highest number of vconstraints to lowest to find unassigned variables as soon as possible
        lst = [(-len(vconstraints[variable]), len(domains[variable]), variable) for variable in domains]
        lst.sort()
        return self.getSolutionsList(domains, vconstraints, [c for a, b, c in lst])
        return list(self.getSolutionIter(domains, constraints, vconstraints, [c for a, b, c in lst]))

    def getSolution(self, domains, constraints, vconstraints):   # noqa: D102
        iter = self.getSolutionIter(domains, constraints, vconstraints)
        try:
            return next(iter)
        except StopIteration:
            return None


class RecursiveBacktrackingSolver(Solver):
    """Recursive problem solver with backtracking capabilities.

    Examples:
    >>> result = [[('a', 1), ('b', 2)],
    ...           [('a', 1), ('b', 3)],
    ...           [('a', 2), ('b', 3)]]

    >>> problem = Problem(RecursiveBacktrackingSolver())
    >>> problem.addVariables(["a", "b"], [1, 2, 3])
    >>> problem.addConstraint(lambda a, b: b > a, ["a", "b"])

    >>> solution = problem.getSolution()
    >>> sorted(solution.items()) in result
    True

    >>> for solution in problem.getSolutions():
    ...     sorted(solution.items()) in result
    True
    True
    True

    >>> problem.getSolutionIter()
    Traceback (most recent call last):
       ...
    NotImplementedError: RecursiveBacktrackingSolver doesn't provide iteration
    """

    def __init__(self, forwardcheck=True):
        """Initialization method.

        @param forwardcheck: If false forward checking will not be requested
                             to constraints while looking for solutions
                             (default is true)
        @type  forwardcheck: bool
        """
        self._forwardcheck = forwardcheck

    def recursiveBacktracking(self, solutions, domains, vconstraints, assignments, single):
        """Mix the Degree and Minimum Remaing Values (MRV) heuristics."""
        lst = [(-len(vconstraints[variable]), len(domains[variable]), variable) for variable in domains]
        lst.sort()
        for item in lst:
            if item[-1] not in assignments:
                # Found an unassigned variable. Let's go.
                break
        else:
            # No unassigned variables. We've got a solution.
            solutions.append(assignments.copy())
            return solutions

        variable = item[-1]
        assignments[variable] = None

        forwardcheck = self._forwardcheck
        if forwardcheck:
            pushdomains = [domains[x] for x in domains if x not in assignments]
        else:
            pushdomains = None

        for value in domains[variable]:
            assignments[variable] = value
            if pushdomains:
                for domain in pushdomains:
                    domain.pushState()
            for constraint, variables in vconstraints[variable]:
                if not constraint(variables, domains, assignments, pushdomains):
                    # Value is not good.
                    break
            else:
                # Value is good. Recurse and get next variable.
                self.recursiveBacktracking(solutions, domains, vconstraints, assignments, single)
                if solutions and single:
                    return solutions
            if pushdomains:
                for domain in pushdomains:
                    domain.popState()
        del assignments[variable]
        return solutions

    def getSolution(self, domains, constraints, vconstraints):   # noqa: D102
        solutions = self.recursiveBacktracking([], domains, vconstraints, {}, True)
        return solutions and solutions[0] or None

    def getSolutions(self, domains, constraints, vconstraints):  # noqa: D102
        return self.recursiveBacktracking([], domains, vconstraints, {}, False)


class MinConflictsSolver(Solver):
    """Problem solver based on the minimum conflicts theory.

    Examples:
    >>> result = [[('a', 1), ('b', 2)],
    ...           [('a', 1), ('b', 3)],
    ...           [('a', 2), ('b', 3)]]

    >>> problem = Problem(MinConflictsSolver())
    >>> problem.addVariables(["a", "b"], [1, 2, 3])
    >>> problem.addConstraint(lambda a, b: b > a, ["a", "b"])

    >>> solution = problem.getSolution()
    >>> sorted(solution.items()) in result
    True

    >>> problem.getSolutions()
    Traceback (most recent call last):
       ...
    NotImplementedError: MinConflictsSolver provides only a single solution

    >>> problem.getSolutionIter()
    Traceback (most recent call last):
       ...
    NotImplementedError: MinConflictsSolver doesn't provide iteration
    """

    def __init__(self, steps=1000):
        """Initialization method.

        @param steps: Maximum number of steps to perform before giving up
                      when looking for a solution (default is 1000)
        @type  steps: int
        """
        self._steps = steps

    def getSolution(self, domains, constraints, vconstraints):   # noqa: D102
        assignments = {}
        # Initial assignment
        for variable in domains:
            assignments[variable] = random.choice(domains[variable])
        for _ in range(self._steps):
            conflicted = False
            lst = list(domains.keys())
            random.shuffle(lst)
            for variable in lst:
                # Check if variable is not in conflict
                for constraint, variables in vconstraints[variable]:
                    if not constraint(variables, domains, assignments):
                        break
                else:
                    continue
                # Variable has conflicts. Find values with less conflicts.
                mincount = len(vconstraints[variable])
                minvalues = []
                for value in domains[variable]:
                    assignments[variable] = value
                    count = 0
                    for constraint, variables in vconstraints[variable]:
                        if not constraint(variables, domains, assignments):
                            count += 1
                    if count == mincount:
                        minvalues.append(value)
                    elif count < mincount:
                        mincount = count
                        del minvalues[:]
                        minvalues.append(value)
                # Pick a random one from these values.
                assignments[variable] = random.choice(minvalues)
                conflicted = True
            if not conflicted:
                return assignments
        return None

def convert_restrictions(restrictions) -> tuple[list[tuple], list[tuple]]:
    if callable(restrictions):
        return ([restrictions], [])
    new_restrictions: list[tuple] = list()
    pruned_restrictions: list[tuple] = list()
    for restriction in restrictions:
        param_names = []
        if isinstance(restriction, tuple):
            restriction, param_names = restriction
        if isinstance(restriction, Constraint):
            restriction = convert_constraint_restriction(restriction)
        elif isinstance(restriction, str):
            def f_restrict(p):
                return eval(replace_param_occurrences(restriction, p))
            restriction = f_restrict
        elif callable(restriction):
            pass
        else:
            raise ValueError(f"Unkown restriction type {type(restriction)}")
        if len(param_names) == 1:
            pruned_restrictions.append((restriction, param_names))
        else:
            new_restrictions.append((restriction, param_names))
    return (new_restrictions, pruned_restrictions)

def check_converted_restrictions(restrictions: list[tuple], params: dict):
    valid = True
    for restriction, param_names in restrictions:
        param_values = list(params.values()) if len(param_names) == 0 else [params[k] for k in param_names]
        if not restriction(param_values):
            valid = False
            break
    return valid


def check_restrictions(restrictions, params: dict, verbose: bool):
    """Check whether a specific instance meets the search space restrictions."""
    valid = True
    if callable(restrictions):
        valid = restrictions(params)
    else:
        for restrict in restrictions:
            try:
                # if it's a tuple, extract the restriction and the used parameter names
                if isinstance(restrict, tuple):
                    restrict, param_names = restrict
                    param_values = [params[k] for k in param_names]
                # if it's a python-constraint, convert to function and execute
                if isinstance(restrict, Constraint):
                    if param_values is None:
                        param_values = params.values()
                    restrict = convert_constraint_restriction(restrict)
                    if not restrict(param_values):
                        valid = False
                        break
                # if it's a string, fill in the parameters and evaluate
                elif isinstance(restrict, str) and not eval(replace_param_occurrences(restrict, params)):
                    valid = False
                    break
                # if it's a function, call it
                elif callable(restrict) and not restrict(params):
                    valid = False
                    break
            except ZeroDivisionError:
                pass
    if not valid and verbose:
        print(f"skipping config {params}, reason: config fails restriction")
    return valid


def convert_constraint_restriction(restrict: Constraint):
    """Convert the python-constraint to a function for backwards compatibility."""
    if isinstance(restrict, FunctionConstraint):
        def f_restrict(p):
            return restrict._func(*p)
    elif isinstance(restrict, AllDifferentConstraint):
        def f_restrict(p):
            return len(set(p)) == len(p)
    elif isinstance(restrict, AllEqualConstraint):
        def f_restrict(p):
            return all(x == p[0] for x in p)
    elif "MaxProdConstraint" in str(type(restrict)):
        def f_restrict(p):
            return prod(p) <= restrict._maxprod
    elif isinstance(restrict, MaxSumConstraint):
        def f_restrict(p):
            return sum(p) <= restrict._maxsum
    elif isinstance(restrict, ExactSumConstraint):
        def f_restrict(p):
            return sum(p) == restrict._exactsum
    elif isinstance(restrict, MinSumConstraint):
        def f_restrict(p):
            return sum(p) >= restrict._minsum
    elif isinstance(restrict, (InSetConstraint, NotInSetConstraint, SomeInSetConstraint, SomeNotInSetConstraint)):
        raise NotImplementedError(
            f"Restriction of the type {type(restrict)} is explicitely not supported in backwards compatibility mode, because the behaviour is too complex. Please rewrite this constraint to a function to use it with this algorithm."
        )
    else:
        raise TypeError(f"Unrecognized restriction {restrict}")
    return f_restrict

def replace_param_occurrences(string: str, params: dict):
    """Replace occurrences of the tuning params with their current value."""
    result = ""

    # Split on tokens and replace a token if it is a key in `params`.
    for part in re.split("([a-zA-Z0-9_]+)", string):
        if part in params:
            result += str(params[part])
        else:
            result += part

    return result
