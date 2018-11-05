#!/usr/bin/python
#
# Assign equal values to equal letters, and different values to
# different letters, in a way that satisfies the following sum:
#
#    SEND
#  + MORE
#  ------
#   MONEY
#
from constraint import Problem, NotInSetConstraint, AllDifferentConstraint


def solve():
    problem = Problem()
    problem.addVariables("sendmory", range(10))
    problem.addConstraint(lambda d, e, y: (d + e) % 10 == y, "dey")
    problem.addConstraint(
        lambda n, d, r, e, y: (n * 10 + d + r * 10 + e) % 100 == e * 10 + y, "ndrey"
    )
    problem.addConstraint(
        lambda e, n, d, o, r, y: (e * 100 + n * 10 + d + o * 100 + r * 10 + e) % 1000 ==
        n * 100 + e * 10 + y,
        "endory",
    )
    problem.addConstraint(
        lambda s, e, n, d, m, o, r, y: 1000 * s +
        100 * e +
        10 * n +
        d +
        1000 * m +
        100 * o +
        10 * r +
        e ==
        10000 * m + 1000 * o + 100 * n + 10 * e + y,
        "sendmory",
    )
    problem.addConstraint(NotInSetConstraint([0]), "sm")
    problem.addConstraint(AllDifferentConstraint())
    solutions = problem.getSolutions()
    return solutions


def main():
    solutions = solve()
    print("SEND+MORE=MONEY")
    for s in solutions:
        print(
            "%(s)d%(e)d%(n)d%(d)d+"
            "%(m)d%(o)d%(r)d%(e)d="
            "%(m)d%(o)d%(n)d%(e)d%(y)d" % s
        )


if __name__ == "__main__":
    main()
