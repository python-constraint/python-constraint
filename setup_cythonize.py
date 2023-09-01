"""Cythonize the listed modules to C-extensions."""

cython_modules = ["constraints", "domain", "problem", "solvers"]
ext = "py"

# from setuptools import Extension
# from setuptools.command.build_py import build_py as _build_py

# class build_py(_build_py):
#     """Used by `tool.setuptools` in pyproject.toml to Cythonize."""

#     def run(self):  # noqa: D102
#         self.run_command("build_ext")
#         return super().run()

#     def initialize_options(self):  # noqa: D102
#         super().initialize_options()
#         extensions = [Extension(f"constraint.{module}", [f"constraint/{module}.{ext}"]) for module in cython_modules]
#         self.distribution.ext_modules = extensions

from pathlib import Path

import tomli
from Cython.Build import cythonize
from setuptools import Extension

# load the pyproject.toml file
package_root = Path(".").parent.parent
pyproject_toml_path = package_root / "pyproject.toml"
assert pyproject_toml_path.exists()
with open(pyproject_toml_path, mode="rb") as fp:
    pyproject = tomli.load(fp)

print("hello")


def build(setup_kwargs):
    """Used by `tool.poetry` in pyproject.toml to Cythonize."""
    extensions = cythonize(
        [Extension(f"constraint.{module}", [f"constraint/{module}.{ext}"]) for module in cython_modules]
    )
    setup_kwargs.update(
        {
            "name": pyproject["project"]["name"],
            # https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#cythonize-arguments
            "ext_modules": extensions,
        }
    )
