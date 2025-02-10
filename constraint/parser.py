"""Module containing the code for parsing string constraints."""
import re
from types import FunctionType
from typing import Union, Optional
from constraint.constraints import (
    AllDifferentConstraint,
    AllEqualConstraint,
    Constraint,
    ExactSumConstraint,
    MaxProdConstraint,
    MaxSumConstraint,
    MinProdConstraint,
    MinSumConstraint,
    # TODO implement parsing for these constraints
    # FunctionConstraint,
    # InSetConstraint,
    # NotInSetConstraint,
    # SomeInSetConstraint,
    # SomeNotInSetConstraint,
)

def parse_restrictions(
    restrictions: list[str], tune_params: dict, monolithic=False, try_to_constraint=True
) -> list[tuple[Union[Constraint, str], list[str]]]:
    """Parses restrictions from a list of strings into compilable functions and constraints, or a single compilable function (if monolithic is True). Returns a list of tuples of (strings or constraints) and parameters."""   # noqa: E501
    # rewrite the restrictions so variables are singled out
    regex_match_variable = r"([a-zA-Z_$][a-zA-Z_$0-9]*)"

    def replace_params(match_object):
        key = match_object.group(1)
        if key in tune_params:
            param = str(key)
            return "params[params_index['" + param + "']]"
        else:
            return key

    def replace_params_split(match_object):
        # careful: has side-effect of adding to set `params_used`
        key = match_object.group(1)
        if key in tune_params:
            param = str(key)
            params_used.add(param)
            return param
        else:
            return key

    def to_multiple_restrictions(restrictions: list[str]) -> list[str]:
        """Split the restrictions into multiple restriction where possible (e.g. 3 <= x * y < 9 <= z -> [(MinProd(3), [x, y]), (MaxProd(9-1), [x, y]), (MinProd(9), [z])])."""  # noqa: E501
        split_restrictions = list()
        for res in restrictions:
            # if there are logic chains in the restriction, skip splitting further
            if " and " in res or " or " in res:
                split_restrictions.append(res)
                continue
            # find the indices of splittable comparators
            comparators = ["<=", ">=", ">", "<"]
            comparators_indices = [(m.start(0), m.end(0)) for m in re.finditer("|".join(comparators), res)]
            if len(comparators_indices) <= 1:
                # this can't be split further
                split_restrictions.append(res)
                continue
            # split the restrictions from the previous to the next comparator
            for index in range(len(comparators_indices)):
                temp_copy = res
                prev_stop = comparators_indices[index - 1][1] + 1 if index > 0 else 0
                next_stop = (
                    comparators_indices[index + 1][0] if index < len(comparators_indices) - 1 else len(temp_copy)
                )
                split_restrictions.append(temp_copy[prev_stop:next_stop].strip())
        return split_restrictions

    def to_numeric_constraint(
        restriction: str, params: list[str]
    ) -> Optional[Union[MinSumConstraint, ExactSumConstraint, MaxSumConstraint, MaxProdConstraint]]:
        """Converts a restriction to a built-in numeric constraint if possible."""
        comparators = ["<=", "==", ">=", ">", "<"]
        comparators_found = re.findall("|".join(comparators), restriction)
        # check if there is exactly one comparator, if not, return None
        if len(comparators_found) != 1:
            return None
        comparator = comparators_found[0]

        # split the string on the comparison and remove leading and trailing whitespace
        left, right = tuple(s.strip() for s in restriction.split(comparator))

        # find out which side is the constant number
        def is_or_evals_to_number(s: str) -> Optional[Union[int, float]]:
            try:
                # check if it's a number or solvable to a number (e.g. '32*2')
                number = eval(s)
                assert isinstance(number, (int, float))
                return number
            except Exception:
                # it's not a solvable subexpression, return None
                return None

        # either the left or right side of the equation must evaluate to a constant number
        left_num = is_or_evals_to_number(left)
        right_num = is_or_evals_to_number(right)
        if (left_num is None and right_num is None) or (left_num is not None and right_num is not None):
            # left_num and right_num can't be both None or both a constant
            return None
        number, variables, variables_on_left = (
            (left_num, right.strip(), False) if left_num is not None else (right_num, left.strip(), True)
        )

        # if the number is an integer, we can map '>' to '>=' and '<' to '<=' by changing the number (does not work with floating points!)  # noqa: E501
        number_is_int = isinstance(number, int)
        if number_is_int:
            if comparator == "<":
                if variables_on_left:
                    # (x < 2) == (x <= 2-1)
                    number -= 1
                else:
                    # (2 < x) == (2+1 <= x)
                    number += 1
            elif comparator == ">":
                if variables_on_left:
                    # (x > 2) == (x >= 2+1)
                    number += 1
                else:
                    # (2 > x) == (2-1 >= x)
                    number -= 1

        # check if an operator is applied on the variables, if not return
        operators = [r"\*\*", r"\*", r"\+"]
        operators_found = re.findall(str("|".join(operators)), variables)
        if len(operators_found) == 0:
            # no operators found, return only based on comparator
            if len(params) != 1 or variables not in params:
                # there were more than one variable but no operator
                return None
            # map to a Constraint
            # if there are restrictions with a single variable, it will be used to prune the domain at the start
            elif comparator == "==":
                return ExactSumConstraint(number)
            elif comparator == "<=" or (comparator == "<" and number_is_int):
                return MaxSumConstraint(number) if variables_on_left else MinSumConstraint(number)
            elif comparator == ">=" or (comparator == ">" and number_is_int):
                return MinSumConstraint(number) if variables_on_left else MaxSumConstraint(number)
            raise ValueError(f"Invalid comparator {comparator}")

        # check which operator is applied on the variables
        operator = operators_found[0]
        if not all(o == operator for o in operators_found):
            # if the operator is inconsistent (e.g. 'x + y * z == 3'), return None
            return None

        # split the string on the comparison
        splitted = variables.split(operator)
        # check if there are only pure, non-recurring variables (no operations or constants) in the restriction
        if len(splitted) == len(params) and all(s.strip() in params for s in splitted):
            # map to a Constraint
            if operator == "**":
                # power operations are not (yet) supported, added to avoid matching the double asterisk
                return None
            elif operator == "*":
                if comparator == "<=" or (comparator == "<" and number_is_int):
                    return MaxProdConstraint(number) if variables_on_left else MinProdConstraint(number)
                elif comparator == ">=" or (comparator == ">" and number_is_int):
                    return MinProdConstraint(number) if variables_on_left else MaxProdConstraint(number)
            elif operator == "+":
                if comparator == "==":
                    return ExactSumConstraint(number)
                elif comparator == "<=" or (comparator == "<" and number_is_int):
                    return MaxSumConstraint(number) if variables_on_left else MinSumConstraint(number)
                elif comparator == ">=" or (comparator == ">" and number_is_int):
                    return MinSumConstraint(number) if variables_on_left else MaxSumConstraint(number)
            else:
                raise ValueError(f"Invalid operator {operator}")
        return None

    def to_equality_constraint(
        restriction: str, params: list[str]
    ) -> Optional[Union[AllEqualConstraint, AllDifferentConstraint]]:
        """Converts a restriction to either an equality or inequality constraint on all the parameters if possible."""
        # check if all parameters are involved
        if len(params) != len(tune_params):
            return None

        # find whether (in)equalities appear in this restriction
        equalities_found = re.findall("==", restriction)
        inequalities_found = re.findall("!=", restriction)
        # check if one of the two have been found, if none or both have been found, return None
        if not (len(equalities_found) > 0 ^ len(inequalities_found) > 0):
            return None
        comparator = equalities_found[0] if len(equalities_found) > 0 else inequalities_found[0]

        # split the string on the comparison
        splitted = restriction.split(comparator)
        # check if there are only pure, non-recurring variables (no operations or constants) in the restriction
        if len(splitted) == len(params) and all(s.strip() in params for s in splitted):
            # map to a Constraint
            if comparator == "==":
                return AllEqualConstraint()
            elif comparator == "!=":
                return AllDifferentConstraint()
            return ValueError(f"Not possible: comparator should be '==' or '!=', is {comparator}")
        return None
    
    # remove functionally duplicate restrictions (preserves order and whitespace)
    if all(isinstance(r, str) for r in restrictions):
        # clean the restriction strings to functional equivalence
        restrictions_cleaned = [r.replace(' ', '') for r in restrictions]
        restrictions_cleaned_unique = list(dict.fromkeys(restrictions_cleaned)) # dict preserves order
        # get the indices of the unique restrictions, use these to build a new list of restrictions
        restrictions_unique_indices = [restrictions_cleaned.index(r) for r in restrictions_cleaned_unique]
        restrictions = [restrictions[i] for i in restrictions_unique_indices]

    # create the parsed restrictions
    if monolithic is False:
        # split into multiple restrictions where possible
        if try_to_constraint:
            restrictions = to_multiple_restrictions(restrictions)
        # split into functions that only take their relevant parameters
        parsed_restrictions = list()
        for res in restrictions:
            params_used: set[str] = set()
            parsed_restriction = re.sub(regex_match_variable, replace_params_split, res).strip()
            params_used_list = list(params_used)
            finalized_constraint = None
            if try_to_constraint and " or " not in res and " and " not in res:
                # if applicable, strip the outermost round brackets
                while (
                    parsed_restriction[0] == "("
                    and parsed_restriction[-1] == ")"
                    and "(" not in parsed_restriction[1:]
                    and ")" not in parsed_restriction[:1]
                ):
                    parsed_restriction = parsed_restriction[1:-1]
                # check if we can turn this into the built-in numeric comparison constraint
                finalized_constraint = to_numeric_constraint(parsed_restriction, params_used_list)
                if finalized_constraint is None:
                    # check if we can turn this into the built-in equality comparison constraint
                    finalized_constraint = to_equality_constraint(parsed_restriction, params_used_list)
            if finalized_constraint is None:
                # we must turn it into a general function
                finalized_constraint = f"def r({', '.join(params_used_list)}): return {parsed_restriction} \n"
            parsed_restrictions.append((finalized_constraint, params_used_list))
    else:
        # create one monolithic function
        parsed_restrictions = ") and (".join(
            [re.sub(regex_match_variable, replace_params, res) for res in restrictions]
        )

        # tidy up the code by removing the last suffix and unnecessary spaces
        parsed_restrictions = "(" + parsed_restrictions.strip() + ")"
        parsed_restrictions = " ".join(parsed_restrictions.split())

        # provide a mapping of the parameter names to the index in the tuple received
        params_index = dict(zip(tune_params.keys(), range(len(tune_params.keys()))))
        parsed_restrictions = [
            (
                f"def restrictions(*params): params_index = {params_index}; return {parsed_restrictions} \n",
                list(tune_params.keys()),
            )
        ]

    return parsed_restrictions

