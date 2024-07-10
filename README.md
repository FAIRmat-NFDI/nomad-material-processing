# nomad-synthesis-plugin

plugin for synthesis data for Huyana Terraschke's workgroup at CAU Kiel

----

This `nomad`_ plugin was generated with `Cookiecutter`_ along with `@nomad`_'s `cookiecutter-nomad-plugin`_ template.


### Install

You should create a virtual environment. You will need the `nomad-lab` package (and `pytest`).
We recommend using Python 3.9.

```sh
python3 -m venv .pyenv
source .pyenv/bin/activate
pip install --upgrade pip
pip install -e '.[dev]' --index-url https://gitlab.mpcdf.mpg.de/api/v4/projects/2187/packages/pypi/simple
```

**Note!**
Until we have an official pypi NOMAD release with the plugins functionality. Make
sure to include NOMAD's internal package registry (e.g. via `--index-url`).

### Testing

You can run automated tests with `pytest`:

```sh
pytest -svx tests
```

### Run linting

```sh
ruff check .
```

### Run auto-formatting

This is entirely optional. To add this as a check in github actions pipeline, uncomment the `ruff-formatting` step in `./github/workflows/actions.yaml`.

```sh
ruff format .
```

### Developing a NOMAD plugin

Follow the [guide](https://nomad-lab.eu/prod/v1/staging/docs/howto/plugins/plugins.html) on how to develop NOMAD plugins.

### Build the python package

The `pyproject.toml` file contains everything that is necessary to turn the project
into a pip installable python package. Run the python build tool to create a package distribution:

```
pip install build
python -m build --sdist
```

You can install the package with pip:

```
pip install dist/nomad-synthesis-plugin-0.1.0
```

Read more about python packages, `pyproject.toml`, and how to upload packages to PyPI
on the [PyPI documentation](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

### Documentation on Github pages

To deploy documentation on Github pages, make sure to [enable GitHub pages via the repo settings](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-from-a-branch). 

To view the documentation locally, install the documentation related packages using:

```sh
pip install -r requirements_docs.txt
```

Run the documentation server:
```sh
mkdocs serve
```

### Template update

We use cruft to update the project based on template changes. A `cruft-update.yml` is included in Github workflows to automatically check for updates and create pull requests to apply updates. Follow the [instructions](https://github.blog/changelog/2022-05-03-github-actions-prevent-github-actions-from-creating-and-approving-pull-requests/) on how to enable Github Actions to create pull requests. 

To run the check for updates locally, follow the instructions on [`cruft` website](https://cruft.github.io/cruft/#updating-a-project).

### License
Distributed under the terms of the `MIT`_ license, "nomad-synthesis-plugin" is free and open source software
