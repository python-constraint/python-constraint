#!/usr/bin/python
#
# Assign equal values to equal letters, and different values to
# different letters, in a way that satisfies the following sum:
#
#    SEIS
#  + SEIS
#  ------
#    DOZE
#
from constraint import Problem, AllDifferentConstraint


def solve():
    problem = Problem()
    problem.addVariables("seidoz", range(10))
    problem.addConstraint(lambda s, e: (2 * s) % 10 == e, "se")
    problem.addConstraint(
        lambda i, s, z, e: ((10 * 2 * i) + (2 * s)) % 100 == z * 10 + e, "isze"
    )
    problem.addConstraint(
        lambda s, e, i, d, o, z: 2 * (s * 1000 + e * 100 + i * 10 + s) ==
        d * 1000 + o * 100 + z * 10 + e,
        "seidoz",
    )
    problem.addConstraint(lambda s: s != 0, "s")
    problem.addConstraint(lambda d: d != 0, "d")
    problem.addConstraint(AllDifferentConstraint())
    solutions = problem.getSolutions()
    return solutions


def main():
    solutions = solve()
    print("SEIS+SEIS=DOZE")
    for s in solutions:
        print("%(s)d%(e)d%(i)d%(s)s+%(s)d%(e)d%(i)d%(s)d=" "%(d)d%(o)d%(z)d%(e)d") % s


if __name__ == "__main__":
    main()