def compile_restrictions(
    restrictions: list, tune_params: dict, monolithic=False, try_to_constraint=True, picklable=False
) -> list[tuple[Union[str, Constraint, FunctionType], list[str], Union[str, None]]]:
    """Parses restrictions from a list of strings into a list of strings, Functions, or Constraints (if `try_to_constraint`) and parameters used and source, or a single Function if monolithic is true.

    picklable (bool): whether to keep constraints such that they can be pickled for parallel solvers. Defaults to False.    
    """ # noqa: E501
    # filter the restrictions to get only the strings
    restrictions_str, restrictions_ignore = [], []
    for r in restrictions:
        (restrictions_str if isinstance(r, str) else restrictions_ignore).append(r)
    if len(restrictions_str) == 0:
        return restrictions_ignore

    # parse the strings
    parsed_restrictions = parse_restrictions(
        restrictions_str, tune_params, monolithic=monolithic, try_to_constraint=try_to_constraint
    )

    # compile the parsed restrictions into a function
    compiled_restrictions: list[tuple] = list()
    for restriction, params_used in parsed_restrictions:
        if isinstance(restriction, str):
            # if it's a string, parse it to a function
            if picklable:
                compiled_restrictions.append((restriction, params_used, restriction))
            else:
                code_object = compile(restriction, "<string>", "exec")
                func = FunctionType(code_object.co_consts[0], globals())
                compiled_restrictions.append((func, params_used, restriction))
        elif isinstance(restriction, Constraint):
            # otherwise it already is a Constraint, pass it directly
            compiled_restrictions.append((restriction, params_used, None))
        else:
            raise ValueError(f"Restriction {restriction} is neither a string or Constraint {type(restriction)}")

    # return the restrictions and used parameters
    if len(restrictions_ignore) == 0:
        return compiled_restrictions

    # use the required parameters or add an empty tuple for unknown parameters of ignored restrictions
    noncompiled_restrictions = []
    for r in restrictions_ignore:
        if isinstance(r, tuple) and len(r) == 2 and isinstance(r[1], (list, tuple)):
            restriction, params_used = r
            noncompiled_restrictions.append((restriction, params_used, restriction))
        else:
            noncompiled_restrictions.append((r, [], r))
    return noncompiled_restrictions + compiled_restrictions
