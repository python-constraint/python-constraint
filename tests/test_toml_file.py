"""Tests for release information."""

from pathlib import Path

import tomli

package_root = Path(".").parent.parent
pyproject_toml_path = package_root / "pyproject.toml"
assert pyproject_toml_path.exists()
with open(pyproject_toml_path, mode="rb") as fp:
    pyproject = tomli.load(fp)
    project = pyproject["project"] if "project" in pyproject else pyproject["tool"]["poetry"]


def test_read():
    """Test whether the contents have been read correctly and the required keys are in place."""
    assert isinstance(pyproject, dict)
    assert "build-system" in pyproject


def test_name():
    """Ensure the name is consistent."""
    assert "name" in project
    assert project["name"] == "python-constraint2"


def test_versioning():
    """Test whether the versioning is PEP440 compliant."""
    from pep440 import is_canonical

    assert "version" in project
    assert is_canonical(project["version"])


def test_authors():
    """Ensure the authors are specified."""
    assert "authors" in project
    assert len(project["authors"]) > 0


def test_license():
    """Ensure the license is set and the file exists."""
    assert "license" in project
    license = project["license"]
    if isinstance(license, dict):
        assert "file" in license
        license = project["license"]["file"]
    assert isinstance(license, str)
    assert len(license) > 0
    if license == "LICENSE":
        assert Path(package_root / license).exists()


def test_readme():
    """Ensure the readme is set and the file exists."""
    assert "readme" in project
    readme = project["readme"]
    if isinstance(readme, dict):
        assert "file" in readme
        readme = project["readme"]["file"]
    assert isinstance(readme, str)
    assert len(readme) > 0
    assert readme[:6] == "README"
    assert Path(package_root / readme).exists()


def test_project_keys():
    """Check whether the expected keys in [project] or [tool.poetry] are present."""
    assert "description" in project
    assert "keywords" in project
    assert "classifiers" in project
    assert "requires-python" in project or "python" in pyproject["tool"]["poetry"]["dependencies"]
