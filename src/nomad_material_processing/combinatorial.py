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

import plotly.graph_objects as go
from nomad.datamodel.data import (
    ArchiveSection,
    EntryData,
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
from nomad.datamodel.metainfo.plot import (
    PlotlyFigure,
    PlotSection,
)
from nomad.metainfo import (
    Package,
    Quantity,
    Section,
    SubSection,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name='Combinatorial Synthesis')


class CombinatorialLibrary(CompositeSystem, EntryData, PlotSection):
    """
    A base section for any continuous combinatorial library.
    """

    m_def = Section()

    def plot(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        from nomad.search import (
            MetadataPagination,
            search,
        )

        query = {
            'section_defs.definition_qualified_name:all': [
                'nomad_material_processing.combinatorial.CombinatorialSample'
            ],
            'entry_references.target_entry_id:all': [archive.metadata.entry_id],
        }
        search_result = search(
            owner='all',
            query=query,
            pagination=MetadataPagination(page_size=1),
            user_id=archive.metadata.main_author.user_id,
        )
        references = []
        x_values = []
        y_values = []
        z_values = []
        if search_result.pagination.total > 0:
            for res in search_result.data:
                entry_id = res['entry_id']
                upload_id = res['upload_id']
                reference = f'../../../{upload_id}/entry/id/{entry_id}'
                x, y, z = None, None, None
                for quantity in res['search_quantities']:
                    if quantity['path_archive'] == 'data.position.x':
                        x = quantity['float_value']
                    if quantity['path_archive'] == 'data.position.y':
                        y = quantity['float_value']
                    if quantity['path_archive'] == 'data.position.z':
                        z = quantity['float_value']
                references.append(reference)
                x_values.append(x)
                y_values.append(y)
                z_values.append(z)
            print(f'Found {search_result.pagination.total} activities.')
        fig = go.Figure(
            data=go.Scatter(
                x=x_values,
                y=y_values,
                mode='markers',
                customdata=references,
                marker=dict(color='#2A4CDF'),
                hovertemplate='<a href="%{customdata}">Link</a><extra></extra>',
            )
        )

        # Set plot title and axis labels
        fig.update_layout(
            template='plotly_white',
            hovermode='closest',
            dragmode='zoom',
            title='Scatter Plot of x and y Coordinates',
            xaxis_title='x / m',
            yaxis_title='y / m',
        )
        plot_json = fig.to_plotly_json()
        plot_json['config'] = dict(
            scrollZoom=False,
        )
        self.figures.append(
            PlotlyFigure(
                label='Power, pressure, and temperature',
                figure=plot_json,
            )
        )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `ContinuousCombiLibrary` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)
        self.figures = []
        self.plot(archive, logger)


class CombinatorialSamplePosition(ArchiveSection):
    """
    A section for representing the position of a sample within a continuous
    combinatorial library.
    If nothing else is specified it is the position relative to the center of mass of
    the library.
    """

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
        """
        The normalizer for the `CombinatorialSamplePosition` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)


class CombinatorialLibraryReference(CompositeSystemReference):
    """
    A section containing a reference to a continuous combinatorial library entry.
    """

    m_def = Section(
        label_quantity='lab_id',
    )
    reference = Quantity(
        type=CombinatorialLibrary,
        description="""
        The reference to the combinatorial library entry.
        """,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
            label='Library Reference',
        ),
    )


class CombinatorialSample(CompositeSystem, EntryData):
    """
    A base section for any sample of a continuous combinatorial library.
    """

    m_def = Section()
    sample_number = Quantity(
        type=int,
        description="""
        A unique number for this sample of the combinatorial library.
        """,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
        ),
    )
    lab_id = Quantity(
        type=str,
        description="""
        A unique human readable ID for the sample within the combinatorial library.
        Suggested to be the ID of the library followed by a dash ("-") and the sample
        number.
        """,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            label='Sample ID',
        ),
    )
    library = SubSection(
        section_def=CombinatorialLibraryReference,
        description="""
        The reference to the combinatorial library entry.
        """,
    )
    position = SubSection(
        section_def=CombinatorialSamplePosition,
        description="""
        The position of a sample within the continuous combinatorial library. If nothing
        else is specified it is the position relative to the center of mass of the
        library.
        """,
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `CombinatorialSample` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)


# Discrete combinatorial library classes:
class DiscreteCombinatorialSample(CompositeSystem):
    """
    A base section for any sample of a discrete combinatorial library.
    """

    m_def = Section()

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `CombinatorialSample` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)


class DiscreteCombinatorialSampleReference(CompositeSystemReference):
    """
    A section containing a reference to a discrete combinatorial sample entry.
    """

    m_def = Section(
        label_quantity='sample_number',
    )
    sample_number = Quantity(
        type=int,
        description="""
        A unique number for this sample of the combinatorial library.
        """,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
        ),
    )
    reference = Quantity(
        type=DiscreteCombinatorialSample,
        description="""
        The reference to the combinatorial sample entry.
        """,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
            label='Sample Reference',
        ),
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `CombinatorialSampleReference` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)


class DiscreteCombinatorialLibrary(Collection):
    """
    A base section for a discrete combinatorial library.
    """

    m_def = Section()
    lab_id = Quantity(
        type=str,
        description="""
        A unique human readable ID for the combinatorial library.
        """,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity, label='Library ID'
        ),
    )
    entities = SubSection(
        section_def=DiscreteCombinatorialSampleReference,
        description="""
        All the investigated samples of the combinatorial library.
        """,
        repeats=True,
        a_eln=ELNAnnotation(label='Samples'),
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `DiscreteCombinatorialLibrary` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)


m_package.__init_metainfo__()
