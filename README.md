![](https://github.com/FAIRmat-NFDI/nomad-material-processing/actions/workflows/publish.yml/badge.svg)
![](https://img.shields.io/pypi/pyversions/nomad-material-processing)
![](https://img.shields.io/pypi/l/nomad-material-processing)
![](https://img.shields.io/pypi/v/nomad-material-processing)

# NOMAD's Material Processing Plugin
This is a plugin for [NOMAD](https://nomad-lab.eu) which contains base sections for
material processing.

## Getting started
This code is currently under development and can be installed by cloning the repository:
```sh
git clone git@github.com:FAIRmat-NFDI/nomad-material-processing.git
cd nomad-material-processing
```

And installing the package in editable mode:
```sh
pip install -e . --index-url https://gitlab.mpcdf.mpg.de/api/v4/projects/2187/packages/pypi/simple
```

**Note!**
Until we have an official pypi NOMAD release with the plugins functionality. Make
sure to include NOMAD's internal package registry (via `--index-url`).
