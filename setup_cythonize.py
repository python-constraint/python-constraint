"""Cythonize the listed modules to C-extensions."""

from setuptools import Extension
from setuptools.command.build_py import build_py as _build_py

class build_py(_build_py):
    """Used by `tool.setuptools` in pyproject.toml to Cythonize."""

    def run(self):  # noqa: D102
        self.run_command("build_ext")
        return super().run()

    def initialize_options(self):  # noqa: D102
        super().initialize_options()
        cython_modules = ['constraints', 'domain', 'problem', 'solvers']
        ext = "py"
        extensions = [Extension(f"constraint.{module}", [f"constraint/{module}.{ext}"]) for module in cython_modules]
        self.distribution.ext_modules = extensions
