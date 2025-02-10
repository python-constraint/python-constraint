"""Module containing the code for the problem solvers."""

import random
from copy import deepcopy
from types import FunctionType
from constraint.domain import Domain
from constraint.constraints import Constraint, FunctionConstraint, CompilableFunctionConstraint
from collections.abc import Hashable

# # for version 5
# import cython
# from cython.cimports.cpython import array
# from cython.parallel import prange, parallel
# from cython.cimports.libc.stdlib import boundscheck, wraparound, cdivision

# for version 6
from concurrent.futures import ProcessPoolExecutor


def getArcs(domains: dict, constraints: list[tuple]) -> dict:
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


class Solver:
    """Abstract base class for solvers."""

    def getSolution(self, domains: dict, constraints: list[tuple], vconstraints: dict):
        """Return one solution for the given problem.

        Args:
            domains (dict): Dictionary mapping variables to their domains
            constraints (list): List of pairs of (constraint, variables)
            vconstraints (dict): Dictionary mapping variables to a list
                of constraints affecting the given variables.
        """
        msg = f"{self.__class__.__name__} is an abstract class"
        raise NotImplementedError(msg)

    def getSolutions(self, domains: dict, constraints: list[tuple], vconstraints: dict):
        """Return all solutions for the given problem.

        Args:
            domains (dict): Dictionary mapping variables to domains
            constraints (list): List of pairs of (constraint, variables)
            vconstraints (dict): Dictionary mapping variables to a list
                of constraints affecting the given variables.
        """
        msg = f"{self.__class__.__name__} provides only a single solution"
        raise NotImplementedError(msg)

    def getSolutionIter(self, domains: dict, constraints: list[tuple], vconstraints: dict):
        """Return an iterator for the solutions of the given problem.

        Args:
            domains (dict): Dictionary mapping variables to domains
            constraints (list): List of pairs of (constraint, variables)
            vconstraints (dict): Dictionary mapping variables to a list
                of constraints affecting the given variables.
        """
        msg = f"{self.__class__.__name__} doesn't provide iteration"
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

    def getSolutionIter(self, domains: dict, constraints: list[tuple], vconstraints: dict):  # noqa: D102
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

    def getSolution(self, domains: dict, constraints: list[tuple], vconstraints: dict):  # noqa: D102
        iter = self.getSolutionIter(domains, constraints, vconstraints)
        try:
            return next(iter)
        except StopIteration:
            return None

    def getSolutions(self, domains: dict, constraints: list[tuple], vconstraints: dict):  # noqa: D102
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

    def getSolutionIter(self, domains: dict, constraints: list[tuple], vconstraints: dict):  # noqa: D102
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

    def getSolutionsList(self, domains: dict[Hashable, Domain], vconstraints: dict[Hashable, list[tuple[Constraint, Hashable]]]) -> list[dict[Hashable, any]]:  # noqa: D102, E501
        """Optimized all-solutions finder that skips forwardchecking and returns the solutions in a list.

        Args:
            domains: Dictionary mapping variables to domains
            vconstraints: Dictionary mapping variables to a list of constraints affecting the given variables.

        Returns:
            the list of solutions as a dictionary.
        """
        # Does not do forwardcheck for simplicity

        # version 0 (currently implemented in main)
        assignments: dict = {}
        queue: list[tuple] = []
        solutions: list[dict] = list()
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

    #     # # initial version 1 (synthetic speedup 6.2x)
    #     # def is_valid(assignment, vconstraints, domains):
    #     #     """Check if all constraints are satisfied given the current assignment."""
    #     #     for constraints in vconstraints.values():
    #     #         for constraint, vars_involved in constraints:
    #     #             if all(v in assignment for v in vars_involved):
    #     #                 if not constraint(vars_involved, domains, assignment, None):
    #     #                     return False
    #     #     return True

    #     # def backtrack(assignment, unassigned_vars, domains, vconstraints, solutions):
    #     #     """Recursive backtracking function to find all valid assignments."""
    #     #     if not unassigned_vars:
    #     #         solutions.append(assignment.copy())
    #     #         return
            
    #     #     var = unassigned_vars.pop()
    #     #     for value in domains[var]:
    #     #         assignment[var] = value
    #     #         if is_valid(assignment, vconstraints, domains):
    #     #             backtrack(assignment, unassigned_vars.copy(), domains, vconstraints, solutions)
    #     #         del assignment[var]
    #     #     unassigned_vars.append(var)

    #     # solutions = []
    #     # backtrack({}, list(domains.keys()), domains, vconstraints, solutions)
    #     # return solutions

    #     # # optimized version 2 (synthetic speedup 11.0x)
    #     # def is_valid(assignment, constraints_lookup):
    #     #     """Check if all constraints are satisfied given the current assignment."""
    #     #     assigned_vars = set(assignment)
    #     #     for constraint, vars_involved in constraints_lookup:
    #     #         if assigned_vars.issuperset(vars_involved):  # Ensure all vars are assigned
    #     #             if not constraint(vars_involved, domains, assignment, None):
    #     #                 return False
    #     #     return True

    #     # def backtrack(assignment, unassigned_vars):
    #     #     """Recursive backtracking function to find all valid assignments."""
    #     #     if not unassigned_vars:
    #     #         solutions.append(assignment.copy())
    #     #         return
            
    #     #     var = unassigned_vars.pop()
    #     #     for value in domains[var]:
    #     #         assignment[var] = value
    #     #         if is_valid(assignment, constraint_lookup[var]):
    #     #             backtrack(assignment, unassigned_vars)
    #     #         del assignment[var]
    #     #     unassigned_vars.append(var)

    #     # # Precompute constraints lookup per variable
    #     # constraint_lookup = {var: vconstraints.get(var, []) for var in domains}

    #     # solutions = []
    #     # backtrack({}, list(domains.keys()))
    #     # return solutions
    
    #     # # optimized version 3 (synthetic speedup 11.0x, added type hints)
    #     # def is_valid(assignment: dict[Hashable, any], constraints_lookup: list[tuple[Constraint, Hashable]]):
    #     #     """Check if all constraints are satisfied given the current assignment."""
    #     #     assigned_vars = set(assignment)
    #     #     for constraint, vars_involved in constraints_lookup:
    #     #         if assigned_vars.issuperset(vars_involved):  # Ensure all vars are assigned
    #     #             if not constraint(vars_involved, domains, assignment, None):
    #     #                 return False
    #     #     return True

    #     # def backtrack(assignment: dict[Hashable, any], unassigned_vars: list[Hashable]):
    #     #     """Recursive backtracking function to find all valid assignments."""
    #     #     if not unassigned_vars:
    #     #         solutions.append(assignment.copy())
    #     #         return
            
    #     #     var: Hashable = unassigned_vars.pop()
    #     #     for value in domains[var]:
    #     #         assignment[var] = value
    #     #         if is_valid(assignment, constraint_lookup[var]):
    #     #             backtrack(assignment, unassigned_vars)
    #     #         del assignment[var]
    #     #     unassigned_vars.append(var)

    #     # # Precompute constraints lookup per variable
    #     # constraint_lookup: (insert type) = {var: vconstraints.get(var, []) for var in domains}

    #     # solutions = []
    #     # backtrack({}, list(domains.keys()))
    #     # return solutions

    #     # optimized version 4 (synthetic speedup 13.1x, variables ordered by domain size, yield instead of append)
    #     def is_valid(assignment: dict[Hashable, any], constraints_lookup: list[tuple[Constraint, Hashable]]) -> bool:
    #         """Check if all constraints are satisfied given the current assignment."""
    #         return all(
    #             constraint(vars_involved, domains, assignment, None)
    #             for constraint, vars_involved in constraints_lookup
    #             if all(v in assignment for v in vars_involved)
    #         )

    #     def backtrack(assignment: dict[Hashable, any], unassigned_vars: list[Hashable]) -> Generator[dict[Hashable, any]]:    # noqa E501
    #         """Recursive backtracking function to find all valid assignments."""
    #         if not unassigned_vars:
    #             yield assignment.copy()
    #             return
            
    #         var = unassigned_vars[-1]  # Get the last variable without modifying the list
    #         remaining_vars = unassigned_vars[:-1]  # Avoid list mutation
            
    #         for value in domains[var]:
    #             assignment[var] = value
    #             if is_valid(assignment, constraint_lookup[var]):
    #                 yield from backtrack(assignment, remaining_vars)
    #             del assignment[var]

    #     # Precompute constraints lookup per variable
    #     constraint_lookup: dict[Hashable, list[tuple[Constraint, Hashable]]] = {var: vconstraints.get(var, []) for var in domains} # noqa E501

    #     # Sort variables by domain size (heuristic)
    #     sorted_vars: list[Hashable] = sorted(domains.keys(), key=lambda v: len(domains[v]))

    #     solutions: list[dict[Hashable, any]] = list(backtrack({}, sorted_vars))
    #     return solutions

    # # optimized version 5 (cython parallel)

    # # part of optimized version 5
    # @cython.nogil
    # def is_valid(assignment: dict[Hashable, any], constraints_lookup: list[tuple[Constraint, Hashable]], domains: dict[Hashable, Domain]) -> bool:    # noqa E501
    #     """Check if all constraints are satisfied given the current assignment."""
    #     return all(
    #         constraint(vars_involved, domains, assignment, None)
    #         for constraint, vars_involved in constraints_lookup
    #         if all(v in assignment for v in vars_involved)
    #     )

    # @cython.nogil
    # def backtrack(assignment: dict[Hashable, any], unassigned_vars: list[Hashable], local_solutions: list[dict[Hashable, any]], domains: dict[Hashable, Domain], constraint_lookup: dict[Hashable, list[tuple[Constraint, Hashable]]]):   # noqa E501
    #     """Sequential recursive backtracking function."""
    #     if not unassigned_vars:
    #         local_solutions.append(assignment.copy())
    #         return

    #     var: Hashable = unassigned_vars[-1]
    #     remaining_vars = unassigned_vars[:-1]  # Avoid modifying the list

    #     for value in domains[var]:
    #         assignment[var] = value
    #         if is_valid(assignment, constraint_lookup[var]):
    #             backtrack(assignment, remaining_vars, local_solutions, domains)
    #         del assignment[var]
    # @boundscheck(False)
    # @wraparound(False)
    # @cdivision(True)
    # def getSolutionsList(self, domains: dict[Hashable, Domain], vconstraints: dict[Hashable, list[tuple[Constraint, Hashable]]]) -> list[dict[Hashable, any]]:  # noqa: D102, E501
    #     """Parallelized all-solutions finder using Cython and OpenMP for branching."""

    #     # Precompute constraints lookup per variable
    #     constraint_lookup: dict[Hashable, list[tuple[Constraint, Hashable]]] = {var: vconstraints.get(var, []) for var in domains}    # noqa E501

    #     # Sort variables by domain size (heuristic)
    #     sorted_vars: list[Hashable] = sorted(domains.keys(), key=lambda v: len(domains[v]))

    #     # Parallelization on the first variable
    #     first_var = sorted_vars[0]
    #     remaining_vars = sorted_vars[1:]
    #     first_var_length = len(domains[first_var])

    #     # Convert to Cython types
    #     domains_c = cython.declare(array.array, domains)

    #     solutions: list[dict[Hashable, any]] = []

    #     print(f"First domain size: {first_var_length}")

    #     i = cython.declare(cython.int)

    #     # Parallel loop over the first variable's domain
    #     with cython.nogil, parallel():
    #         for i in prange(first_var_length, schedule='dynamic'):
    #             local_solutions: list[dict[Hashable, any]] = []
    #             first_value = domains_c[first_var][i]
    #             local_assignment = {first_var: first_value}
    #             if is_valid(local_assignment, constraint_lookup[first_var]):
    #                 backtrack(local_assignment, remaining_vars, local_solutions, domains_c, constraint_lookup)
    #             with cython.gil:
    #                 solutions.extend(local_solutions)  # Merge results safely

    #     return solutions

    def getSolutions(self, domains: dict, constraints: list[tuple], vconstraints: dict):  # noqa: D102
        if self._forwardcheck:
            return list(self.getSolutionIter(domains, constraints, vconstraints))
        return self.getSolutionsList(domains, vconstraints)

    def getSolution(self, domains: dict, constraints: list[tuple], vconstraints: dict):  # noqa: D102
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

    def getSolution(self, domains: dict, constraints: list[tuple], vconstraints: dict):  # noqa: D102
        solutions = self.recursiveBacktracking([], domains, vconstraints, {}, True)
        return solutions and solutions[0] or None

    def getSolutions(self, domains: dict, constraints: list[tuple], vconstraints: dict):  # noqa: D102
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

    def __init__(self, steps=1000, rand=None):
        """Initialization method.

        Args:
            steps (int): Maximum number of steps to perform before
                giving up when looking for a solution (default is 1000)
            rand (Random): Optional random.Random instance to use for
                repeatability.
        """
        self._steps = steps
        self._rand = rand

    def getSolution(self, domains: dict, constraints: list[tuple], vconstraints: dict):   # noqa: D102
        choice = self._rand.choice if self._rand is not None else random.choice
        shuffle = self._rand.shuffle if self._rand is not None else random.shuffle
        assignments = {}
        # Initial assignment
        for variable in domains:
            assignments[variable] = choice(domains[variable])
        for _ in range(self._steps):
            conflicted = False
            lst = list(domains.keys())
            shuffle(lst)
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
                assignments[variable] = choice(minvalues)
                conflicted = True
            if not conflicted:
                return assignments
        return None


