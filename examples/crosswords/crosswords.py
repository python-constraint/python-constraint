#!/usr/bin/python
from constraint import Problem, AllDifferentConstraint
import random
import sys

MINLEN = 3


def main(puzzle, lines):
    puzzle = puzzle.rstrip().splitlines()
    while puzzle and not puzzle[0]:
        del puzzle[0]

    # Extract horizontal words
    horizontal = []
    word = []
    predefined = {}
    for row in range(len(puzzle)):
        for col in range(len(puzzle[row])):
            char = puzzle[row][col]
            if not char.isspace():
                word.append((row, col))
                if char != "#":
                    predefined[row, col] = char
            elif word:
                if len(word) > MINLEN:
                    horizontal.append(word[:])
                del word[:]
        if word:
            if len(word) > MINLEN:
                horizontal.append(word[:])
            del word[:]

    # Extract vertical words
    vertical = []
    validcol = True
    col = 0
    while validcol:
        validcol = False
        for row in range(len(puzzle)):
            if col >= len(puzzle[row]):
                if word:
                    if len(word) > MINLEN:
                        vertical.append(word[:])
                    del word[:]
            else:
                validcol = True
                char = puzzle[row][col]
                if not char.isspace():
                    word.append((row, col))
                    if char != "#":
                        predefined[row, col] = char
                elif word:
                    if len(word) > MINLEN:
                        vertical.append(word[:])
                    del word[:]
        if word:
            if len(word) > MINLEN:
                vertical.append(word[:])
            del word[:]
        col += 1

    # hnames = ["h%d" % i for i in range(len(horizontal))]
    # vnames = ["v%d" % i for i in range(len(vertical))]

    # problem = Problem(MinConflictsSolver())
    problem = Problem()

    for hi, hword in enumerate(horizontal):
        for vi, vword in enumerate(vertical):
            for hchar in hword:
                if hchar in vword:
                    hci = hword.index(hchar)
                    vci = vword.index(hchar)
                    problem.addConstraint(
                        lambda hw, vw, hci=hci, vci=vci: hw[hci] == vw[vci],
                        ("h%d" % hi, "v%d" % vi),
                    )

    for char, letter in predefined.items():
        for hi, hword in enumerate(horizontal):
            if char in hword:
                hci = hword.index(char)
                problem.addConstraint(
                    lambda hw, hci=hci, letter=letter: hw[hci] == letter, ("h%d" % hi,)
                )
        for vi, vword in enumerate(vertical):
            if char in vword:
                vci = vword.index(char)
                problem.addConstraint(
                    lambda vw, vci=vci, letter=letter: vw[vci] == letter, ("v%d" % vi,)
                )

    wordsbylen = {}
    for hword in horizontal:
        wordsbylen[len(hword)] = []
    for vword in vertical:
        wordsbylen[len(vword)] = []

    for line in lines:
        line = line.strip()
        ll = len(line)
        if ll in wordsbylen:
            wordsbylen[ll].append(line.upper())

    for hi, hword in enumerate(horizontal):
        words = wordsbylen[len(hword)]
        random.shuffle(words)
        problem.addVariable("h%d" % hi, words)
    for vi, vword in enumerate(vertical):
        words = wordsbylen[len(vword)]
        random.shuffle(words)
        problem.addVariable("v%d" % vi, words)

    problem.addConstraint(AllDifferentConstraint())

    solution = problem.getSolution()
    if not solution:
        print("No solution found!")

    maxcol = 0
    maxrow = 0
    for hword in horizontal:
        for row, col in hword:
            if row > maxrow:
                maxrow = row
            if col > maxcol:
                maxcol = col
    for vword in vertical:
        for row, col in vword:
            if row > maxrow:
                maxrow = row
            if col > maxcol:
                maxcol = col

    matrix = []
    for row in range(maxrow + 1):
        matrix.append([" "] * (maxcol + 1))

    for variable in solution:
        if variable[0] == "v":
            word = vertical[int(variable[1:])]
        else:
            word = horizontal[int(variable[1:])]
        for (row, col), char in zip(word, solution[variable]):
            matrix[row][col] = char

    for row in range(maxrow + 1):
        for col in range(maxcol + 1):
            sys.stdout.write(matrix[row][col])
        sys.stdout.write("\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: crosswords.py <maskfile> <wordsfile>")
    main(open(sys.argv[1]).read(), open(sys.argv[2]))
