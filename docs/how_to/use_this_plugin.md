# How to Use the NOMAD-material-processing Plugin

The **NOMAD-material-processing plugin** provides standardized schemas for common methods, processes, and instruments. These schemas are generalized to ensure they are not tied to any specific lab or setup, promoting interoperability across the materials science community. Users can inherit from these schemas, further specializing them to fit their specific needs, all while maintaining a consistent structure that benefits broader community use. For more details, see [levels of schemas in NOMAD](../explanation/levelsofschema.md).

To use this plugin, you must have it installed on your NOMAD Oasis instance (please refer to the [installation guide](install.md) for instructions). Alternatively, you can explore the plugin’s functionality and make use of it on our centrally hosted [Example Oasis](https://nomad-lab.eu/prod/v1/oasis/gui/search/entries).

This guide will walk you through the different ways to use the NOMAD-material-processing plugin:

- **Without specialization**: Instantiating NOMAD entries directly from the "*built-in schemas*".
- **Inheriting and specializing**: Using custom YAML schemas to adapt the existing schemas for your specific use case.
- **Using Python schema plugins**: Inheriting and specializing schemas with Python for advanced customization.

## Using "Built-in Schemas"

In this section, we will demonstrate how to use the standard, built-in **entry** schemas
provided by the plugin without any specialization. These schemas can be directly
instantiated to create entries in a NOMAD Oasis.

1. Start a new upload and click on the **CREATE FROM SCHEMA** button.
2. Select the schema from the drop-down menu, add the name for the entry, and
hit **CREATE**.

    <img src="../assets/use-built-in-schema-1.png" alt="How to use built-in schemas: picture 1" width="80%"/>

    <img src="../assets/use-built-in-schema-2.png" alt="How to use built-in schemas: picture 2" width="80%"/>

## Inheriting and Specializing Using Custom YAML Schemas

Here, we will guide you through how to extend and specialize the built-in schemas using custom YAML schemas. This approach allows you to tailor the schema to your specific requirements while still leveraging the standardized base provided by the plugin.

The schemas found in the plugin are general base sections and they go more and more specific in several techniques, however, they can be limiting in case of your own requirements.

Luckily, NOMAD provides a way of adding technique-specific behavior to the ELNs: YAML schemas - config file containing schemas added to the upload

Using a `SolutionPreparation` example, we show how to specialize a class with a YAML schema.
Two quantities, namely `initial_temperature` and `final_temperature` are added to `AddSolutionComponent` class, and `SolutionPreparation` is customized with this new class in the `steps` subsection.
We use a custom YAML schema to define the following sections:

- `SolutionPreparation`
- `AddSolutionComponent`

This leads to an improvement over the initial class

```yaml
definitions:
  name: 'Solution customization'
  sections:
    MyAddSolutionComponent:
      m_annotations:
        eln:
          properties:
            order:
              - 'name'
              - 'start_time'
              - 'duration'
              - 'comment'
              - 'solution_component'
      base_sections:
        - nomad_material_processing.solution.general.AddSolutionComponent
      quantities:
        initial_temperature:
          type: np.float64
          unit: celsius
          description: "initial temperature set for ramp"
          m_annotations:
            eln:
              component: NumberEditQuantity
              defaultDisplayUnit: celsius
        final_temperature:
          type: np.float64
          unit: celsius
          description: "final temperature set for ramp"
          m_annotations:
            eln:
              component: NumberEditQuantity
              defaultDisplayUnit: celsius
    MySolutionPreparation:
      base_sections:
        - nomad_material_processing.solution.general.Solution
        - nomad.datamodel.data.EntryData
      sub_sections:
        steps:
          repeats: True
          section: '#/MyAddSolutionComponent'
```

You can learn in detail how to create your own YAML schemas in our previous [tutorial 8](https://youtu.be/5VXGZNlz9rc?feature=shared) and [tutorial 13](https://github.com/FAIRmat-NFDI/AreaA-Examples/tree/main/tutorial13/part2).
You can navigate in the [tutorial 8](https://github.com/FAIRmat-NFDI/AreaA-Examples/tree/main/tutorial8) repository
to see some other examples of YAML files that inherit and extend existing classes.

## Inheriting and Specializing Using Python Schema Plugins

For users needing more advanced customization, we will show you how to inherit and specialize schemas using Python schema plugins. This method allows for dynamic, programmatic extensions of the standard schemas to accommodate complex use cases.

By following these steps, you can seamlessly integrate the NOMAD-material-processing plugin into your workflows and adapt it to meet your specific needs.