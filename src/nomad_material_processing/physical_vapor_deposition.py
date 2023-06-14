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

m_package = Package(name='Physical Vapor Deposition')


class PhysicalVaporDeposition(SampleDeposition):
    '''
    A synthesis technique where vaporized molecules or atoms condense on a surface,
    forming a thin layer. The process is purely physical; no chemical reaction occurs
    at the surface. [database_cross_reference: https://orcid.org/0000-0002-0640-0422]

    Synonyms:
     - PVD
     - physical vapor deposition
    '''
    m_def = Section(
        links=[
            "http://purl.obolibrary.org/obo/CHMO_0001356"
        ],)

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `PhysicalVaporDeposition` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(PhysicalVaporDeposition, self).normalize(archive, logger)


class PulsedLaserDeposition(PhysicalVaporDeposition):
    '''
    A synthesis technique where a high-power pulsed laser beam is focused (inside a
    vacuum chamber) onto a target of the desired composition. Material is then
    vaporized from the target ('ablation') and deposited as a thin film on a
    substrate facing the target.
    [database_cross_reference: https://orcid.org/0000-0002-0640-0422]

    Synonyms:
     - pulsed laser ablation deposition
     - PLD
     - pulsed-laser ablation deposition
     - laser ablation growth
     - PLA deposition
     - pulsed-laser deposition
    '''
    m_def = Section(
        links=[
            "http://purl.obolibrary.org/obo/CHMO_0001363"
        ],)

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `PulsedLaserDeposition` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(PulsedLaserDeposition, self).normalize(archive, logger)


class SputterDeposition(PhysicalVaporDeposition):
    '''
    A synthesis technique where a solid target is bombarded with electrons or
    energetic ions (e.g. Ar+) causing atoms to be ejected ('sputtering'). The ejected
    atoms then deposit, as a thin-film, on a substrate.
    [database_cross_reference: https://orcid.org/0000-0002-0640-0422]

    Synonyms:
     - sputtering
     - sputter coating
    '''
    m_def = Section(
        links=[
            "http://purl.obolibrary.org/obo/CHMO_0001364"
        ],)

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `SputterDeposition` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(SputterDeposition, self).normalize(archive, logger)


class ThermalEvaporation(PhysicalVaporDeposition):
    '''
    A synthesis technique where the material to be deposited is heated until
    evaporation in a vacuum (<10^{-4} Pa) and eventually deposits as a thin film by
    condensing on a (cold) substrate.
    [database_cross_reference: https://orcid.org/0000-0002-0640-0422]

    Synonyms:
     - evaporative deposition)
     - vacuum thermal evaporation
     - TE
     - thermal deposition
     - filament evaporation
     - vacuum condensation
    '''
    m_def = Section(
        links=[
            "http://purl.obolibrary.org/obo/CHMO_0001360"
        ],)

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `ThermalEvaporation` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(ThermalEvaporation, self).normalize(archive, logger)


m_package.__init_metainfo__()
