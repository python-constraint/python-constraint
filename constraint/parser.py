"""Module containing the code for parsing string constraints."""
import re
from types import FunctionType
from typing import Union, Optional
from constraint.constraints import (
    AllDifferentConstraint,
    AllEqualConstraint,
    Constraint,
    ExactSumConstraint,
    MinSumConstraint,
    MaxSumConstraint,
    ExactProdConstraint,
    MinProdConstraint,
    MaxProdConstraint,
    FunctionConstraint,
    CompilableFunctionConstraint,
    VariableExactSumConstraint,
    VariableMinSumConstraint,
    VariableMaxSumConstraint,
    VariableExactProdConstraint,
    VariableMinProdConstraint,
    VariableMaxProdConstraint,
    # TODO implement parsing for these constraints:
    # InSetConstraint,
    # NotInSetConstraint,
    # SomeInSetConstraint,
    # SomeNotInSetConstraint,
)

def parse_restrictions(restrictions: list[str], tune_params: dict) -> list[tuple[Union[Constraint, str], list[str]]]:
    """Parses restrictions (constraints in string format) from a list of strings into compilable functions and constraints. Returns a list of tuples of (strings or constraints) and parameters."""   # noqa: E501
    # rewrite the restrictions so variables are singled out
    regex_match_variable = r"([a-zA-Z_$][a-zA-Z_$0-9]*)"
    regex_match_variable_or_constant = r"([a-zA-Z_$0-9]*)"

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
    ) -> Optional[Union[MinSumConstraint, VariableMinSumConstraint, ExactSumConstraint, VariableExactSumConstraint, MaxSumConstraint, VariableMaxSumConstraint, MinProdConstraint, VariableMinProdConstraint, ExactProdConstraint, VariableExactProdConstraint, MaxProdConstraint, VariableMaxProdConstraint]]:  # noqa: E501
        """Converts a restriction to a built-in numeric constraint if possible."""
        # first check if all parameters have only numbers as values
        if len(params) == 0 or not all(all(isinstance(v, (int, float)) for v in tune_params[p]) for p in params):
            return None

        comparators = ["<=", "==", ">=", ">", "<"]
        comparators_found = re.findall("|".join(comparators), restriction)
        # check if there is exactly one comparator, if not, return None
        if len(comparators_found) != 1:
            return None
        comparator = comparators_found[0]

        # split the string on the comparison and remove leading and trailing whitespace
        left, right = tuple(s.strip() for s in restriction.split(comparator))

        # if we have an inverse operation, rewrite to the other side
        supported_operators = ["**", "*", "+", "-", "/"]
        operators_left = [s.strip() for s in list(left) if s in supported_operators]
        operators_right = [s.strip() for s in list(right) if s in supported_operators]
        # TODO implement the case where the minus is part of a constant, e.g. "-3 <= x + y"
        if len(operators_left) > 0 and len(operators_right) > 0:
            # if there are operators on both sides, we can't handle this yet
            return None
        unique_operators_left = set(operators_left)
        unique_operators_right = set(operators_right)
        unique_operators = unique_operators_left.union(unique_operators_right)
        if len(unique_operators) == 1:
            variables_on_left = len(unique_operators_left) > 0
            swapped_side_first_component = re.search(regex_match_variable_or_constant, left if variables_on_left else right)    # noqa: E501
            if swapped_side_first_component is None:
                # if there is no variable on the left side, we can't handle this yet
                return None
            else:
                swapped_side_first_component = swapped_side_first_component.group(0)
            if "-" in unique_operators:
                if not variables_on_left:
                    # e.g. "G == B-M" becomes "G+M == B"
                    right_remainder = right[len(swapped_side_first_component):]
                    left_swap = right_remainder.replace("-", "+")
                    restriction = f"{left}{left_swap}{comparator}{swapped_side_first_component}"
                else:
                    # e.g. "B-M == G" becomes "B == G+M"
                    left_remainder = left[len(swapped_side_first_component):]
                    right_swap = left_remainder.replace("-", "+")
                    restriction = f"{swapped_side_first_component}{comparator}{right}{right_swap}"
            if "/" in unique_operators:
                if not variables_on_left:
                    # e.g. "G == B/M" becomes "G*M == B"
                    right_remainder = right[len(swapped_side_first_component):]
                    left_swap = right_remainder.replace("/", "*")
                    restriction = f"{left}{left_swap}{comparator}{swapped_side_first_component}"
                else:
                    # e.g. "B/M == G" becomes "B == G*M"
                    left_remainder = left[len(swapped_side_first_component):]
                    right_swap = left_remainder.replace("/", "*")
                    restriction = f"{swapped_side_first_component}{comparator}{right}{right_swap}"

            # we have a potentially rewritten restriction, split again
            left, right = tuple(s.strip() for s in restriction.split(comparator))
            operators_left = [s.strip() for s in list(left) if s in supported_operators]
            operators_right = [s.strip() for s in list(right) if s in supported_operators]
            unique_operators_left = set(operators_left)
            unique_operators_right = set(operators_right)
            unique_operators = unique_operators_left.union(unique_operators_right)

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

        # either the left or right side of the equation must evaluate to a constant number, otherwise we use a VariableConstraint   # noqa: E501
        left_num = is_or_evals_to_number(left)
        right_num = is_or_evals_to_number(right)
        if (left_num is None and right_num is None) or (left_num is not None and right_num is not None):
            # if both sides are parameters, try to use the VariableConstraints
            variable_supported_operators = ['+', '*']
            # variables = [s.strip() for s in list(left + right) if s not in variable_supported_operators]
            variables = re.findall(regex_match_variable, restriction)

            # if the restriction contains more than the variables and supported operators, return None
            if len(variables) == 0:
                return None
            if any(var.strip() not in tune_params for var in variables):
                raise ValueError(f"Variables {variables} not in tune_params {tune_params.keys()}")
            if len(re.findall('[+-]?\d+', restriction)) > 0:    # adjust when we support modifiers such as multipliers
                # if the restriction contains numbers, return None
                return None

            # find all unique variable_supported_operators in the restriction, can have at most one
            variable_operators_left = list(s.strip() for s in list(left) if s in variable_supported_operators)
            variable_operators_right = list(s.strip() for s in list(right) if s in variable_supported_operators)
            variable_unique_operators = list(set(variable_operators_left).union(set(variable_operators_right)))
            # if there is a mix of operators (e.g. 'x + y * z == a') or multiple variables on both sides, return None
            if len(variable_unique_operators) <= 1 and all(s.strip() in params for s in variables) and (len(unique_operators_left) == 0 or len(unique_operators_right) == 0):  # noqa: E501
                variables_on_left = len(unique_operators_left) > 0
                if len(variable_unique_operators) == 0 or variable_unique_operators[0] == "+":
                    if comparator == "==":
                        return VariableExactSumConstraint(variables[-1], variables[:-1]) if variables_on_left else VariableExactSumConstraint(variables[0], variables[1:])  # noqa: E501
                    elif comparator == "<=":
                        # "B+C <= A" (maxsum) if variables_on_left else "A <= B+C" (minsum)
                        return VariableMaxSumConstraint(variables[-1], variables[:-1]) if variables_on_left else VariableMinSumConstraint(variables[0], variables[1:])  # noqa: E501
                    elif comparator == ">=":
                        # "B+C >= A" (minsum) if variables_on_left else "A >= B+C" (maxsum)
                        return VariableMinSumConstraint(variables[-1], variables[:-1]) if variables_on_left else VariableMaxSumConstraint(variables[0], variables[1:])  # noqa: E501
                elif variable_unique_operators[0] == "*":
                    if comparator == "==":
                        return VariableExactProdConstraint(variables[-1], variables[:-1]) if variables_on_left else VariableExactProdConstraint(variables[0], variables[1:])  # noqa: E501
                    elif comparator == "<=":
                        # "B*C <= A" (maxprod) if variables_on_left else "A <= B*C" (minprod)
                        return VariableMaxProdConstraint(variables[-1], variables[:-1]) if variables_on_left else VariableMinProdConstraint(variables[0], variables[1:])    # noqa: E501
                    elif comparator == ">=":
                        # "B*C >= A" (minprod) if variables_on_left else "A >= B*C" (maxprod)
                        return VariableMinProdConstraint(variables[-1], variables[:-1]) if variables_on_left else VariableMaxProdConstraint(variables[0], variables[1:])    # noqa: E501

            # left_num and right_num can't both be constants, or for other reasons we can't use a VariableConstraint
            return None

        # if one side is a number, the other side must be a variable or expression
        number, variables, variables_on_left = (
            (left_num, right.strip(), False) if left_num is not None else (right_num, left.strip(), True)
        )

        # we can map '>' to '>=' and '<' to '<=' by adding a tiny offset to the number
        offset = 1e-12
        if comparator == "<":
            if variables_on_left:
                # (x < 2) == (x <= 2-offset)
                number -= offset
            else:
                # (2 < x) == (2+offset <= x)
                number += offset
        elif comparator == ">":
            if variables_on_left:
                # (x > 2) == (x >= 2+offset)
                number += offset
            else:
                # (2 > x) == (2-offset >= x)
                number -= offset

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
            elif comparator == "<=" or comparator == "<":
                return MaxSumConstraint(number) if variables_on_left else MinSumConstraint(number)
            elif comparator == ">=" or comparator == ">":
                return MinSumConstraint(number) if variables_on_left else MaxSumConstraint(number)
            raise ValueError(f"Invalid comparator {comparator}")

        # check which operator is applied on the variables
        operator = operators_found[0]
        if not all(o == operator for o in operators_found):
            # if there is a mix of operators (e.g. 'x + y * z == 3'), return None
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
                if comparator == "==":
                    return ExactProdConstraint(number)
                elif comparator == "<=" or comparator == "<":
                    return MaxProdConstraint(number) if variables_on_left else MinProdConstraint(number)
                elif comparator == ">=" or comparator == ">":
                    return MinProdConstraint(number) if variables_on_left else MaxProdConstraint(number)
            elif operator == "+":
                if comparator == "==":
                    return ExactSumConstraint(number)
                elif comparator == "<=" or comparator == "<":
                    # raise ValueError(restriction, comparator)
                    return MaxSumConstraint(number) if variables_on_left else MinSumConstraint(number)
                elif comparator == ">=" or comparator == ">":
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
        if not (bool(len(equalities_found) > 0) ^ bool(len(inequalities_found) > 0)):
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

    # create the parsed restrictions, split into multiple restrictions where possible
    restrictions = to_multiple_restrictions(restrictions)
    # split into functions that only take their relevant parameters
    parsed_restrictions = list()
    for res in restrictions:
        params_used: set[str] = set()
        parsed_restriction = re.sub(regex_match_variable, replace_params_split, res).strip()
        params_used_list = list(params_used)
        finalized_constraint = None
        if " or " not in res and " and " not in res:
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

    return parsed_restrictions

