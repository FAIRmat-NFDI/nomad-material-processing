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
from nomad.metainfo import (
    Package,
    Quantity,
    SubSection,
    Section,
)
from nomad.datamodel.data import (
    ArchiveSection,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
)
from nomad.datamodel.metainfo.basesections import (
    Collection,
    CompositeSystem,
    CompositeSystemReference,
)
if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name='Combinatorial Synthesis')


class CombinatorialSample(CompositeSystem):
    '''
    A base section for any sample of a combinatorial library.
    '''
    m_def = Section()
    sample_number = Quantity(
        type=int,
        description='''
        A unique number for this sample of the combinatorial library.
        ''',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
        ),
    )
    lab_id = Quantity(
        type=str,
        description='''
        A unique human readable ID for the sample within the combinatorial library.
        Suggested to be the ID of the library followed by a dash ("-") and the sample
        number.
        ''',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            label='Sample ID',
        ),
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        '''
        The normalizer for the `CombinatorialSample` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(CombinatorialSample, self).normalize(archive, logger)


class CombinatorialSampleReference(CompositeSystemReference):
    '''
    A section containing a reference to a combinatorial sample entry.
    '''
    m_def = Section(
        label_quantity='sample_number',
    )
    sample_number = Quantity(
        type=int,
        description='''
        A unique number for this sample of the combinatorial library.
        ''',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
        ),
    )
    reference = Quantity(
        type=CombinatorialSample,
        description='''
        The reference to the combinatorial sample entry.
        ''',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
            label='Sample Reference',
        ),
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        '''
        The normalizer for the `CombinatorialSampleReference` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(CombinatorialSampleReference, self).normalize(archive, logger)


class CombinatorialLibrary(Collection):
    '''
    A base section for any combinatorial library.
    '''
    m_def = Section()
    lab_id = Quantity(
        type=str,
        description='''
        A unique human readable ID for the combinatorial library.
        ''',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            label='Library ID'
        ),
    )
    entities = SubSection(
        section_def=CombinatorialSampleReference,
        description='''
        All the investigated samples of the combinatorial library.
        ''',
        repeats=True,
        a_eln=ELNAnnotation(
            label='Samples'
        ),
    )
    # lab_id = Collection.lab_id.m_copy()
    # lab_id.description = '''
    #     A unique human readable ID for the combinatorial library.
    #     '''
    # lab_id.m_annotations['eln'].label = 'Library ID'
    # entities = Collection.entities.m_copy()
    # entities.section_def = CombinatorialSampleReference
    # entities.description = '''
    #     All the investigated samples of the combinatorial library.
    #     '''
    # entities.m_annotations['eln'] = ELNAnnotation(
    #     label='Samples'
    # )  # Currently the label cannot be overwritten.

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        '''
        The normalizer for the `CombinatorialLibrary` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(CombinatorialLibrary, self).normalize(archive, logger)


class CombinatorialSamplePosition(ArchiveSection):
    '''
    A section for representing the position of a sample within a continuous
    combinatorial library.
    If nothing else is specified it is the position relative to the center of mass of
    the library.
    '''
    m_def = Section()
    x = Quantity(
        type=float,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='mm',
        ),
        unit='m',
    )
    y = Quantity(
        type=float,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='mm',
        ),
        unit='m',
    )
    z = Quantity(
        type=float,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='mm',
        ),
        unit='m',
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        '''
        The normalizer for the `CombinatorialSamplePosition` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(CombinatorialSamplePosition, self).normalize(archive, logger)


class ContinuousCombiSample(CombinatorialSample):
    '''
    A base section for any sample of a continuous combinatorial library.
    '''
    m_def = Section()
    position = SubSection(
        section_def=CombinatorialSamplePosition,
        description='''
        The position of a sample within the continuous combinatorial library. If nothing 
        else is specified it is the position relative to the center of mass of the 
        library.
        ''',
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        '''
        The normalizer for the `ContinuousCombiSample` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(ContinuousCombiSample, self).normalize(archive, logger)


class ContinuousCombiSampleReference(CombinatorialSampleReference):
    '''
    A section containing a reference to a continuous combinatorial sample entry.
    '''
    m_def = Section(
        label_quantity='sample_number',
    )
    reference = Quantity(
        type=ContinuousCombiSample,
        description='''
        The reference to the combinatorial sample entry.
        ''',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
            label='Sample Reference',
        ),
    )
    # reference = CombinatorialSampleReference.reference.m_copy()
    # reference.type = ContinuousCombiSample  # Specializing custom types is currently not supported.
    position = SubSection(
        section_def=CombinatorialSamplePosition,
        description='''
        The position of a sample within the continuous combinatorial library. If nothing 
        else is specified it is the position relative to the center of mass of the 
        library.
        ''',
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        '''
        The normalizer for the `ContinuousCombiSampleReference` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(ContinuousCombiSampleReference, self).normalize(archive, logger)


class ContinuousCombiLibrary(CombinatorialLibrary):
    '''
    A base section for any continuous combinatorial library.
    '''
    m_def = Section()
    entities = SubSection(
        section_def=ContinuousCombiSampleReference,
        description='''
        All the investigated samples of the combinatorial library.
        ''',
        repeats=True,
        a_eln=ELNAnnotation(
            label='Samples'
        ),
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        '''
        The normalizer for the `ContinuousCombiLibrary` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(ContinuousCombiLibrary, self).normalize(archive, logger)


m_package.__init_metainfo__()
