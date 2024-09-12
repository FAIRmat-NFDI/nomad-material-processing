## NOMAD Material Processing: a Community plugin

The NOMAD Material Processing Plugin contains schemas for different synthesis methods.
An overview of the package structure is shown below.

### Technical description

There are some technical aspects to understand the Python package built for this plugin, they are not crucial for the data model understanding itself:

- It is structured according to the [src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/).
- It is a [regular Python package](https://docs.python.org/3/reference/import.html#regular-packages), i. e., the structure is defined by the presence of `__init__.py` files. Each of these files contains one or multiple [entry points](https://nomad-lab.eu/prod/v1/staging/docs/howto/plugins/plugins.html#plugin-entry-points). These are used to load a portion of the code within your NOMAD through a specific section in the `nomad.yaml` file.
- It is pip installable. The `project.toml` file defines what will be installed, the dependencies, further details. The **entry points** included are listed in this file.

```text
nomad-material-processing/
├── docs
├── pyproject.toml
├── README.md
├── src
│   └── nomad_material_processing
│       ├── __init__.py
│       ├── utils.py
│       ├── general.py
│       ├── vapor_deposition
│       │   ├── __init__.py
│       │   ├── general.py
│       │   ├── cvd
│       │   │   ├── __init__.py
│       │   │   ├── general.py
│       │   │   └── movpe.py
│       │   └── pvd
│       │       ├── __init__.py
│       │       ├── general.py
│       │       ├── mbe.py
│       │       ├── pld.py
│       │       ├── sputtering.py
│       │       └── thermal.py
│       └── solution
│           ├── __init__.py
│           ├── general.py
│           └── utils.py
└── tests
```

### Data model description

Each method has a dedicated [module](https://docs.python.org/3/tutorial/modules.html), i. e., a python file.

#### nomad_material_processing.general

A very general module containing several categories of classes:

- an abstract process class `SampleDeposition` that is inherited in the specific processes such as MOVPE, MBE, PLD, etc.
- `Substrate` and `CrystallineSubstrate` entities, the support used in `SampleDeposition` activities.
- `ThinFilm` entity, usually created during `SampleDeposition` activities.
- `ThinFilmStack` in case of processes producing multilayer samples. This class also contains a reference to the `Substrate`.
- `Geometry` and it's subclasses, defining the commonly found macroscopic shapes of a sample. It is a subsection composed within the `Substrate`. They include `Parallelepiped`, `SquareCuboid`, `RectangleCuboid`, `TruncatedCone`, `Cylinder`, `CylinderSector`, `IrregularParallelSurfaces`.
- `Miscut` another subsection of  `Substrate` to specify the miscut of the orientation of the surface in terms of angular deviation toward crystallographic directions.
- `CrystalProperties` and `ElectronicProperties`, found as subsection of sample entities that need these parameters.
- simple activities performed on samples: `Etching`, `Annealing`, `Cleaning`. They also include a `Recipe` that can be referenced inside to avoid repetition for routinary tasks.


#### nomad_material_processing.vapor_deposition.general



#### nomad_material_processing.vapor_deposition.cvd
#### nomad_material_processing.vapor_deposition.cvd.general
#### nomad_material_processing.vapor_deposition.cvd.movpe
#### nomad_material_processing.vapor_deposition.pvd
#### nomad_material_processing.vapor_deposition.pvd.general
#### nomad_material_processing.vapor_deposition.pvd.mbe
#### nomad_material_processing.vapor_deposition.pvd.pld
#### nomad_material_processing.vapor_deposition.pvd.sputtering
#### nomad_material_processing.vapor_deposition.pvd.thermal
#### nomad_material_processing.solution.general
!!! todo: add description of each module