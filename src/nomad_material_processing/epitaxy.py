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

from structlog.stdlib import (
    BoundLogger,
)
from nomad.metainfo import (
    Package,
    Section,
)
from nomad_material_processing import (
    SampleDeposition,
)

m_package = Package(name='Epitaxy')


class Epitaxy(SampleDeposition):
    '''
    A synthesis method which consists of depositing a monocrystalline film (from
    liquid or gaseous precursors) on a monocrystalline substrate.
    [database_cross_reference: https://orcid.org/0000-0002-0640-0422]
    '''
    m_def = Section(
        links=[
            "http://purl.obolibrary.org/obo/CHMO_0001336"
        ],)

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `Epitaxy` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(Epitaxy, self).normalize(archive, logger)


class MolecularBeamEpitaxy(Epitaxy):
    '''
    A synthesis method which consists of depositing a monocrystalline film (from a
    molecular beam) on a monocrystalline substrate under high vacuum (<10^{-8} Pa).
    Molecular beam epitaxy is very slow, with a deposition rate of <1000 nm per hour.
    [database_cross_reference: https://orcid.org/0000-0002-0640-0422]

    Synonyms:
     - MBE
     - molecular-beam epitaxy
    '''
    m_def = Section(
        links=[
            "http://purl.obolibrary.org/obo/CHMO_0001341"
        ],)

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `MolecularBeamEpitaxy` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(MolecularBeamEpitaxy, self).normalize(archive, logger)


class VaporPhaseEpitaxy(Epitaxy):
    '''
    A synthesis method which consists of depositing a monocrystalline film (from
    vapour-phase precursors) on a monocrystalline substrate.
    [database_cross_reference: https://orcid.org/0000-0002-0640-0422]

    Synonyms:
     - vapour-phase epitaxial growth
     - vapor-phase epitaxy
     - vapor phase epitaxy
     - VPE
     - vapour phase epitaxy
    '''
    m_def = Section(
        links=[
            "http://purl.obolibrary.org/obo/CHMO_0001346"
        ],)

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `VaporPhaseEpitaxy` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(VaporPhaseEpitaxy, self).normalize(archive, logger)


class MetalOrganicVaporPhaseEpitaxy(VaporPhaseEpitaxy):
    '''
    A synthesis method which consists of depositing a monocrystalline film, from
    organometallic vapour-phase precursors, on a monocrystalline substrate.
    [database_cross_reference: https://orcid.org/0000-0002-0640-0422]

    Synonyms:
     - OMVPE
     - MOVPE
     - metalorganic vapour phase epitaxy
     - metal organic vapour phase epitaxy
     - metalorganic vapor phase epitaxy
     - organometallic vapor phase epitaxy
     - metal-organic vapor-phase epitaxy
     - metal organic vapor phase epitaxy
     - metal-organic vapour-phase epitaxy
     - organometallic vapour phase epitaxy
    '''
    m_def = Section(
        links=[
            "http://purl.obolibrary.org/obo/CHMO_0001348"
        ],)

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `MetalOrganicVaporPhaseEpitaxy` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(MetalOrganicVaporPhaseEpitaxy, self).normalize(archive, logger)


m_package.__init_metainfo__()
