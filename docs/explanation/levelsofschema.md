## Levels of schemas in NOMAD

It is important to understand the structure and relationship of different types of schemas in NOMAD. Here we break down the levels of schemas and how they interact. For detailed information, please visit the [official NOMAD documentation](https://nomad-lab.eu/prod/v1/staging/docs/explanation/data.html#schema).

### Types of Schemas in NOMAD

NOMAD categorizes its schemas into multiple levels, each serving distinct purposes while ensuring consistent data organization and interoperability:

1. **Basic Architecture Sections**: These define the overall structure of any entry within NOMAD, regardless of the specific data type. They provide a shared, high-level framework applicable across different use cases, ensuring that every entry adheres to a consistent format. `EntryData` and `ArchiveSection` are the two relevant classes to be mentioned here.
Every entry in NOMAD must inherit from `EntryData`, whenever a class is only used as a subsection composed within a more general one, inheriting from `ArchiveSection` is enough.

2. **Base Sections**: These are central to NOMAD's data model and are designed to maintain interoperability between different database entries. The base sections follow an entity-activity model tailored for materials science, capturing essential relationships between key entities like samples, instruments, processes, measurements, analyses, experiments, and simulations. The goal is to provide standardized structures for data representation.


	- **Important Note**: Base sections in NOMAD are abstract and should not be instantiated directly. Instead, users must implement these sections in their own schemas (referred to as user schemas) by inheriting from a base section and `nomad.datamodel.EntryData`. Users are strongly encouraged to use the most specialized section available for their use case.


3. **Community/Standard Plugins**: FAIRmat offers standardized schemas for common methods, processes, and instruments that are generalized and not tied to any specific lab or setup. These schemas are derived from recurring patterns identified across user schemas. Users can inherit from these standard plugins in a similar manner as the base sections, further specializing them as needed while still maintaining a consistent structure for broader community use.
FAIRmat's Area A for synthesis data provides two community plugins, NOMAD Measurements and NOMAD Materials Processing.

4. **User Defined Sections**: These schemas are developed by users and are specific to a method or an instrument, a lab, or a full institute. They build upon the base sections and community plugins, tailoring them to meet specific research needs. In this level, users can define more specialized structures that directly reflect the specific characteristics of their experiments or simulations.



### How These Schemas Relate to Each Other

The relationships between these schema levels can be visualized as a layered model:

- **Basic Architecture and Base Sections**: At the core, ensuring interoperability and defining the primary structures.

- **Community/Standard Plugins**: Inherit and specialize the base sections and provide generalized versions of common user schemas, making them clearly shaped on distinct fields of materials science while still allowing broad applicability across the community.

- **User Schemas**: Inherit and specialize community plugins sections, if availbale, or the base sections according to specific requirements.

### Encouraged Usage

NOMAD encourages users to first explore the available community/standard plugins and base sections before developing their own schemas. By doing so, they can maximize interoperability and benefit from established structures, while still retaining the flexibility to adapt the schema to their unique needs.

The figure below illustrates these schema levels and the recommended workflow for schema development within NOMAD.

In next documentation sections, an overview of the available methods will be provided.

![Levels of schema](../assets/levelsschema.png)


## Community/Standard Schemas

The NOMAD Material Processing Plugin contains schemas for different synthesis methods.
An overview of the package structure is shown below.

There are some technical aspects of the package that should be mentioned but they are not crucial for the data model understanding itself.

- it is an `src` structured package, i. e., the source code is contained within the `src` folder instead of being spread directly within the root folder.
- the package structure is defined by the presence of `__init__.py` files. Inside each of these files, the **entry points** of the plugin are specifiec.
- the package is pip installable. The `project.toml` file defines what will be installed, the dependencies, further details. The **entry points** that will be installed are listed in thsi file.

```
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

Moving on with the description of the scientific data model contained in this plugin, each method has a dedicated module, i. e., a python file.

- general.py
- vapor deposition:
  - cvd:
    - general.py
    - movpe.py
  - pvd:
    - general.py
    - mbe.py
    - pld.py
    - sputtering.py
    - thermal.py
- solution:
  - general.py
  - utils.py
