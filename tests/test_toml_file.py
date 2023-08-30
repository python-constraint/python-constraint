"""Tests for release information."""

from pathlib import Path

import tomli

package_root = Path('.').parent.parent
pyproject_toml_path = package_root / "pyproject.toml"
assert pyproject_toml_path.exists()
with open(pyproject_toml_path, mode="rb") as fp:
    pyproject = tomli.load(fp)


def test_read():
    """Test whether the contents have been read correctly and the required keys are in place."""
    assert isinstance(pyproject, dict)
    assert "build-system" in pyproject
    assert "project" in pyproject


def test_name():
    """Ensure the name is consistent."""
    assert "name" in pyproject["project"]
    assert pyproject["project"]["name"] == "python-constraint"


def test_versioning():
    """Test whether the versioning is PEP440 compliant."""
    from pep440 import is_canonical

    assert "version" in pyproject["project"]
    assert is_canonical(pyproject["project"]["version"])


def test_authors():
    """Ensure the authors are specified."""
    assert "authors" in pyproject["project"]
    assert len(pyproject["project"]["authors"]) > 0


def test_license():
    """Ensure the license is set and the file exists."""
    assert "license" in pyproject["project"]
    license = pyproject["project"]["license"]
    assert len(license) > 0
    assert license["file"] == "LICENSE"
    assert Path(package_root / "LICENSE").exists()


def test_readme():
    """Ensure the readme is set and the file exists."""
    assert "readme" in pyproject["project"]
    readme = pyproject["project"]["readme"]["file"]
    assert len(readme) > 0
    assert Path(package_root / readme).exists()


def test_project_keys():
    """Check whether the expected keys in [project] are present."""
    project = pyproject["project"]
    assert "description" in project
    assert "keywords" in project
    assert "classifiers" in project
    assert "requires-python" in project
