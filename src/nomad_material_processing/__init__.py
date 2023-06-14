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
    Quantity,
    Section,
)
from nomad.datamodel.data import (
    ArchiveSection,
)
from nomad.datamodel.metainfo.eln import (
    Process,
    Ensemble,
)

m_package = Package(name='Material Processing')


class ActivityStep(ArchiveSection):
    '''
    A step in an activity.
    '''
    m_def = Section()

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `ActivityStep` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(ActivityStep, self).normalize(archive, logger)


class Substrate(Ensemble, ArchiveSection):
    '''
    A thin free standing sheet of material. Not to be confused with the substrate role
    during a deposition, which can be a `Substrate` with `ThinFilm`(s) on it.
    '''
    m_def = Section()
    thickness = Quantity(
        type=float,
        description='''
        The (average) thickness of the substrate.
        ''',
        a_eln={
            "component": "NumberEditQuantity",
            "defaultDisplayUnit": "millimeter"
        },
        unit="meter",
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `Substrate` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(Substrate, self).normalize(archive, logger)


class ThinFilm(Ensemble, ArchiveSection):
    '''
    A thin film of material which exists as part of a stack.
    '''
    m_def = Section()
    thickness = Quantity(
        type=float,
        description='''
        The (average) thickness of the thin film.
        ''',
        a_eln={
            "component": "NumberEditQuantity",
            "defaultDisplayUnit": "nanometer"
        },
        unit="meter",
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `ThinFilm` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(ThinFilm, self).normalize(archive, logger)


class ThinFilmStack(Ensemble, ArchiveSection):
    '''
    A stack of `ThinFilm`(s). Typically deposited on a `Substrate`.
    '''
    m_def = Section()
    substrate = Quantity(
        type=Substrate,
        description='''
        The substrate which the thin film layers of the thin film stack are deposited
        on.
        ''',
        a_eln={
            "component": "ReferenceEditQuantity"
        },
    )
    layers = Quantity(
        type=ThinFilm,
        description='''
        An ordered list (starting at the substrate) of the thin films making up the
        thin film stacks.
        ''',
        a_eln={
            "component": "ReferenceEditQuantity"
        },
        shape=["*"],
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `ThinFilmStack` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(ThinFilmStack, self).normalize(archive, logger)


class SampleDeposition(Process, ArchiveSection):
    '''
    The process of the settling of particles (atoms or molecules) from a solution,
    suspension or vapour onto a pre-existing surface, resulting in the growth of a
    new phase. [database_cross_reference: https://orcid.org/0000-0002-0640-0422]

    Synonyms:
     - deposition
    '''
    m_def = Section(
        links=[
            "http://purl.obolibrary.org/obo/CHMO_0001310"
        ],)

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `SampleDeposition` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(SampleDeposition, self).normalize(archive, logger)


m_package.__init_metainfo__()
