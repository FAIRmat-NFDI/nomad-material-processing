# NOMAD Material Processing: a Community plugin

The NOMAD Material Processing Plugin contains schemas for different synthesis methods.
An overview of the package structure is shown below.

## Technical description

This section introduces some aspects of the Python package built for this plugin. Despite not being crucial for the understanding of the data model, they can help installing or developing it.

- It is structured according to the [src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/).
- It is a [regular Python package](https://docs.python.org/3/reference/import.html#regular-packages), i. e., the structure is defined by the presence of `__init__.py` files.
- The `__init__.py` files contain one or multiple [entry points](https://nomad-lab.eu/prod/v1/staging/docs/howto/plugins/plugins.html#plugin-entry-points). These are used to load a portion of the code within your NOMAD through a specific section in the `nomad.yaml` file. If this section is not specified, all the entry points are loaded by default.
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

## Data model description

Each method is separated in a dedicated [module](https://docs.python.org/3/tutorial/modules.html), i. e., a python file.

### General

The `nomad_material_processing.general` module contains several general categories of classes:

- an abstract process class `SampleDeposition` that is inherited in the specific processes such as MOVPE, MBE, PLD, etc.
- `Substrate` and `CrystallineSubstrate` entities, the support used in `SampleDeposition` activities.
- `ThinFilm` entity, usually created during `SampleDeposition` activities.
- `ThinFilmStack` in case of processes producing multilayer samples. This class also contains a reference to the `Substrate`.
- `Geometry` and its [subclasses](../reference/references.md#subclass), defining the commonly found macroscopic shapes of a sample. It is a [subsection](../reference/references.md#subsection) composed within the `Substrate`. They include `Parallelepiped`, `SquareCuboid`, `RectangleCuboid`, `TruncatedCone`, `Cylinder`, `CylinderSector`, `IrregularParallelSurfaces`.
- `Miscut` another [subsection](../reference/references.md#subsection) of  `Substrate` to specify the miscut of the orientation of the surface in terms of angular deviation toward crystallographic directions.
- `CrystalProperties` and `ElectronicProperties`, found as [subsection](../reference/references.md#subsection) of sample entities that need these parameters.
- simple activities performed on samples: `Etching`, `Annealing`, `Cleaning`. They also include a `Recipe` that can be referenced inside to avoid repetition for routine tasks.
- `TimeSeries` a general class that shapes every kind of parameters logged along a time window. The quantities referring to the measured parameter are `value` and `time`. `set_value` and `set_time` can also be specified, as they usually differ from the measured ones. Several [subclasses](../reference/references.md#subclass) inheriting from this one can be found nested in the package.

### Vapor Deposition

The `nomad_material_processing.vapor_deposition.general` module contains classes describing
a general vapor deposition process. The master class in this module is `VaporDeposition`, inheriting from `SampleDeposition`.

The other classes found here are specifying the [subsections](../reference/references.md#subsection) found in the steps of the `VaporDeposition` process.
`VaporDepositionStep` contains three [subsections](../reference/references.md#subsection) allowing to describe the parameters usually recorded during an experiment:

- `VaporDepositionSource` the metadata on which kind of source will bring the raw material in the reaction chamber.
This class is in turn composed by three distinct elements, namely the `Component` material to be evaporated, the `EvaporationSource` that is the element that produces the vapor, and `MolarFlowRate` that is a time series recording the molar flux exiting the source. This is used as a list within the `VaporDepositionStep` because many sources can be present at the same time.
- `SampleParameter` this [subsection](../reference/references.md#subsection) hosts the references to the `ThinFilm` deposited and the `ThinFilmStack` or `Substrate` used as support of the deposition. This [subsection](../reference/references.md#subsection) is also used to record sample-specific parameters in the process, such as temperature, or growth rate. This is a list because many samples can be grown at the same time.
- `ChamberEnvironment` collects the metadata connected to the whole reaction chamber that cannot be linked to one single sample. It usually contains temperature or `GasFlow` [subsections](../reference/references.md#subsection).

These three [subsections](../reference/references.md#subsection) are the backbone of the `VaporDeposition` process and they are usually inherited whenever a specific experiment requires to extend them.

### Chemical Vapor Deposition

The `nomad_material_processing.vapor_deposition.cvd.general` module contains specifications of `VaporDepositionSource` and `TimeSeries` commonly adopted in CVD techniques:

Sources for CVD are inheriting from `CVDSource`, that is in turn a `VaporDepositionSource`.

- `BubblerSource` defines a bubbler commonly used in CVD for liquid precursors.
- `FlashSource` the vapor is generated by a `FlashEvaporator`.
- `MistSource` another kind of source adopted in CVD.
- `GasCylinderSource` a simple cylinder containing some gas phase precursor. In this case the `EvaporationSource` [subclass](../reference/references.md#subclass), called `GasCylinderEvaporator`, is not really evaporating as the precursor is already at the gas state.
- `GasLineSource` used for gaseous precursors that are provided through a stable installation sourcing gas from facilities external to the lab.

`TimeSeries` used in CVD are:

- `Rotation` specifies rotation frequency of the substrate holder in the chamber
- `PartialVaporPressure` as [subclass](../reference/references.md#subclass) of `Pressure`
- `PushPurgeGasFlow` contains two `VolumetricFlowRate` [subsections](../reference/references.md#subsection) that record the source and drain fluxes of the carries gas in the chamber.


### Metal-organic Vapor Phase Epitaxy (MOVPE)

The `nomad_material_processing.vapor_deposition.cvd.movpe` module contains classes
dedicated to the Metal-organic Vapor Phase Epitaxy (MOVPE) technique.

### Physical Vapor Deposition (PVD)
The `nomad_material_processing.vapor_deposition.pvd.general` module contains classes
describing a general Physical Vapor Deposition (PVD) process. This adopts the three
general concepts from the vapor deposition above (the chamber, the sources, and the
 substrates) and specializes them for various PVD techniques:

#### Pulsed Laser Deposition (PLD)
The `nomad_material_processing.vapor_deposition.pvd.pld` module adds a specialized laser
source with its corresponding parameters.

#### Sputtering
The `nomad_material_processing.vapor_deposition.pvd.sputtering` module adds a specialized
sputtering source with its corresponding parameters.

#### Thermal Evaporation
The `nomad_material_processing.vapor_deposition.pvd.thermal` module adds a specialized
thermal evaporation source with its corresponding parameters.

#### Molecular Beam Epitaxy (MBE)
The `nomad_material_processing.vapor_deposition.pvd.mbe` module uses the thermal evaporation
source and also adds a plasma source.


### nomad_material_processing.solution.general

The main entry sections in this module are
[`Solution`](#nomad_material_processing.solution.general.Solution) and
[`SolutionPreparation`](#nomad_material_processing.solution.general.SolutionPreparation) which can
be used to create NOMAD
[entries](https://nomad-lab.eu/prod/v1/docs/reference/glossary.html#entry).
There's a long list of other auxiliary sections supporting these entry section which
can be accessed in the
[metainfo browser](https://nomad-lab.eu/prod/v1/oasis/gui/analyze/metainfo/nomad_material_processing)
by searching for: `"nomad_material_processing.solution.general"`

#### `nomad_material_processing.solution.general.Solution`

Describes liquid solutions by extending the
[`CompositeSystem`](https://nomad-lab.eu/prod/v1/docs/howto/customization/base_sections.html#system) with quantities: _pH_, _mass_,
_calculated_volume_, _measured_volume_, _density_, and sub-sections:
_solvents_, _solutes_, and _solution_storage_.

```py
class Solution(CompositeSystem, EntryData):
    ph_value: float
    mass: float
    calculated_volume: float
    measured_volume: float
    density: float
    components: list[
        Union(
            SolutionComponent,
            SolutionComponentReference,
        )
    ]
    solutes: list[SolutionComponent]
    solvents: list[SolutionComponent]
    solution_storage: SolutionStorage
```

!!! info
    The _measured_volume_ field is user-defined. By default, the automation in
    `Solution` uses _calculated_volume_, but if _measured_volume_ is provided, it will take
    precedence. This is useful when the final solution volume differs from the sum of its
    component volumes, and should be specified by the user.

The _components_ sub-section, inherited from `CompositeSystem` and re-defined, is used to describe
a list of components used in the solution. Each of them contributes to the _mass_ and
_calculated_volume_ of the solution. The component can either nest a
sub-section describing its composition, or can be another `Solution` entry connected
via reference.
These options are are handled by
`SolutionComponent` and `SolutionComponentReference` sections respectively. Let's take a closer look at each of them.

`SolutionComponent` extends `PureSubstanceComponent` with quantities:
_component_role_, _mass_, _volume_, _density_, and sub-section: _molar_concentration_.
The _pure_substance_ sub-section inherited from `PureSubstanceComponent` specifies the
chemical compound. This information along with the mass of the component and
total volume of the solution is used to automatically determine the molar concentration of
the component, populating the corresponding sub-section.
Based on the _component_role_, the components are copied over to either
`Solution.solvents` or `Solution.solutes`.

```py
class SolutionComponent(PureSubstanceComponent):
    component_role: Enum('Solvent', 'Solute')
    mass: float
    volume: float
    density: float
    molar_concentration: MolarConcentration
```

`SolutionComponentReference` makes a reference to another `Solution` entry and specifies
the amount used. Based on this, _solutes_ and _solvents_ of the referenced solution are
copied over to the first solution. Their mass and volume are adjusted based on the
amount of the referenced solution used.

```py
class SolutionComponentReference(SystemComponent):
    mass: float
    volume: float
    system: Solution
```

Both `Solution.solvents` and `Solution.solutes` are a list of `SolutionComponent`. The
molar concentration of each of them is automatically determined. Additionally, if the
list has multiple `SolutionComponent` representing the same chemical entity, there are
combined into one.

The _solution_storage_ uses `SolutionStorage` section to describe storage conditions
, i.e., temperature and atmosphere, along with preparation and expiry dates.

#### `nomad_material_processing.solution.general.SolutionPreparation`

Describes the steps of solution preparation by extending
[`Process`](https://nomad-lab.eu/prod/v1/docs/howto/customization/base_sections.html#process).
Based on the steps added, it also creates a `Solution` entry and references it under the
_solution_ sub-section.

```py
class SolutionPreparation(Process, EntryData):
    solution_name: str
    solution: SolutionReference
    step: list[SolutionPreparationStep]
```

The generated `Solution` entry picks its name from _solution_name_, if specified.
Otherwise, it will be uniquely named as `"unnamed_solution_{i}"`, where `i` will be an
integer starting from 0. Currently, the following `SolutionPreparationStep` are defined:

- `AddSolutionComponent`: Adds a `SolutionComponent` or `SolutionComponentReference` to
_components_ list of the generated `Solution` entry. It also contains a sub-section
`measurement` which can be used to specify the methodology used for measuring the
component like pipetting and scaling.
```py
class AddSolutionComponent(SolutionPreparationStep):
    solution_component: Union(
        SolutionComponent,
        SolutionComponentReference,
    )
    measurement: MeasurementMethodology
```

- `Agitation`: Specifies the process of agitating the solution. There are more sections
inheriting this class and describing specific techniques:
`MechanicalStirring(Agitation)` and `Sonication(Agitation)`.

