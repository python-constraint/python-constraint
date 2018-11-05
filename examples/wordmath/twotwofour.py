#!/usr/bin/python
#
# Assign equal values to equal letters, and different values to
# different letters, in a way that satisfies the following sum:
#
#    TWO
#  + TWO
#  -----
#   FOUR
#
from constraint import Problem, AllDifferentConstraint, NotInSetConstraint


def solve():
    problem = Problem()
    problem.addVariables("twofur", range(10))
    problem.addConstraint(lambda o, r: (2 * o) % 10 == r, "or")
    problem.addConstraint(
        lambda w, o, u, r: ((10 * 2 * w) + (2 * o)) % 100 == u * 10 + r, "wour"
    )
    problem.addConstraint(
        lambda t, w, o, f, u, r: 2 * (t * 100 + w * 10 + o) ==
        f * 1000 + o * 100 + u * 10 + r,
        "twofur",
    )
    problem.addConstraint(NotInSetConstraint([0]), "ft")
    problem.addConstraint(AllDifferentConstraint())
    solutions = problem.getSolutions()
    return solutions


def main():
    solutions = solve()
    print("TWO+TWO=FOUR")
    for s in solutions:
        print("%(t)d%(w)d%(o)d+%(t)d%(w)d%(o)d=%(f)d%(o)d%(u)d%(r)d" % s)


if __name__ == "__main__":
    main()
