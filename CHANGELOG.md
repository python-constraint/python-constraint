# Change Log

## Python Contraint

All notable changes to this code base will be documented in this file,
in every released version.

### Version 2.0.0

- Released: TBD
- Issues/Enhancements:
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
  - Achieved and requires test coverage of at least 65%
  - Added `nox` for testing against all supported Python versions 
  - Added `ruff` for codestyle testing
  - Moved the documentation to GitHub Pages
  - Moved test & publishing automation to GitHub Actions
  - Switched dependency & build system to Poetry
  - Dropped Python 3.4, 3.5, 3.6, 3.7, 3.8 support

### Version 1.4.0

- Released: 2018-11-05
- Issues/Enhancements:
  - Add tests around `SomeNotInSetConstraint.`
  - Minor `README` fixes
  - Fix `dict.keys()` issue with Python 3 and add some unit tests
  - Drop Python 3.3 support

### Version 1.3.1

- Released: 2017-03-31
- Issues/Enhancements:
  - Better `README` rendering (using reStructuredText)

### Version 1.3

- Released: 2017-03-31
- Maintainer: Sébastien Celles <s.celles@gmail.com>
- Issues/Enhancements:
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
