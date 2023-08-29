"""Module containing the code for constraint definitions."""

from constraint.domain import Unassigned
from typing import Callable, List, Union, Optional, Sequence

class Constraint(object):
    """Abstract base class for constraints."""

    def __call__(self, variables: Sequence, domains: dict, assignments: dict, forwardcheck=False):
        """Perform the constraint checking.

        If the forwardcheck parameter is not false, besides telling if
        the constraint is currently broken or not, the constraint
        implementation may choose to hide values from the domains of
        unassigned variables to prevent them from being used, and thus
        prune the search space.

        Args:
            variables (sequence): :py:class:`Variables` affected by that constraint,
                in the same order provided by the user
            domains (dict): Dictionary mapping variables to their
                domains
            assignments (dict): Dictionary mapping assigned variables to
                their current assumed value
            forwardcheck: Boolean value stating whether forward checking
                should be performed or not

        Returns:
            bool: Boolean value stating if this constraint is currently
            broken or not
        """
        return True

    def preProcess(self, variables: Sequence, domains: dict, constraints: List[tuple], vconstraints: dict):
        """Preprocess variable domains.

        This method is called before starting to look for solutions,
        and is used to prune domains with specific constraint logic
        when possible. For instance, any constraints with a single
        variable may be applied on all possible values and removed,
        since they may act on individual values even without further
        knowledge about other assignments.

        Args:
            variables (sequence): Variables affected by that constraint,
                in the same order provided by the user
            domains (dict): Dictionary mapping variables to their
                domains
            constraints (list): List of pairs of (constraint, variables)
            vconstraints (dict): Dictionary mapping variables to a list
                of constraints affecting the given variables.
        """
        if len(variables) == 1:
            variable = variables[0]
            domain = domains[variable]
            for value in domain[:]:
                if not self(variables, domains, {variable: value}):
                    domain.remove(value)
            constraints.remove((self, variables))
            vconstraints[variable].remove((self, variables))

    def forwardCheck(self, variables: Sequence, domains: dict, assignments: dict, _unassigned=Unassigned):
        """Helper method for generic forward checking.

        Currently, this method acts only when there's a single
        unassigned variable.

        Args:
            variables (sequence): Variables affected by that constraint,
                in the same order provided by the user
            domains (dict): Dictionary mapping variables to their
                domains
            assignments (dict): Dictionary mapping assigned variables to
                their current assumed value

        Returns:
            bool: Boolean value stating if this constraint is currently
            broken or not
        """
        unassignedvariable = _unassigned
        for variable in variables:
            if variable not in assignments:
                if unassignedvariable is _unassigned:
                    unassignedvariable = variable
                else:
                    break
        else:
            if unassignedvariable is not _unassigned:
                # Remove from the unassigned variable domain's all
                # values which break our variable's constraints.
                domain = domains[unassignedvariable]
                if domain:
                    for value in domain[:]:
                        assignments[unassignedvariable] = value
                        if not self(variables, domains, assignments):
                            domain.hideValue(value)
                    del assignments[unassignedvariable]
                if not domain:
                    return False
        return True


