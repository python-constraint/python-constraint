# Release procedue

* Ensure supported Python versions in `setup.py` and `.travis.yml` are corrects 

* Ensure `python-constraint` version is up to date in `version.py`

* Ensure `CHANGELOG.md` have been updated

* Tag commit and push to github

using Github website

Go to https://github.com/python-constraint/python-constraint/releases/new
tag: vx.x.x

or using cli

```bash
git tag -a x.x.x -m 'Version x.x.x'
git push python-constraint master --tags
```

* Upload to PyPI

Ensure a `~/.pypirc` exists

```
[distutils] # this tells distutils what package indexes you can push to
index-servers = pypi
    pypi # the live PyPI
    pypitest # test PyPI

[pypi]
repository:http://pypi.python.org/pypi
username:scls
password:**********
```

Upload

```
git clean -xfd
python setup.py register sdist bdist_wheel --universal
python setup.py sdist bdist_wheel upload
```

* Verify on PyPI

Go to https://pypi.python.org/pypi/python-constraint/

Verify that new version is published.