### Helper functions for parallel solver

def is_valid(assignment: dict[Hashable, any], constraints_lookup: list[tuple[Constraint, Hashable]], domains: dict[Hashable, Domain]) -> bool:      # noqa E501
    """Check if all constraints are satisfied given the current assignment."""
    return all(
        constraint(vars_involved, domains, assignment, None)
        for constraint, vars_involved in constraints_lookup
        if all(v in assignment for v in vars_involved)
    )

def compile_to_function(constraint: CompilableFunctionConstraint) -> FunctionConstraint:
    """Compile a CompilableFunctionConstraint to a function, wrapped by a FunctionConstraint"""
    func_string = constraint._func
    code_object = compile(func_string, "<string>", "exec")
    func = FunctionType(code_object.co_consts[0], globals())
    return FunctionConstraint(func)
    
def sequential_backtrack(assignment: dict[Hashable, any], unassigned_vars: list[Hashable], domains: dict[Hashable, Domain], constraint_lookup: dict[Hashable, list[tuple[Constraint, Hashable]]]) -> list[dict[Hashable, any]]:     # noqa E501
    """Sequential recursive backtracking function for subproblems."""
    # TODO check if using the OptimizedBacktracking approach is more efficient
    if not unassigned_vars:
        return [assignment.copy()]

    var = unassigned_vars[-1]
    remaining_vars = unassigned_vars[:-1]

    solutions: list[dict[Hashable, any]] = []
    for value in domains[var]:
        assignment[var] = value
        if is_valid(assignment, constraint_lookup[var], domains):
            solutions.extend(sequential_backtrack(assignment, remaining_vars, domains, constraint_lookup))
        del assignment[var]
    return solutions

