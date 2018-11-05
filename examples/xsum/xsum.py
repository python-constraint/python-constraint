#!/usr/bin/python
#
# Reorganize the following numbers in a way that each line of
# 5 numbers sum to 27.
#
#       1   6
#        2 7
#         3
#        8 4
#       9   5
#
from constraint import Problem, AllDifferentConstraint


def solve():
    problem = Problem()
    problem.addVariables("abcdxefgh", range(1, 10))
    problem.addConstraint(
        lambda a, b, c, d, x: a < b < c < d and a + b + c + d + x == 27, "abcdx"
    )
    problem.addConstraint(
        lambda e, f, g, h, x: e < f < g < h and e + f + g + h + x == 27, "efghx"
    )
    problem.addConstraint(AllDifferentConstraint())
    solutions = problem.getSolutions()
    return solutions


def main():
    solutions = solve()
    print("Found %d solutions!" % len(solutions))
    showSolutions(solutions)


def showSolutions(solutions):
    for solution in solutions:
        print(
            """ %d   %d
  %d %d
   %d
  %d %d
 %d   %d
"""
            % (
                solution["a"],
                solution["e"],
                solution["b"],
                solution["f"],
                solution["x"],
                solution["g"],
                solution["c"],
                solution["h"],
                solution["d"],
            )
        )


if __name__ == "__main__":
    main()
