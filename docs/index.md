# Welcome to the NOMAD-materials-processing Plugin Documentation

Welcome to the official documentation for the **NOMAD-materials-processing Plugin**! This plugin provides NOMAD schemas, readers, and parsers for data of materials science synthesis processes in alignment with the FAIR (Findable, Accessible, Interoperable, and Reusable) principles. It serves as a community or standard plugin, offering commonly used schemas and classes/sections for materials processing data that can be shared across a community.

## Supported Materials Processing Techniques

Currently, this plugin supports the following materials processing techniques:

- **Synthesis from Gas Phase**:
  Supports different *Vapor Deposition* methods:
  ```bash
  Vapor Deposition
  ├── Phyiscal Vapor Deposition (PVD)
  │       ├── Molecular Beam Epitaxy (MBE)
  │       ├── Pulsed Laser Deposition (PLD)
  │       ├── Sputtering
  │       └── Thermal Evaporation
  │
  └── Chemical Vapor Deposition (CVD)
          └── Metalorganic Vapor Phase Epitaxy (MOVPE)
  ```

- **Synthesis from Solution**:
  Supports Solution Preparation

Additional materials processing techniques are actively being developed and will be included soon, including Synthesis from the Melt (bulk crystal growth), Synthesis by Assembly (e.g. polymerization).

Stay tuned for updates as more methods become available!

## What You Will Find in This Documentation

This documentation builds upon the general [NOMAD documentation](https://nomad-lab.eu/prod/v1/staging/docs/explanation/data.html). Here, you will find comprehensive guides on:

- **Using the Plugin**: Step-by-step instructions on how to integrate and use the NOMAD Materials Processing Plugin in your NOMAD Oasis.
- **Data Structures and Supported Methods**: Detailed descriptions of the available schemas, sections, and supported materials processing techniques.
- **Contributing**: Learn how you can contribute to the ongoing development of this plugin.

## About NOMAD

NOMAD is an open-source data management platform tailored for materials science, designed to follow the FAIR principles. It offers a robust framework for managing and sharing materials data in a standardized and interoperable manner. To learn more about NOMAD, visit the [official homepage](https://nomad-lab.eu).


We hope this documentation provides all the information you need to make the most of the NOMAD Measurements Plugin. Feel free to [contact](contact.md) us for further questions.

