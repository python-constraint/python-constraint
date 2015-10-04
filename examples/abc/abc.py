#!/usr/bin/python
#
# What's the minimum value for:
#
#        ABC
#      -------
#       A+B+C
#
# From http://www.umassd.edu/mathcontest/abc.cfm
#
from constraint import *

def main():
    problem = Problem()
    problem.addVariables("abc", range(1,10))
    problem.getSolutions()
    minvalue = 999/(9*3)
    minsolution = {}
    for solution in problem.getSolutions():
        a = solution["a"]
        b = solution["b"]
        c = solution["c"]
        value = (a*100+b*10+c)/(a+b+c)
        if value < minvalue:
            minsolution = solution
    print minvalue
    print minsolution

if __name__ == "__main__":
    main()
