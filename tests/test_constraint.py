import constraint

from examples.abc import abc
from examples.coins import coins

# from examples.crosswords import crosswords
from examples.einstein import einstein
from examples.queens import queens
from examples.rooks import rooks
from examples.studentdesks import studentdesks

# from examples.sudoku import sudoku
# from examples.wordmath import (seisseisdoze, sendmoremoney, twotwofour)
# from examples.xsum import xsum

import constraint.compat as compat


def test_abc():
    solutions = abc.solve()
    minvalue, minsolution = solutions
    assert abs(minvalue - 10.473684210526315) < 0.00001
    assert minsolution == {"a": 1, "b": 9, "c": 9}


def test_coins():
    solutions = coins.solve()
    assert len(solutions) == 2


def test_einstein():
    solutions = einstein.solve()
    expected_solutions = [
        {
            "nationality2": "dane",
            "nationality3": "brit",
            "nationality1": "norwegian",
            "nationality4": "german",
            "nationality5": "swede",
            "color1": "yellow",
            "color3": "red",
            "color2": "blue",
            "color5": "white",
            "color4": "green",
            "drink4": "coffee",
            "drink5": "beer",
            "drink1": "water",
            "drink2": "tea",
            "drink3": "milk",
            "smoke5": "bluemaster",
            "smoke4": "prince",
            "smoke3": "pallmall",
            "smoke2": "blends",
            "smoke1": "dunhill",
            "pet5": "dogs",
            "pet4": "fish",
            "pet1": "cats",
            "pet3": "birds",
            "pet2": "horses",
        }
    ]
    assert solutions == expected_solutions


def test_queens():
    solutions, size = queens.solve()
    assert size == 8
    for solution in solutions:
        queens.showSolution(solution, size)


def test_rooks():
    size = 8
    solutions = rooks.solve(size)
    assert len(solutions) == rooks.factorial(size)


def test_studentdesks():
    solutions = studentdesks.solve()
    expected_solutions = {
        1: "A",
        2: "E",
        3: "D",
        4: "E",
        5: "D",
        6: "A",
        7: "C",
        8: "B",
        9: "C",
        10: "B",
        11: "E",
        12: "D",
        13: "E",
        14: "D",
        15: "A",
        16: "C",
        17: "B",
        18: "C",
        19: "B",
        20: "A",
    }
    assert solutions == expected_solutions


def test_constraint_without_variables():
    problem = constraint.Problem()
    problem.addVariable("a", [1, 2, 3])
    problem.addConstraint(lambda a: a * 2 == 6)
    solutions = problem.getSolutions()
    assert solutions == [{"a": 3}]


def test_version():
    assert isinstance(constraint.__version__, compat.string_types)
