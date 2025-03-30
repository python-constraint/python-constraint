"""Module containing the code for the problem solvers."""

import random
from types import FunctionType
from constraint.domain import Domain
from constraint.constraints import Constraint, FunctionConstraint, CompilableFunctionConstraint
from collections.abc import Hashable

# for parallel solver
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


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

    requires_pickling = False

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
            lst.sort(key=lambda x: (x[0], x[1]))
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
        lst.sort(key=lambda x: (x[0], x[1]))
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
        lst.sort(key=lambda x: (x[0], x[1]))
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
    

class ParallelSolver(Solver):
    """Problem solver that executes all-solution solve in parallel (ProcessPool or ThreadPool mode).

        Sorts the domains on size, creating jobs for each value in the domain with the most variables.
        Each leaf job is solved locally with either optimized backtracking or recursion.
        Whether this is actually faster than non-parallel solving depends on your problem, and hardware and software environment. 

        Uses ThreadPool by default. Instantiate with process_mode=True to use ProcessPool. 
        In ProcessPool mode, the jobs do not share memory.
        In ProcessPool mode, precompiled FunctionConstraints are not allowed due to pickling, use string constraints instead.

    Examples:
        >>> result = [[('a', 1), ('b', 2)],
        ...           [('a', 1), ('b', 3)],
        ...           [('a', 2), ('b', 3)]]

        >>> problem = Problem(ParallelSolver())
        >>> problem.addVariables(["a", "b"], [1, 2, 3])
        >>> problem.addConstraint("b > a", ["a", "b"])

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
    """     # noqa E501

    def __init__(self, process_mode=False):
        """Initialization method. Set `process_mode` to True for using ProcessPool, otherwise uses ThreadPool."""
        super().__init__()
        self._process_mode = process_mode
        self.requires_pickling = process_mode

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
        args = ((self.requires_pickling, domains, constraint_lookup, first_var, val, remaining_vars.copy()) for val in domains[first_var])  # noqa: E501
        solutions: list[dict[Hashable, any]] = []

        # execute in parallel
        parallel_pool = ProcessPoolExecutor if self._process_mode else ThreadPoolExecutor
        with parallel_pool() as executor:
            # results = map(parallel_worker, args)  # sequential
            results = executor.map(parallel_worker, args, chunksize=1)   # parallel
            for result in results:
                solutions.extend(result)

        return solutions
    
    def getSolutions(self, domains: dict, constraints: list[tuple], vconstraints: dict):  # noqa: D102
        return self.getSolutionsList(domains, vconstraints)

### Helper functions for parallel solver

def is_valid(assignment: dict[Hashable, any], constraints_lookup: list[tuple[Constraint, Hashable]], domains: dict[Hashable, Domain]) -> bool:      # noqa E501
    """Check if all constraints are satisfied given the current assignment."""
    return all(
        constraint(vars_involved, domains, assignment, None)
        for constraint, vars_involved in constraints_lookup
        if all(v in assignment for v in vars_involved)
    )

def compile_to_function(constraint: CompilableFunctionConstraint) -> FunctionConstraint:
    """Compile a CompilableFunctionConstraint to a function, wrapped by a FunctionConstraint."""
    func_string = constraint._func
    code_object = compile(func_string, "<string>", "exec")
    func = FunctionType(code_object.co_consts[0], globals())
    return FunctionConstraint(func)
    
def sequential_recursive_backtrack(assignment: dict[Hashable, any], unassigned_vars: list[Hashable], domains: dict[Hashable, Domain], constraint_lookup: dict[Hashable, list[tuple[Constraint, Hashable]]]) -> list[dict[Hashable, any]]:     # noqa E501
    """Sequential recursive backtracking function for subproblems."""
    if not unassigned_vars:
        return [assignment.copy()]

    var = unassigned_vars[-1]
    remaining_vars = unassigned_vars[:-1]

    solutions: list[dict[Hashable, any]] = []
    for value in domains[var]:
        assignment[var] = value
        if is_valid(assignment, constraint_lookup[var], domains):
            solutions.extend(sequential_recursive_backtrack(assignment, remaining_vars, domains, constraint_lookup))
        del assignment[var]
    return solutions

def sequential_optimized_backtrack(assignment: dict[Hashable, any], unassigned_vars: list[Hashable], domains: dict[Hashable, Domain], constraint_lookup: dict[Hashable, list[tuple[Constraint, Hashable]]]) -> list[dict[Hashable, any]]:     # noqa E501
    """Sequential optimized backtracking (as in OptimizedBacktrackingSolver) function for subproblems."""
    # Does not do forwardcheck for simplicity

    assignments = assignment
    sorted_variables = unassigned_vars
    queue: list[tuple] = []
    solutions: list[dict] = list()

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
            for constraint, variables in constraint_lookup[variable]:
                if not constraint(variables, domains, assignments, None):
                    # Value is not good.
                    break
            else:
                break

        # Push state before looking for next variable.
        queue.append((variable, values))


def parallel_worker(args: tuple[bool, dict[Hashable, Domain], dict[Hashable, list[tuple[Constraint, Hashable]]], Hashable, any, list[Hashable]]) -> list[dict[Hashable, any]]:    # noqa E501
    """Worker function for parallel execution on first variable."""
    process_mode, domains, constraint_lookup, first_var, first_value, remaining_vars = args
    local_assignment = {first_var: first_value}

    if process_mode:
        # if there are any CompilableFunctionConstraint, they must be compiled locally first
        for var, constraints in constraint_lookup.items():
            constraint_lookup[var] = [tuple([compile_to_function(constraint) if isinstance(constraint, CompilableFunctionConstraint) else constraint, vals]) for constraint, vals in constraints]        # noqa E501

    # continue solving sequentially on this process
    if is_valid(local_assignment, constraint_lookup[first_var], domains):
        return sequential_optimized_backtrack(local_assignment, remaining_vars, domains, constraint_lookup)
    return []
    