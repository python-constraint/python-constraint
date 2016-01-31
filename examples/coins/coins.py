#!/usr/bin/python
#
# 100 coins must sum to $5.00
#
# That's kind of a country-specific problem, since depending on the
# country there are different values for coins. Here is presented
# the solution for a given set.
#
from constraint import Problem, ExactSumConstraint
import sys


def solve():
    problem = Problem()
    total = 5.00
    variables = ("0.01", "0.05", "0.10", "0.50", "1.00")
    values = [float(x) for x in variables]
    for variable, value in zip(variables, values):
        problem.addVariable(variable, range(int(total / value)))
    problem.addConstraint(ExactSumConstraint(total, values), variables)
    problem.addConstraint(ExactSumConstraint(100))
    solutions = problem.getSolutionIter()
    return solutions, variables


def main():
    solutions, variables = solve()
    for i, solution in enumerate(solutions):
        sys.stdout.write("%03d -> " % (i + 1))
        for variable in variables:
            sys.stdout.write("%s:%d " % (variable, solution[variable]))
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
