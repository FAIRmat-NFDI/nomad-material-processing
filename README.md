![](https://github.com/FAIRmat-NFDI/nomad-material-processing/actions/workflows/publish.yml/badge.svg)
![](https://img.shields.io/pypi/pyversions/nomad-material-processing)
![](https://img.shields.io/pypi/l/nomad-material-processing)
![](https://img.shields.io/pypi/v/nomad-material-processing)

# NOMAD's Material Processing Plugin
This is a plugin for [NOMAD](https://nomad-lab.eu) which contains base sections for
material processing.

## Getting started
`nomad-material-processing` can be installed from PyPI using `pip`. 

> [!WARNING] 
> Unfortunately, the current plugin mechanism is not supported by the latest nomad-lab version on PyPI and therefore an index url pointing to the NOMAD Gitlab registry needs to be added.

```sh
pip install nomad-material-processing --index-url https://gitlab.mpcdf.mpg.de/api/v4/projects/2187/packages/pypi/simple
```

### Setting up your OASIS
Read the [NOMAD plugin documentation](https://nomad-lab.eu/prod/v1/staging/docs/plugins/plugins.html#add-a-plugin-to-your-nomad) for all details on how to deploy the plugin on your NOMAD instance.

You don't need to modify the ```nomad.yaml``` configuration file of your NOMAD instance, beacuse the package is pip installed and all the available modules (entry points) are loaded.
To include, instead, only some of the entry points, you need to specify them in the ```include``` section of the ```nomad.yaml```. In the following lines, a list of all the available entry points:

```yaml
plugins:
  include:
    - "nomad_material_processing:schema"
    - "nomad_material_processing.solution:schema"
    - "nomad_material_processing.vapor_deposition.cvd:schema"
    - "nomad_material_processing.vapor_deposition.pvd:schema"
    - "nomad_material_processing.vapor_deposition.pvd:mbe_schema"
    - "nomad_material_processing.vapor_deposition.pvd:pld_schema"
    - "nomad_material_processing.vapor_deposition.pvd:sputtering_schema"
    - "nomad_material_processing.vapor_deposition.pvd:thermal_schema"
 ```

### Development
This code is currently under development and for installing and contributing you should clone the repository:
```sh
git clone git@github.com:FAIRmat-NFDI/nomad-material-processing.git
cd nomad-material-processing
```

And install the package in editable mode:
```sh
pip install -e .[dev] --index-url https://gitlab.mpcdf.mpg.de/api/v4/projects/2187/packages/pypi/simple
```
