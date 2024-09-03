"""
Module containing NOMAD classes for material systems.
To be moved to a more general plugin in the future.
"""

from typing import TYPE_CHECKING

from nomad.metainfo import (
    SchemaPackage,
)

if TYPE_CHECKING:
    pass

m_package = SchemaPackage(
    aliases=[
        'nomad_material_processing.material_systems',
    ],
)


m_package.__init_metainfo__()
