#!/usr/bin/python
#
# http://home.chello.no/~dudley/
#
from constraint import Problem, AllDifferentConstraint, SomeInSetConstraint
import sys

STUDENTDESKS = [
    [0, 1, 0, 0, 0, 0],
    [0, 2, 3, 4, 5, 6],
    [0, 7, 8, 9, 10, 0],
    [0, 11, 12, 13, 14, 0],
    [15, 16, 17, 18, 19, 0],
    [0, 0, 0, 0, 20, 0],
]


def solve():
    problem = Problem()
    problem.addVariables(range(1, 21), ["A", "B", "C", "D", "E"])
    problem.addConstraint(SomeInSetConstraint(["A"], 4, True))
    problem.addConstraint(SomeInSetConstraint(["B"], 4, True))
    problem.addConstraint(SomeInSetConstraint(["C"], 4, True))
    problem.addConstraint(SomeInSetConstraint(["D"], 4, True))
    problem.addConstraint(SomeInSetConstraint(["E"], 4, True))
    for row in range(len(STUDENTDESKS) - 1):
        for col in range(len(STUDENTDESKS[row]) - 1):
            lst = [
                STUDENTDESKS[row][col],
                STUDENTDESKS[row][col + 1],
                STUDENTDESKS[row + 1][col],
                STUDENTDESKS[row + 1][col + 1],
            ]
            lst = [x for x in lst if x]
            problem.addConstraint(AllDifferentConstraint(), lst)
    solutions = problem.getSolution()
    return solutions


def main():
    solutions = solve()
    showSolution(solutions)


def showSolution(solution):
    for row in range(len(STUDENTDESKS)):
        for col in range(len(STUDENTDESKS[row])):
            id = STUDENTDESKS[row][col]
            sys.stdout.write(" %s" % (id and solution[id] or " "))
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