def compile_to_constraints(constraints: list[str], domains: dict, picklable=False) -> list[tuple[Constraint, list[str], Union[str, None]]]:    # noqa: E501
    """Parses constraints in string format (referred to as restrictions) from a list of strings into a list of Constraints, parameters used, and source if applicable.

    Args:
        constraints (list[str]): list of constraints in string format to compile.
        domains (dict): the domains to use.
        picklable (bool, optional): whether to keep constraints such that they can be pickled for parallel solvers. Defaults to False.

    Returns:
        list of tuples with restrictions, parameters used (list[str]), and source (str) if applicable. Returned restrictions are strings, functions, or Constraints depending on the options provided.
    """ # noqa: E501
    parsed_restrictions = parse_restrictions(constraints, domains)
    compiled_constraints: list[tuple[Constraint, list[str], Union[str, None]]] = list()
    for restriction, params_used in parsed_restrictions:
        if isinstance(restriction, str):
            # if it's a string, wrap it in a (compilable or compiled) function constraint
            if picklable:
                constraint = CompilableFunctionConstraint(restriction)
            else:
                code_object = compile(restriction, "<string>", "exec")
                func = FunctionType(code_object.co_consts[0], globals())
                constraint = FunctionConstraint(func)
            compiled_constraints.append((constraint, params_used, restriction))
        elif isinstance(restriction, Constraint):
            # otherwise it already is a Constraint, pass it directly
            compiled_constraints.append((restriction, params_used, None))
        else:
            raise ValueError(f"Restriction {restriction} is neither a string or Constraint {type(restriction)}")

    # return the restrictions and used parameters
    return compiled_constraints
