# NOMAD's Material Processing Plugin

## Getting started
This code is currently under development and can be installed by cloning the repository:
```sh
git clone git@github.com:FAIRmat-NFDI/AreaA-data_modeling_and_schemas.git
cd AreaA-data_modeling_and_schemas
```

And installing the package in editable mode:
```sh
pip install -e ./base_sections/nomad_material_processing_plugin/ --index-url https://gitlab.mpcdf.mpg.de/api/v4/projects/2187/packages/pypi/simple
```

**Note!**
Until we have an official pypi NOMAD release with the plugins functionality. Make
sure to include NOMAD's internal package registry (e.g. via `--index-url`). Follow the instructions
in `requirements.txt`.
