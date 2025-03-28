# Change Log

## Python Constraint

All notable changes to this code base will be documented in this file, for every released major and minor version. For all versions, see [releases](https://github.com/python-constraint/python-constraint/releases). 

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
