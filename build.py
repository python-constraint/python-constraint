"""Cythonize the listed modules to C-extensions.

Based on https://blagovdaryu.hashnode.dev/tremendously-speed-up-python-code-with-cython-and-package-it-with-poetry.
"""

import os
import shutil

from Cython.Build import build_ext, cythonize
from setuptools import Distribution, Extension

# obtain the files to Cythonize
module_name = "constraint"
cython_modules = ["constraints", "domain", "problem", "solvers"]
ext = "py"
extensions = [
    Extension(f"constraint.{module}", [f"constraint/{module}.{ext}"], extra_compile_args=["-O3"])
    for module in cython_modules
]

# Cythonize the files
ext_modules = cythonize(extensions, include_path=[module_name])
dist = Distribution({"ext_modules": ext_modules})
cmd = build_ext(dist)  # bundle into a library file
cmd.ensure_finalized()
cmd.run()

# copy the resulting library bundle into the installed directory
for output in cmd.get_outputs():
    relative_extension = os.path.relpath(output, cmd.build_lib)
    shutil.copyfile(output, relative_extension)


# from pathlib import Path

# import tomli
# from Cython.Build import cythonize
# from setuptools import Extension
# from setuptools.command import build_ext

# cython_modules = ["constraints", "domain", "problem", "solvers"]
# ext = "py"

# # load the pyproject.toml file
# package_root = Path(".").parent.parent
# pyproject_toml_path = package_root / "pyproject.toml"
# assert pyproject_toml_path.exists()
# with open(pyproject_toml_path, mode="rb") as fp:
#     pyproject = tomli.load(fp)


# def build(setup_kwargs):
#     """Used by `tool.poetry` in pyproject.toml to Cythonize."""
#     extensions = [Extension(f"constraint.{module}", [f"constraint/{module}.{ext}"]) for module in cython_modules]
#     # extensions = [f"constraint/{module}.{ext}" for module in cython_modules]
#     # Build
#     setup_kwargs.update(
#         {
#             "ext_modules": cythonize(
#                 extensions,
#                 language_level=3,
#                 compiler_directives={"linetrace": True},
#             ),
#             "cmdclass": {"build_ext": build_ext},
#         }
#     )