class FunctionConstraint(Constraint):
    """Constraint which wraps a function defining the constraint logic.

    Examples:
        >>> problem = Problem()
        >>> problem.addVariables(["a", "b"], [1, 2])
        >>> def func(a, b):
        ...     return b > a
        >>> problem.addConstraint(func, ["a", "b"])
        >>> problem.getSolution()
        {'a': 1, 'b': 2}

        >>> problem = Problem()
        >>> problem.addVariables(["a", "b"], [1, 2])
        >>> def func(a, b):
        ...     return b > a
        >>> problem.addConstraint(FunctionConstraint(func), ["a", "b"])
        >>> problem.getSolution()
        {'a': 1, 'b': 2}
    """

    def __init__(self, func: Callable, assigned: bool = True):
        """Initialization method.

        Args:
            func (callable object): Function wrapped and queried for
                constraint logic
            assigned (bool): Whether the function may receive unassigned
                variables or not
        """
        self._func = func
        self._assigned = assigned

    def __call__(  # noqa: D102
        self,
        variables: Sequence,
        domains: dict,
        assignments: dict,
        forwardcheck=False,
        _unassigned=Unassigned,
    ):
        # # initial code: 0.94621 seconds, Cythonized: 0.92805 seconds
        # parms = [assignments.get(x, _unassigned) for x in variables]
        # missing = parms.count(_unassigned)

        # # list comprehension and sum: 0.13744 seconds, Cythonized: 0.10059 seconds
        # parms = [assignments.get(x, _unassigned) for x in variables]
        # missing = sum(x not in assignments for x in variables)

        # # sum check with fallback: , Cythonized: 0.10108 seconds
        # missing = sum(x not in assignments for x in variables)
        # parms = [assignments.get(x, _unassigned) for x in variables] if missing > 0 else [assignments[x] for x in var]

        # # tuple list comprehension with unzipping: 0.14521 seconds, Cythonized: 0.12054 seconds
        # lst = [(assignments[x], 0) if x in assignments else (_unassigned, 1) for x in variables]
        # parms, missing_iter = zip(*lst)
        # parms = list(parms)
        # missing = sum(missing_iter)

        # # single loop array: 0.11249 seconds, Cythonized: 0.09514 seconds
        # parms = [None] * len(variables)
        # missing = 0
        # for i, x in enumerate(variables):
        #     if x in assignments:
        #         parms[i] = assignments[x]
        #     else:
        #         parms[i] = _unassigned
        #         missing += 1

        # single loop list: 0.11462 seconds, Cythonized: 0.08686 seconds
        parms = list()
        missing = 0
        for x in variables:
            if x in assignments:
                parms.append(assignments[x])
            else:
                parms.append(_unassigned)
                missing += 1

        # if there are unassigned variables, do a forward check before executing the restriction function
        if missing > 0:
            return (self._assigned or self._func(*parms)) and (
                not forwardcheck or missing != 1 or self.forwardCheck(variables, domains, assignments)
            )
        return self._func(*parms)


class AllDifferentConstraint(Constraint):
    """Constraint enforcing that values of all given variables are different.

    Example:
        >>> problem = Problem()
        >>> problem.addVariables(["a", "b"], [1, 2])
        >>> problem.addConstraint(AllDifferentConstraint())
        >>> sorted(sorted(x.items()) for x in problem.getSolutions())
        [[('a', 1), ('b', 2)], [('a', 2), ('b', 1)]]
    """

    def __call__(  # noqa: D102
        self,
        variables: Sequence,
        domains: dict,
        assignments: dict,
        forwardcheck=False,
        _unassigned=Unassigned,
    ):
        seen = {}
        for variable in variables:
            value = assignments.get(variable, _unassigned)
            if value is not _unassigned:
                if value in seen:
                    return False
                seen[value] = True
        if forwardcheck:
            for variable in variables:
                if variable not in assignments:
                    domain = domains[variable]
                    for value in seen:
                        if value in domain:
                            domain.hideValue(value)
                            if not domain:
                                return False
        return True


class AllEqualConstraint(Constraint):
    """Constraint enforcing that values of all given variables are equal.

    Example:
        >>> problem = Problem()
        >>> problem.addVariables(["a", "b"], [1, 2])
        >>> problem.addConstraint(AllEqualConstraint())
        >>> sorted(sorted(x.items()) for x in problem.getSolutions())
        [[('a', 1), ('b', 1)], [('a', 2), ('b', 2)]]
    """

    def __call__(   # noqa: D102
        self,
        variables: Sequence,
        domains: dict,
        assignments: dict,
        forwardcheck=False,
        _unassigned=Unassigned,
    ):
        singlevalue = _unassigned
        for variable in variables:
            value = assignments.get(variable, _unassigned)
            if singlevalue is _unassigned:
                singlevalue = value
            elif value is not _unassigned and value != singlevalue:
                return False
        if forwardcheck and singlevalue is not _unassigned:
            for variable in variables:
                if variable not in assignments:
                    domain = domains[variable]
                    if singlevalue not in domain:
                        return False
                    for value in domain[:]:
                        if value != singlevalue:
                            domain.hideValue(value)
        return True


