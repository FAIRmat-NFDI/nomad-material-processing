# nomad-plugin-template
A template repository for creating a repository with a NOMAD plugin package.


## Getting started

1. Click on the `Use this template` button and create a new plugin repository. The form will ask you to fill out the name for the new plugin repository.

2. In the newly created repository, start a new Github Codespace and generate the plugin structure.

Run the following command to create a new NOMAD plugin project using cookiecutter-nomad-plugin:

```sh
cruft create https://github.com/FAIRmat-NFDI/cookiecutter-nomad-plugin
```

Cookiecutter prompts you for information regarding your plugin:

```no-highlight
full_name [John Doe]: Citizen Kane
email [john.doe@physik.hu-berlin.de]: citizen@kane.de
github_username [foo]: kane
plugin_name [foobar]: awesome-tools
module_name [awesome_tools]: awesome_tools
short_description [NOMAD example template]: An awesome plugin for NOMAD
version [0.1.0]:
Select license:
1 - MIT
2 - BSD-3
3 - GNU GPL v3.0+
Choose from 1, 2, 3 [1]: 2
include_schema_package [y/n] (y): y
include_normalizer [y/n] (y): n
include_parser [y/n] (y): y
include_app [y/n] (y): n

INFO:post_gen_project:Initializing python for package - src
..
INFO:post_gen_project:Remove temporary folder: licenses
INFO:post_gen_project:Remove temporary folder: macros
INFO:post_gen_project:Remove temporary folder: py_sources
```




There you go - you just created a minimal NOMAD plugin:

> [!NOTE]
> In the above prompt, we pressed `y` for schema_package and parser, this creates a python package with two plugin entry points: one for parser and one for schema_package.

```no-highlight
nomad-awesome-tools/
├── LICENSE
├── README.rst
├── pyproject.toml
├── move_template_files.sh
├── src
│   └── nomad_awesome_tools
│       ├── __init__.py
|       ├── schema_packages
│       |   ├── __init__.py
│       |   └── plugin.py
|       └── parsers
│           ├── __init__.py
│           └── plugin.py
|
├── tests
│   ├── conftest.py
│   └── test_awesome.py
└── MANIFEST.in
```


> [!NOTE]
> The project `nomad-awesome-tools` is created in a new directory, we have included a helper script to move all the files to the parent level of the repository.


```sh
sh CHANGE_TO_PLUGIN_NAME/move_template_files.sh
```

> [!IMPORTANT]
> The `CHANGE_TO_PLUGIN_NAME` should be substituted by the name of the plugin you've created. In the above case it'll be `sh nomad-awesome-tools/move_template_files.sh`. 
