#!/usr/bin/python
from distutils.core import setup
import os

if os.path.isfile("MANIFEST"):
    os.unlink("MANIFEST")

setup(name="python-constraint",
      version = "1.2",
      description = "Python module for handling Constraint Solving Problems",
      author = "Gustavo Niemeyer",
      author_email = "gustavo@niemeyer.net",
      url = "http://labix.org/python-constraint",
      license = "Simplified BSD",
      long_description =
"""
python-constraint is a module implementing support for handling CSPs
(Constraint Solving Problems) over finite domains.
""",
      py_modules = ["constraint"],
      )
