from constraint import *

from examples.abc import abc
from examples.coins import coins
from examples.crosswords import crosswords
from examples.einstein import einstein
from examples.queens import queens
from examples.rooks import rooks
from examples.studentdesks import studentdesks
from examples.sudoku import sudoku
from examples.wordmath import (seisseisdoze, sendmoremoney, twotwofour)
from examples.xsum import xsum

def test_abc():
    solutions = abc.solve()
    minvalue, minsolution = solutions
    assert minvalue==37
    assert minsolution=={'a': 1, 'c': 2, 'b': 1}

def test_coins():
    solutions = coins.solve()
    assert len(solutions)==2

def test_einstein():
    solutions = einstein.solve()
    expected_solutions = [
        {
            'nationality2': 'dane',
            'nationality3': 'brit',
            'nationality1': 'norwegian',
            'nationality4': 'german',
            'nationality5': 'swede',
            'color1': 'yellow',
            'color3': 'red',
            'color2': 'blue',
            'color5': 'white',
            'color4': 'green',
            'drink4': 'coffee',
            'drink5': 'beer',
            'drink1': 'water',
            'drink2': 'tea',
            'drink3': 'milk',
            'smoke5': 'bluemaster',
            'smoke4': 'prince',
            'smoke3': 'pallmall',
            'smoke2': 'blends',
            'smoke1': 'dunhill',
            'pet5': 'dogs',
            'pet4': 'fish',
            'pet1': 'cats',
            'pet3': 'birds',
            'pet2': 'horses'
        }
    ]
    assert solutions == expected_solutions

def test_rooks():
    size = 8
    solutions = rooks.solve(size)
    assert len(solutions) == rooks.factorial(size)
