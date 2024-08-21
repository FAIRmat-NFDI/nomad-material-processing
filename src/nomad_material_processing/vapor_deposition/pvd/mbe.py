#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from typing import (
    TYPE_CHECKING,
)

from nomad.config import config
from nomad.metainfo import (
    SchemaPackage,
    Section,
)

from nomad_material_processing.vapor_deposition.pvd.general import (
    PhysicalVaporDeposition,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )


m_package = SchemaPackage(name='Molecular Beam Epitaxy')

configuration = config.get_plugin_entry_point(
    'nomad_material_processing.vapor_deposition.pvd:mbe_schema',
)


class MolecularBeamEpitaxy(PhysicalVaporDeposition):
    """
    A synthesis method which consists of depositing a monocrystalline film (from a
    molecular beam) on a monocrystalline substrate under high vacuum (<10^{-8} Pa).
    Molecular beam epitaxy is very slow, with a deposition rate of <1000 nm per hour.
    [database_cross_reference: https://orcid.org/0000-0002-0640-0422]

    Synonyms:
     - MBE
     - molecular-beam epitaxy
    """

    m_def = Section(
        links=[
            'http://purl.obolibrary.org/obo/CHMO_0001336',
            'http://purl.obolibrary.org/obo/CHMO_0001341',
        ],
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `MolecularBeamEpitaxy` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)