class MaxSumConstraint(Constraint):
    """Constraint enforcing that values of given variables sum up to a given amount.

    Example:
        >>> problem = Problem()
        >>> problem.addVariables(["a", "b"], [1, 2])
        >>> problem.addConstraint(MaxSumConstraint(3))
        >>> sorted(sorted(x.items()) for x in problem.getSolutions())
        [[('a', 1), ('b', 1)], [('a', 1), ('b', 2)], [('a', 2), ('b', 1)]]
    """

    def __init__(self, maxsum: Union[int, float], multipliers: Optional[Sequence] = None):
        """Initialization method.

        Args:
            maxsum (number): Value to be considered as the maximum sum
            multipliers (sequence of numbers): If given, variable values
                will be multiplied by the given factors before being
                summed to be checked
        """
        self._maxsum = maxsum
        self._multipliers = multipliers

    def preProcess(self, variables: Sequence, domains: dict, constraints: List[tuple], vconstraints: dict): # noqa: D102
        Constraint.preProcess(self, variables, domains, constraints, vconstraints)

        # check if there are any negative values in the associated variables
        variable_contains_negative: list[bool] = list()
        variable_with_negative = None
        for variable in variables:
            contains_negative = any(value < 0 for value in domains[variable])
            variable_contains_negative.append(contains_negative)
            if contains_negative:
                if variable_with_negative is not None:
                    # if more than one associated variables contain negative, we can't prune
                    return
                variable_with_negative = variable

        # prune the associated variables of values > maxsum
        multipliers = self._multipliers
        maxsum = self._maxsum
        if multipliers:
            for variable, multiplier in zip(variables, multipliers):
                if variable_with_negative is not None and variable_with_negative != variable:
                    continue
                domain = domains[variable]
                for value in domain[:]:
                    if value * multiplier > maxsum:
                        domain.remove(value)
        else:
            for variable in variables:
                if variable_with_negative is not None and variable_with_negative != variable:
                    continue
                domain = domains[variable]
                for value in domain[:]:
                    if value > maxsum:
                        domain.remove(value)

    def __call__(self, variables: Sequence, domains: dict, assignments: dict, forwardcheck=False):  # noqa: D102
        multipliers = self._multipliers
        maxsum = self._maxsum
        sum = 0
        if multipliers:
            for variable, multiplier in zip(variables, multipliers):
                if variable in assignments:
                    sum += assignments[variable] * multiplier
            if isinstance(sum, float):
                sum = round(sum, 10)
            if sum > maxsum:
                return False
            if forwardcheck:
                for variable, multiplier in zip(variables, multipliers):
                    if variable not in assignments:
                        domain = domains[variable]
                        for value in domain[:]:
                            if sum + value * multiplier > maxsum:
                                domain.hideValue(value)
                        if not domain:
                            return False
        else:
            for variable in variables:
                if variable in assignments:
                    sum += assignments[variable]
            if isinstance(sum, float):
                sum = round(sum, 10)
            if sum > maxsum:
                return False
            if forwardcheck:
                for variable in variables:
                    if variable not in assignments:
                        domain = domains[variable]
                        for value in domain[:]:
                            if sum + value > maxsum:
                                domain.hideValue(value)
                        if not domain:
                            return False
        return True


