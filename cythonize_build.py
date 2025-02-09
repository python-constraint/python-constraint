"""Cythonize the listed modules to C-extensions.

Based on https://blagovdaryu.hashnode.dev/tremendously-speed-up-python-code-with-cython-and-package-it-with-poetry.
"""

import os
import shutil
from subprocess import CalledProcessError
from warnings import warn

from Cython.Build import build_ext, cythonize
from setuptools import Distribution, Extension

# obtain the files to Cythonize
module_name = "constraint"
cython_modules = ["constraints", "domain", "problem", "solvers", "parser"]
ext = "py"
extensions = [
    Extension(f"constraint.{module}", [f"constraint/{module}.{ext}"], extra_compile_args=["-O3"])
    for module in cython_modules
]

# Cythonize the files
ext_modules = cythonize(extensions, include_path=[module_name], language_level=3, force=True)
dist = Distribution({"ext_modules": ext_modules})
try:
    cmd = build_ext(dist)  # bundle into a library file
    cmd.ensure_finalized()
    cmd.run()
except CalledProcessError:
    warn(RuntimeWarning("System does not have a C-compiler usable for `build_ext` installed, using slower Python code"))

# copy the resulting library bundle into the installed directory
for output in cmd.get_outputs():
    relative_extension = os.path.relpath(output, cmd.build_lib)
    shutil.copyfile(output, relative_extension)
