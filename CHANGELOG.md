# Python Constraint Changelog

All notable changes to this code base will be documented in this file, for every released major and minor version. For all versions, see [releases](https://github.com/python-constraint/python-constraint/releases). 

### Version 2.3.0

- Released: 2025-06-17
- Issues / Enhancements:
  - Python Constraint now has an entirely new type of built-in constraints, allowing comparisons with variables on both sides to be evaluated much more efficiently.
  - Constraint rewriting has been extended to include minus and division operators.
  - Rewriting of restrictions with less-than or greater-than operators now supports floats as well.
  - Tests have been extended and amended to reflect changes introduced.
  - Documentation has been extended and amended to reflect changes introduced.
  - Various minor bugs have been resolved.

### Version 2.2.0

- Released: 2025-03-25
- Issues / Enhancements:
  - Automatic performance benchmarking and validation with real-world cases and automatic reporting (see [#93](https://github.com/python-constraint/python-constraint/pull/93)).
  - Preparations for free-threading (no GIL) capabilities (see [#94](https://github.com/python-constraint/python-constraint/pull/94)).
  - Removed NumPy dependency in micro benchmarks, updated dependencies, and optimized test interfaces.
  - Changed development status from Beta to Production / Stable.

### Version 2.1.0

- Released: 2025-02-11
- Issues / Enhancements (see [#91](https://github.com/python-constraint/python-constraint/pull/91) for more details):
  - Implemented a new string format for constraints, that is automatically parsed to constraint types (currently in beta, please report issues)
  - Implemented a new `ParallelSolver` with both Thread and Process mode (currently experimental)
  - Added Python 3.13 and experimental 3.14 support

### Version 2.0.0

- Released: 2025-01-29
- Maintainer: Floris-Jan Willemsen <fjwillemsen97@gmail.com>
- Issues / Enhancements:
  - Cythonized the package
  - Added the `OptimizedBacktracking` solver based on [issue #62](https://github.com/python-constraint/python-constraint/issues/62)
  - Added type-hints to improve Cythonization
  - Added the MaxProd and MinProd constraints
  - Improved pre-processing for the MaxSum constraint
  - Optimized the Function constraint
  - Added `getSolutionsOrderedList` and `getSolutionsAsListDict` functions for efficient result shaping
  - Overall optimization of common bottlenecks
  - Split the codebase into multiple files for convenience
  - Switched from `setup.py` to `pyproject.toml`
  - Added `nox` for testing against all supported Python versions 
  - Added `ruff` for codestyle testing
  - Achieved and requires test coverage of at least 80%
  - Moved the documentation to GitHub Pages
  - Moved test & publishing automation to GitHub Actions
  - Switched dependency & build system to Poetry
  - Dropped Python 3.4, 3.5, 3.6, 3.7, 3.8 support

### Version 1.4.0

- Released: 2018-11-05
- Issues / Enhancements:
  - Add tests around `SomeNotInSetConstraint.`
  - Minor `README` fixes
  - Fix `dict.keys()` issue with Python 3 and add some unit tests
  - Drop Python 3.3 support

### Version 1.3.1

- Released: 2017-03-31
- Issues / Enhancements:
  - Better `README` rendering (using reStructuredText)

### Version 1.3

- Released: 2017-03-31
- Maintainer: Sébastien Celles <s.celles@gmail.com>
- Issues / Enhancements:
  - Original code forked from https://labix.org/python-constraint
  - Publish on Github
  - Python 2 / 3 support
  - Remove Python 2.6 support
  - Unit tests and continuous integration
  - Create a registered pip instalable package
  - PEP8

### Initial development

- Author: Gustavo Biemeyer <gustavo@niemeyer.net>
- URL: https://labix.org/python-constraint