class ExactSumConstraint(Constraint):
    """Constraint enforcing that values of given variables sum exactly to a given amount.

    Example:
        >>> problem = Problem()
        >>> problem.addVariables(["a", "b"], [1, 2])
        >>> problem.addConstraint(ExactSumConstraint(3))
        >>> sorted(sorted(x.items()) for x in problem.getSolutions())
        [[('a', 1), ('b', 2)], [('a', 2), ('b', 1)]]
    """

    def __init__(self, exactsum: Union[int, float], multipliers: Optional[Sequence] = None):
        """Initialization method.

        Args:
            exactsum (number): Value to be considered as the exact sum
            multipliers (sequence of numbers): If given, variable values
                will be multiplied by the given factors before being
                summed to be checked
        """
        self._exactsum = exactsum
        self._multipliers = multipliers

    def preProcess(self, variables: Sequence, domains: dict, constraints: List[tuple], vconstraints: dict): # noqa: D102
        Constraint.preProcess(self, variables, domains, constraints, vconstraints)
        multipliers = self._multipliers
        exactsum = self._exactsum
        if multipliers:
            for variable, multiplier in zip(variables, multipliers):
                domain = domains[variable]
                for value in domain[:]:
                    if value * multiplier > exactsum:
                        domain.remove(value)
        else:
            for variable in variables:
                domain = domains[variable]
                for value in domain[:]:
                    if value > exactsum:
                        domain.remove(value)

    def __call__(self, variables: Sequence, domains: dict, assignments: dict, forwardcheck=False):    # noqa: D102
        multipliers = self._multipliers
        exactsum = self._exactsum
        sum = 0
        missing = False
        if multipliers:
            for variable, multiplier in zip(variables, multipliers):
                if variable in assignments:
                    sum += assignments[variable] * multiplier
                else:
                    missing = True
            if isinstance(sum, float):
                sum = round(sum, 10)
            if sum > exactsum:
                return False
            if forwardcheck and missing:
                for variable, multiplier in zip(variables, multipliers):
                    if variable not in assignments:
                        domain = domains[variable]
                        for value in domain[:]:
                            if sum + value * multiplier > exactsum:
                                domain.hideValue(value)
                        if not domain:
                            return False
        else:
            for variable in variables:
                if variable in assignments:
                    sum += assignments[variable]
                else:
                    missing = True
            if isinstance(sum, float):
                sum = round(sum, 10)
            if sum > exactsum:
                return False
            if forwardcheck and missing:
                for variable in variables:
                    if variable not in assignments:
                        domain = domains[variable]
                        for value in domain[:]:
                            if sum + value > exactsum:
                                domain.hideValue(value)
                        if not domain:
                            return False
        if missing:
            return sum <= exactsum
        else:
            return sum == exactsum


class MinSumConstraint(Constraint):
    """Constraint enforcing that values of given variables sum at least to a given amount.

    Example:
        >>> problem = Problem()
        >>> problem.addVariables(["a", "b"], [1, 2])
        >>> problem.addConstraint(MinSumConstraint(3))
        >>> sorted(sorted(x.items()) for x in problem.getSolutions())
        [[('a', 1), ('b', 2)], [('a', 2), ('b', 1)], [('a', 2), ('b', 2)]]
    """

    def __init__(self, minsum: Union[int, float], multipliers: Optional[Sequence] = None):
        """Initialization method.

        Args:
            minsum (number): Value to be considered as the minimum sum
            multipliers (sequence of numbers): If given, variable values
                will be multiplied by the given factors before being
                summed to be checked
        """
        self._minsum = minsum
        self._multipliers = multipliers

    def __call__(self, variables: Sequence, domains: dict, assignments: dict, forwardcheck=False):    # noqa: D102
        # check if each variable is in the assignments
        for variable in variables:
            if variable not in assignments:
                return True

        # with each variable assigned, sum the values
        multipliers = self._multipliers
        minsum = self._minsum
        sum = 0
        if multipliers:
            for variable, multiplier in zip(variables, multipliers):
                sum += assignments[variable] * multiplier
        else:
            for variable in variables:
                sum += assignments[variable]
        if isinstance(sum, float):
            sum = round(sum, 10)
        return sum >= minsum


