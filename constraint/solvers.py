"""Module containing the code for the problem solvers."""

import random
from typing import List


def getArcs(domains: dict, constraints: List[tuple]) -> dict:
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


def doArc8(arcs: dict, domains: dict, assignments: dict) -> bool:
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

    def getSolution(self, domains: dict, constraints: List[tuple], vconstraints: dict):
        """Return one solution for the given problem.

        Args:
            domains (dict): Dictionary mapping variables to their domains
            constraints (list): List of pairs of (constraint, variables)
            vconstraints (dict): Dictionary mapping variables to a list
                of constraints affecting the given variables.
        """
        msg = "%s is an abstract class" % self.__class__.__name__
        raise NotImplementedError(msg)

    def getSolutions(self, domains: dict, constraints: List[tuple], vconstraints: dict):
        """Return all solutions for the given problem.

        Args:
            domains (dict): Dictionary mapping variables to domains
            constraints (list): List of pairs of (constraint, variables)
            vconstraints (dict): Dictionary mapping variables to a list
                of constraints affecting the given variables.
        """
        msg = "%s provides only a single solution" % self.__class__.__name__
        raise NotImplementedError(msg)

    def getSolutionIter(self, domains: dict, constraints: List[tuple], vconstraints: dict):
        """Return an iterator for the solutions of the given problem.

        Args:
            domains (dict): Dictionary mapping variables to domains
            constraints (list): List of pairs of (constraint, variables)
            vconstraints (dict): Dictionary mapping variables to a list
                of constraints affecting the given variables.
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

        Args:
            forwardcheck (bool): If false forward checking will not be
                requested to constraints while looking for solutions
                (default is true)
        """
        self._forwardcheck = forwardcheck

    def getSolutionIter(self, domains: dict, constraints: List[tuple], vconstraints: dict):  # noqa: D102
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

    def getSolution(self, domains: dict, constraints: List[tuple], vconstraints: dict):  # noqa: D102
        iter = self.getSolutionIter(domains, constraints, vconstraints)
        try:
            return next(iter)
        except StopIteration:
            return None

    def getSolutions(self, domains: dict, constraints: List[tuple], vconstraints: dict):  # noqa: D102
        return list(self.getSolutionIter(domains, constraints, vconstraints))

class OptimizedBacktrackingSolver(Solver):
    """Problem solver with backtracking capabilities, implementing several optimizations for increased performance.

    Optimizations are especially in obtaining all solutions.
    View https://github.com/python-constraint/python-constraint/pull/76 for more details.

    Examples:
        >>> result = [[('a', 1), ('b', 2)],
        ...           [('a', 1), ('b', 3)],
        ...           [('a', 2), ('b', 3)]]

        >>> problem = Problem(OptimizedBacktrackingSolver())
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

        Args:
            forwardcheck (bool): If false forward checking will not be
                requested to constraints while looking for solutions
                (default is true)
        """
        self._forwardcheck = forwardcheck

    def getSolutionIter(self, domains: dict, constraints: List[tuple], vconstraints: dict):  # noqa: D102
        forwardcheck = self._forwardcheck
        assignments = {}
        sorted_variables = self.getSortedVariables(domains, vconstraints)

        queue = []

        while True:
            # Mix the Degree and Minimum Remaing Values (MRV) heuristics
            for variable in sorted_variables:
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

    def getSolutionsList(self, domains: dict, vconstraints: dict) -> List[dict]:  # noqa: D102
        """Optimized all-solutions finder that skips forwardchecking and returns the solutions in a list.

        Args:
            domains: Dictionary mapping variables to domains
            vconstraints: Dictionary mapping variables to a list of constraints affecting the given variables.

        Returns:
            the list of solutions as a dictionary.
        """
        # Does not do forwardcheck for simplicity
        assignments: dict = {}
        queue: List[tuple] = []
        solutions: List[dict] = list()
        sorted_variables = self.getSortedVariables(domains, vconstraints)

        while True:
            # Mix the Degree and Minimum Remaing Values (MRV) heuristics
            for variable in sorted_variables:
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

        raise RuntimeError("Can't happen")


    def getSolutions(self, domains: dict, constraints: List[tuple], vconstraints: dict):  # noqa: D102
        if self._forwardcheck:
            return list(self.getSolutionIter(domains, constraints, vconstraints))
        return self.getSolutionsList(domains, vconstraints)

    def getSolution(self, domains: dict, constraints: List[tuple], vconstraints: dict):   # noqa: D102
        iter = self.getSolutionIter(domains, constraints, vconstraints)
        try:
            return next(iter)
        except StopIteration:
            return None

    def getSortedVariables(self, domains: dict, vconstraints: dict) -> list:
        """Sorts the list of variables on number of vconstraints to find unassigned variables quicker.

        Args:
            domains: Dictionary mapping variables to their domains
            vconstraints: Dictionary mapping variables to a list
                of constraints affecting the given variables.

        Returns:
            the list of variables, sorted from highest number of vconstraints to lowest.
        """
        lst = [(-len(vconstraints[variable]), len(domains[variable]), variable) for variable in domains]
        lst.sort()
        return [c for _, _, c in lst]


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

        Args:
            forwardcheck (bool): If false forward checking will not be
                requested to constraints while looking for solutions
                (default is true)
        """
        self._forwardcheck = forwardcheck

    def recursiveBacktracking(self, solutions, domains, vconstraints, assignments, single):
        """Mix the Degree and Minimum Remaing Values (MRV) heuristics.

        Args:
            solutions: _description_
            domains: _description_
            vconstraints: _description_
            assignments: _description_
            single: _description_

        Returns:
            _description_
        """
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

    def getSolution(self, domains: dict, constraints: List[tuple], vconstraints: dict):   # noqa: D102
        solutions = self.recursiveBacktracking([], domains, vconstraints, {}, True)
        return solutions and solutions[0] or None

    def getSolutions(self, domains: dict, constraints: List[tuple], vconstraints: dict):  # noqa: D102
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

        Args:
            steps (int): Maximum number of steps to perform before
                giving up when looking for a solution (default is 1000)
        """
        self._steps = steps

    def getSolution(self, domains: dict, constraints: List[tuple], vconstraints: dict):   # noqa: D102
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
