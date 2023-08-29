import doctest
import constraint.problem as problem
import constraint.domain as domain
import constraint.constraints as constraints
import constraint.solvers as solvers

assert doctest.testmod(problem)[0] == 0
assert doctest.testmod(domain)[0] == 0
assert doctest.testmod(constraints, extraglobs={'Problem': problem.Problem})[0] == 0
assert doctest.testmod(solvers, extraglobs={'Problem': problem.Problem})[0] == 0
