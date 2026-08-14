"""Tests for python-constraint example solvers."""

from examples.crosswords import crosswords
from examples.sudoku import sudoku
from examples.wordmath import seisseisdoze, sendmoremoney, twotwofour
from examples.xsum import xsum


def test_sudoku():
    """Verify that sudoku solver returns valid 9x9 solutions."""
    solutions = sudoku.solve()
    assert len(solutions) >= 1
    sol = solutions[0]
    assert sol[12] == 9
    row1 = [sol[10 + col] for col in range(1, 10)]
    assert sorted(row1) == list(range(1, 10))


def test_sendmoremoney():
    """Verify cryptarithmetic solution for SEND+MORE=MONEY."""
    solutions = sendmoremoney.solve()
    assert len(solutions) == 1
    s = solutions[0]
    assert s["s"] == 9 and s["e"] == 5 and s["m"] == 1 and s["y"] == 2


def test_twotwofour():
    """Verify cryptarithmetic solution for TWO+TWO=FOUR."""
    solutions = twotwofour.solve()
    assert len(solutions) > 0
    for s in solutions:
        two = s["t"] * 100 + s["w"] * 10 + s["o"]
        four = s["f"] * 1000 + s["o"] * 100 + s["u"] * 10 + s["r"]
        assert 2 * two == four


def test_seisseisdoze():
    """Verify cryptarithmetic solution for SEIS+SEIS=DOZE."""
    solutions = seisseisdoze.solve()
    assert len(solutions) > 0
    for s in solutions:
        seis = s["s"] * 1000 + s["e"] * 100 + s["i"] * 10 + s["s"]
        doze = s["d"] * 1000 + s["o"] * 100 + s["z"] * 10 + s["e"]
        assert 2 * seis == doze


def test_xsum():
    """Verify xsum solver where each 5-number row sums to 27."""
    solutions = xsum.solve()
    assert len(solutions) > 0
    for s in solutions:
        row1_sum = s["a"] + s["b"] + s["c"] + s["d"] + s["x"]
        row2_sum = s["e"] + s["f"] + s["g"] + s["h"] + s["x"]
        assert row1_sum == 27
        assert row2_sum == 27


def test_crosswords():
    """Verify crossword puzzle solver execution with sample mask and word list."""
    puzzle = "####\n####\n####\n####"
    words = ["DATA", "CODE", "TEST", "MATH", "BYTE", "DISK", "FILE", "FLOW"]
    solution, matrix = crosswords.solve(puzzle, words)
    assert isinstance(matrix, list)

