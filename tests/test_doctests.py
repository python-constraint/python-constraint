import doctest
import constraint.problem as problem
import constraint.domain as domain
import constraint.constraints as constraints
import constraint.solvers as solvers

import unittest
import re
import textwrap

assert doctest.testmod(problem)[0] == 0
assert doctest.testmod(domain)[0] == 0
assert doctest.testmod(constraints, extraglobs={'Problem': problem.Problem})[0] == 0
assert doctest.testmod(solvers, extraglobs={'Problem': problem.Problem})[0] == 0

def extract_python_code_blocks(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Matches '.. code-block:: python' followed by any amount of blank space,
    # then captures all subsequent lines that are indented by 4+ spaces
    pattern = re.compile(
        r"""
        ^[ \t]*\.\. \s*code-block::\s*python   # The directive
        (?:\r?\n[ \t]*)+                       # One or more blank lines (maybe just newline)
        (
            (?:
                (^[ \t]{4,}.*(?:\r?\n|$))      # Lines indented ≥4 spaces
                |
                (^\s*$)                        # Or completely blank lines
            )+
        )
        """,
        re.MULTILINE | re.VERBOSE
    )

    matches = pattern.findall(content)

    # # Dedent each block (remove 4-space indent)
    # blocks = [textwrap.dedent(block) for block in matches]

    # Each match is a tuple due to multiple capture groups — flatten and dedent
    blocks = []
    for match in matches:
        block_lines = match[0]
        blocks.append(textwrap.dedent(block_lines))

    return "\n\n".join(blocks)

class TestReadmeDoctests(unittest.TestCase):
    def test_readme_code_blocks(self):
        code = extract_python_code_blocks("README.rst")
        parser = doctest.DocTestParser()
        globs = {}
        test = parser.get_doctest(
            code,
            globs=globs,
            name="README.rst",
            filename="README.rst",
            lineno=0
        )
        runner = doctest.DocTestRunner(optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
        runner.run(test)
        failures, _ = runner.summarize()
        self.assertEqual(failures, 0)
