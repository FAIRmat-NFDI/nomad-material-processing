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
    Section,
    SubSection,
    Quantity,
    MEnum,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
)

from nomad_material_processing import (
    TimeSeries,
)
from nomad_material_processing.vapor_deposition import (
    EvaporationSource,
    VaporDepositionSource,
    SampleParameters,
    VaporDepositionStep,
    VaporDeposition,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name='Physical Vapor Deposition')


class SourcePower(TimeSeries):
    """
    The power supplied to the source (watt).
    """

    m_def = Section(
        a_plot=dict(
            # x=['time', 'set_time'],
            # y=['value', 'set_value'],
            x='time',
            y='value',
        ),
    )
    value = TimeSeries.value.m_copy()
    value.unit = 'watt'
    set_value = TimeSeries.set_value.m_copy()
    set_value.unit = 'watt'


class PVDEvaporationSource(EvaporationSource):
    m_def = Section(
        a_plot=dict(
            x='power/time',
            y='power/value',
        ),
    )
    power = SubSection(
        section_def=SourcePower,
    )


class ImpingingFlux(TimeSeries):
    """
    The impinging flux of the material onto the substrate (mol/area/time).
    """

    m_def = Section(
        a_plot=dict(
            # x=['time', 'set_time'],
            # y=['value', 'set_value'],
            x='time',
            y='value',
        ),
    )
    measurement_type = Quantity(
        type=MEnum(
            'Assumed',
            'Quartz Crystal Microbalance',
        ),
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.EnumEditQuantity,
        ),
    )
    value = TimeSeries.value.m_copy()
    value.unit = 'mol/meter ** 2/second'
    set_value = TimeSeries.set_value.m_copy()
    set_value.unit = 'mol/meter ** 2/second'


class PVDSource(VaporDepositionSource):
    m_def = Section(
        a_plot=[
            dict(
                x=[
                    'vapor_source/power/time',
                    'impinging_flux/time',
                ],
                y=[
                    'vapor_source/power/value',
                    'impinging_flux/value',
                ],
            ),
        ],
    )
    vapor_source = SubSection(
        section_def=PVDEvaporationSource,
        description="""
        Example: A heater, a filament, a laser, etc.
        """,
    )
    impinging_flux = SubSection(
        section_def=ImpingingFlux,
        description="""
        The deposition rate of the material onto the substrate (mol/area/time).
        """,
        repeats=True,
    )


class PVDSampleParameters(SampleParameters):
    heater = Quantity(
        description="""
        What is the substrate heated by.
        """,
        type=MEnum(
            'No heating',
            'Halogen lamp',
            'Filament',
            'Resistive element',
            'CO2 laser',
        ),
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.EnumEditQuantity,
        ),
    )
    distance_to_source = Quantity(
        type=float,
        unit='meter',
        description="""
        The distance between the substrate and all the sources.
        In the case of multiple sources, the distances are listed in the same order as the
        sources are listed in the parent `VaporDepositionStep` section.
        """,
        shape=['*'],
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
        ),
    )


class PVDStep(VaporDepositionStep):
    """
    A step of any physical vapor deposition process.
    """

    sources = SubSection(
        section_def=PVDSource,
        repeats=True,
    )
    sample_parameters = SubSection(
        section_def=PVDSampleParameters,
        repeats=True,
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `PVDStep` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super(PVDStep, self).normalize(archive, logger)


class PhysicalVaporDeposition(VaporDeposition):
    """
    A synthesis technique where vaporized molecules or atoms condense on a surface,
    forming a thin layer. The process is purely physical; no chemical reaction occurs
    at the surface. [database_cross_reference: https://orcid.org/0000-0002-0640-0422]

    Synonyms:
     - PVD
     - physical vapor deposition
    """

    m_def = Section(
        links=['http://purl.obolibrary.org/obo/CHMO_0001356'],
        a_plot=[
            dict(
                x='steps/:/environment/pressure/time',
                y='steps/:/environment/pressure/value',
            ),
            dict(
                x='steps/:/source/:/vapor_source/power/time',
                y='steps/:/source/:/vapor_source/power/value',
            ),
        ],
    )
    steps = SubSection(
        description="""
        The steps of the deposition process.
        """,
        section_def=PVDStep,
        repeats=True,
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `PhysicalVaporDeposition` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super(PhysicalVaporDeposition, self).normalize(archive, logger)


m_package.__init_metainfo__()
