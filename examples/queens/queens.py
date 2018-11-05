#!/usr/bin/python
#
# http://mathworld.wolfram.com/QueensProblem.html
#
from constraint import Problem
import sys


def solve():
    problem = Problem()
    size = 8
    cols = range(size)
    rows = range(size)
    problem.addVariables(cols, rows)
    for col1 in cols:
        for col2 in cols:
            if col1 < col2:
                problem.addConstraint(
                    lambda row1, row2, col1=col1,
                    col2=col2: abs(row1 - row2) !=
                    abs(col1 - col2) and row1 != row2,
                    (col1, col2),
                )
    solutions = problem.getSolutions()
    return solutions, size


def showSolution(solution, size):
    sys.stdout.write("   %s \n" % ("-" * ((size * 4) - 1)))
    for i in range(size):
        sys.stdout.write("  |")
        for j in range(size):
            if solution[j] == i:
                sys.stdout.write(" %d |" % j)
            else:
                sys.stdout.write("   |")
        sys.stdout.write("\n")
        if i != size - 1:
            sys.stdout.write("  |%s|\n" % ("-" * ((size * 4) - 1)))
    sys.stdout.write("   %s \n" % ("-" * ((size * 4) - 1)))


def main(show=False):
    solutions, size = solve()
    print("Found %d solution(s)!" % len(solutions))
    if show:
        for solution in solutions:
            showSolution(solution, size)


if __name__ == "__main__":
    show = False
    if len(sys.argv) == 2 and sys.argv[1] == "-s":
        show = True
    elif len(sys.argv) != 1:
        sys.exit("Usage: queens.py [-s]")
    main(show)