class MaxProdConstraint(Constraint):
    """Constraint enforcing that values of given variables create a product up to at most a given amount."""

    def __init__(self, maxprod: Union[int, float]):
        """Instantiate a MaxProdConstraint.

        Args:
            maxprod: Value to be considered as the maximum product
        """
        self._maxprod = maxprod

    def preProcess(self, variables: Sequence, domains: dict, constraints: List[tuple], vconstraints: dict): # noqa: D102
        Constraint.preProcess(self, variables, domains, constraints, vconstraints)

        # check if there are any values less than 1 in the associated variables
        variable_contains_lt1: list[bool] = list()
        variable_with_lt1 = None
        for variable in variables:
            contains_lt1 = any(value < 1 for value in domains[variable])
            variable_contains_lt1.append(contains_lt1)
            if contains_lt1 is True:
                if variable_with_lt1 is not None:
                    # if more than one associated variables contain less than 1, we can't prune
                    return
                variable_with_lt1 = variable

        # prune the associated variables of values > maxprod
        maxprod = self._maxprod
        for variable in variables:
            if variable_with_lt1 is not None and variable_with_lt1 != variable:
                continue
            domain = domains[variable]
            for value in domain[:]:
                if value > maxprod:
                    domain.remove(value)
                elif value == 0 and maxprod < 0:
                    domain.remove(value)

    def __call__(self, variables: Sequence, domains: dict, assignments: dict, forwardcheck=False):    # noqa: D102
        maxprod = self._maxprod
        prod = 1
        for variable in variables:
            if variable in assignments:
                prod *= assignments[variable]
        if isinstance(prod, float):
            prod = round(prod, 10)
        if prod > maxprod:
            return False
        if forwardcheck:
            for variable in variables:
                if variable not in assignments:
                    domain = domains[variable]
                    for value in domain[:]:
                        if prod * value > maxprod:
                            domain.hideValue(value)
                    if not domain:
                        return False
        return True


class MinProdConstraint(Constraint):
    """Constraint enforcing that values of given variables create a product up to at least a given amount."""

    def __init__(self, minprod: Union[int, float]):
        """Instantiate a MinProdConstraint.

        Args:
            minprod: Value to be considered as the maximum product
        """
        self._minprod = minprod

    def preProcess(self, variables: Sequence, domains: dict, constraints: List[tuple], vconstraints: dict): # noqa: D102
        Constraint.preProcess(self, variables, domains, constraints, vconstraints)

        # prune the associated variables of values > maxprod
        minprod = self._minprod
        for variable in variables:
            domain = domains[variable]
            for value in domain[:]:
                if value == 0 and minprod > 0:
                    domain.remove(value)

    def __call__(self, variables: Sequence, domains: dict, assignments: dict, forwardcheck=False):    # noqa: D102
        # check if each variable is in the assignments
        for variable in variables:
            if variable not in assignments:
                return True

        # with each variable assigned, sum the values
        minprod = self._minprod
        prod = 1
        for variable in variables:
            prod *= assignments[variable]
        if isinstance(prod, float):
            prod = round(prod, 10)
        return prod >= minprod


class InSetConstraint(Constraint):
    """Constraint enforcing that values of given variables are present in the given set.

    Example:
        >>> problem = Problem()
        >>> problem.addVariables(["a", "b"], [1, 2])
        >>> problem.addConstraint(InSetConstraint([1]))
        >>> sorted(sorted(x.items()) for x in problem.getSolutions())
        [[('a', 1), ('b', 1)]]
    """

    def __init__(self, set):
        """Initialization method.

        Args:
            set (set): Set of allowed values
        """
        self._set = set

    def __call__(self, variables, domains, assignments, forwardcheck=False):    # noqa: D102
        # preProcess() will remove it.
        raise RuntimeError("Can't happen")

    def preProcess(self, variables: Sequence, domains: dict, constraints: List[tuple], vconstraints: dict): # noqa: D102
        set = self._set
        for variable in variables:
            domain = domains[variable]
            for value in domain[:]:
                if value not in set:
                    domain.remove(value)
            vconstraints[variable].remove((self, variables))
        constraints.remove((self, variables))


