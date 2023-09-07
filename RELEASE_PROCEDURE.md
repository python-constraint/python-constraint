# Release procedure
The following is the release procedure from the main branch to having the package on PyPI. 
Please be aware that access to these functions may be restricted on a user account basis. 

## Check release information

* Ensure supported Python versions in `pyproject.toml` and `noxfile.py` are correct

* Ensure version is bumped in `pyproject.toml` and it is [PEP440-compliant](https://peps.python.org/pep-0440/)

## CHANGELOG

Ensure `CHANGELOG.md` has been updated.

## Tag & Release

Create a [new release](https://github.com/python-constraint/python-constraint/releases/new). 
Add a new tag that matches the version in `pyproject.toml`. 
The release title must start with the exact version as well, followed by a brief description of the changes. 
Ensure that the release description contains all the relevant information, especially if there are breaking changes.
The release description must link to the changelog.  

## Upload to PyPI

Once a new release is created, publishing to PyPI happens automatically via a GitHub action. 
This action builds wheels for manylinux, macOS and Windows on x86. ARM support will be added as soon as it is supported by GitHub. 
Source build is also released, be aware that this requires a C-compiler on the user side.  

## Verify release

Check the status of the [Publish Package](https://github.com/python-constraint/python-constraint/actions/workflows/publish-package.yml) GitHub action. 
Go to https://pypi.python.org/pypi/python-constraint/ and verify that new version is published.
In addition, check in the managing section of PyPI if all wheels and the source distributions are correctly uploaded. 