def parallel_worker(args: tuple[dict[Hashable, Domain], dict[Hashable, list[tuple[Constraint, Hashable]]], Hashable, any, list[Hashable]]) -> list[dict[Hashable, any]]:    # noqa E501
    """Worker function for parallel execution on first variable."""
    domains, constraint_lookup, first_var, first_value, remaining_vars = args
    local_assignment = {first_var: first_value}

    # if there are any CompilableFunctionConstraint, they must be compiled locally first
    for var, constraints in constraint_lookup.items():
        constraint_lookup[var] = [tuple([compile_to_function(constraint) if isinstance(constraint, CompilableFunctionConstraint) else constraint, vals]) for constraint, vals in constraints]        # noqa E501

    # continue solving sequentially on this process
    if is_valid(local_assignment, constraint_lookup[first_var], domains):
        return sequential_backtrack(local_assignment, remaining_vars, domains, constraint_lookup)
    return []

class ParallelSolver(Solver):
    """Problem solver that executes all-solution solve in parallel.

    Sorts the domains on size, creating jobs for each value in the domain with the most variables.
    Each leaf job is solved recursively.

    Examples:
        >>> result = [[('a', 1), ('b', 2)],
        ...           [('a', 1), ('b', 3)],
        ...           [('a', 2), ('b', 3)]]

        >>> problem = Problem(ParallelSolver())
        >>> problem.addVariables(["a", "b"], [1, 2, 3])
        >>> problem.addConstraint(lambda a, b: b > a, ["a", "b"])

        >>> for solution in problem.getSolutions():
        ...     sorted(solution.items()) in result
        True
        True
        True

        >>> problem.getSolution()
        Traceback (most recent call last):
        ...
        NotImplementedError: ParallelSolver only provides all solutions

        >>> problem.getSolutionIter()
        Traceback (most recent call last):
        ...
        NotImplementedError: ParallelSolver doesn't provide iteration
    """

    def __init__(self):
        """Initialization method."""
        super().__init__()

    def getSolution(self, domains: dict, constraints: list[tuple], vconstraints: dict):
        """Return one solution for the given problem.

        Args:
            domains (dict): Dictionary mapping variables to their domains
            constraints (list): List of pairs of (constraint, variables)
            vconstraints (dict): Dictionary mapping variables to a list
                of constraints affecting the given variables.
        """
        msg = f"{self.__class__.__name__} only provides all solutions"
        raise NotImplementedError(msg)

        # optimized version 6 (python parallel)
    def getSolutionsList(self, domains: dict[Hashable, Domain], vconstraints: dict[Hashable, list[tuple[Constraint, Hashable]]]) -> list[dict[Hashable, any]]:  # noqa: D102, E501
        """Parallelized all-solutions finder using ProcessPoolExecutor for work-stealing."""
        # Precompute constraints lookup per variable
        constraint_lookup: dict[Hashable, list[tuple[Constraint, Hashable]]] = {var: vconstraints.get(var, []) for var in domains}  # noqa: E501

        # Sort variables by domain size (heuristic)
        sorted_vars: list[Hashable] = sorted(domains.keys(), key=lambda v: len(domains[v]))

        # Split parallel and sequential parts
        first_var = sorted_vars[0]
        remaining_vars = sorted_vars[1:]

        # Create the parallel function arguments and solutions lists
        args = ((domains, deepcopy(constraint_lookup), first_var, val, remaining_vars.copy()) for val in domains[first_var])
        solutions: list[dict[Hashable, any]] = []

        # execute in parallel
        with ProcessPoolExecutor() as executor:
            # results = map(parallel_worker, args)  # sequential
            results = executor.map(parallel_worker, args, chunksize=1)   # parallel
            for result in results:
                solutions.extend(result)

        return solutions
    
    def getSolutions(self, domains: dict, constraints: list[tuple], vconstraints: dict):  # noqa: D102
        return self.getSolutionsList(deepcopy(domains), deepcopy(vconstraints))
    