class NotInSetConstraint(Constraint):
    """Constraint enforcing that values of given variables are not present in the given set.

    Example:
        >>> problem = Problem()
        >>> problem.addVariables(["a", "b"], [1, 2])
        >>> problem.addConstraint(NotInSetConstraint([1]))
        >>> sorted(sorted(x.items()) for x in problem.getSolutions())
        [[('a', 2), ('b', 2)]]
    """

    def __init__(self, set):
        """Initialization method.

        Args:
            set (set): Set of disallowed values
        """
        self._set = set

    def __call__(self, variables, domains, assignments, forwardcheck=False):    # noqa: D102
        # preProcess() will remove it.
        raise RuntimeError("Can't happen")

    def preProcess(self, variables: Sequence, domains: dict, constraints: List[tuple], vconstraints: dict): # noqa: D102
        set = self._set
        for variable in variables:
            domain = domains[variable]
            for value in domain[:]:
                if value in set:
                    domain.remove(value)
            vconstraints[variable].remove((self, variables))
        constraints.remove((self, variables))


class SomeInSetConstraint(Constraint):
    """Constraint enforcing that at least some of the values of given variables must be present in a given set.

    Example:
        >>> problem = Problem()
        >>> problem.addVariables(["a", "b"], [1, 2])
        >>> problem.addConstraint(SomeInSetConstraint([1]))
        >>> sorted(sorted(x.items()) for x in problem.getSolutions())
        [[('a', 1), ('b', 1)], [('a', 1), ('b', 2)], [('a', 2), ('b', 1)]]
    """

    def __init__(self, set, n=1, exact=False):
        """Initialization method.

        Args:
            set (set): Set of values to be checked
            n (int): Minimum number of assigned values that should be
                present in set (default is 1)
            exact (bool): Whether the number of assigned values which
                are present in set must be exactly `n`
        """
        self._set = set
        self._n = n
        self._exact = exact

    def __call__(self, variables: Sequence, domains: dict, assignments: dict, forwardcheck=False):    # noqa: D102
        set = self._set
        missing = 0
        found = 0
        for variable in variables:
            if variable in assignments:
                found += assignments[variable] in set
            else:
                missing += 1
        if missing:
            if self._exact:
                if not (found <= self._n <= missing + found):
                    return False
            else:
                if self._n > missing + found:
                    return False
            if forwardcheck and self._n - found == missing:
                # All unassigned variables must be assigned to
                # values in the set.
                for variable in variables:
                    if variable not in assignments:
                        domain = domains[variable]
                        for value in domain[:]:
                            if value not in set:
                                domain.hideValue(value)
                        if not domain:
                            return False
        else:
            if self._exact:
                if found != self._n:
                    return False
            else:
                if found < self._n:
                    return False
        return True


class SomeNotInSetConstraint(Constraint):
    """Constraint enforcing that at least some of the values of given variables must not be present in a given set.

    Example:
        >>> problem = Problem()
        >>> problem.addVariables(["a", "b"], [1, 2])
        >>> problem.addConstraint(SomeNotInSetConstraint([1]))
        >>> sorted(sorted(x.items()) for x in problem.getSolutions())
        [[('a', 1), ('b', 2)], [('a', 2), ('b', 1)], [('a', 2), ('b', 2)]]
    """

    def __init__(self, set, n=1, exact=False):
        """Initialization method.

        Args:
            set (set): Set of values to be checked
            n (int): Minimum number of assigned values that should not
                be present in set (default is 1)
            exact (bool): Whether the number of assigned values which
                are not present in set must be exactly `n`
        """
        self._set = set
        self._n = n
        self._exact = exact

    def __call__(self, variables: Sequence, domains: dict, assignments: dict, forwardcheck=False):    # noqa: D102
        set = self._set
        missing = 0
        found = 0
        for variable in variables:
            if variable in assignments:
                found += assignments[variable] not in set
            else:
                missing += 1
        if missing:
            if self._exact:
                if not (found <= self._n <= missing + found):
                    return False
            else:
                if self._n > missing + found:
                    return False
            if forwardcheck and self._n - found == missing:
                # All unassigned variables must be assigned to
                # values not in the set.
                for variable in variables:
                    if variable not in assignments:
                        domain = domains[variable]
                        for value in domain[:]:
                            if value in set:
                                domain.hideValue(value)
                        if not domain:
                            return False
        else:
            if self._exact:
                if found != self._n:
                    return False
            else:
                if found < self._n:
                    return False
        return True
