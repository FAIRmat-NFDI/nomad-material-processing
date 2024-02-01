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
from nomad.datamodel.data import (
    ArchiveSection,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
)
from nomad.datamodel.metainfo.basesections import (
    ActivityStep,
    CompositeSystem,
    PureSubstanceSection,
    ReadableIdentifiers,
)
from nomad_material_processing import (
    SampleDeposition,
    ThinFilmStack,
    ThinFilm,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name='Vapor Deposition')


class MaterialEvaporationRate(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x='process_time',
            y='rate',
        ),
    )
    rate = Quantity(
        type=float,
        unit='mol/meter ** 2/second',
        shape=['*'],
        a_eln=ELNAnnotation(
            defaultDisplayUnit='micromol/m ** 2/second',
        ),
    )
    flow = Quantity(   ############### I need this, let's discuss if it must be here or in CVD module
        type=float,
        a_eln=ELNAnnotation(
            defaultDisplayUnit='micromol/m ** 2/second',
        ),
        unit="cm ** 3 / minute",
    )
    process_time = Quantity(
        type=float,
        unit='second',
        shape=['*'],
        a_eln=ELNAnnotation(
            defaultDisplayUnit='second',
        ),
    )
    measurement_type = Quantity(
        type=MEnum(
            'Assumed',
            'Quartz Crystal Microbalance',
            'RHEED',
            'Mass Flow Controller', ######################### added 
        )
    )


class MaterialSource(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x='rate/process_time',
            y='rate/rate',
        ),
    )
    material = Quantity(
        description='''
        The material that is being evaporated.
        ''',
        type=CompositeSystem,
    )
    rate = SubSection(
        section_def=MaterialEvaporationRate,
    )


class SourcePower(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x='process_time',
            y='power',
        ),
    )
    power = Quantity(
        type=float,
        unit='watt',
        shape=['*'],
        a_eln=ELNAnnotation(
            defaultDisplayUnit='watt',
        ),
    )
    process_time = Quantity(
        type=float,
        unit='second',
        shape=['*'],
        a_eln=ELNAnnotation(
            defaultDisplayUnit='second',
        ),
    )


class EvaporationSource(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x='power/process_time',
            y='power/power',
        ),
    )
    power = SubSection(
        section_def=SourcePower,   ##### I'll check better which are the parametrs recorded for CVD souces, and, consequantly, what can remain here and what will go to PVD and CVD
    )


class Source(ArchiveSection):
    m_def = Section(
        a_plot=[
            dict(
                x=[
                    'evaporation_source/power/process_time',
                    'material_source/rate/process_time',
                ],
                y=[
                    'evaporation_source/power/power',
                    'material_source/rate/rate',
                ]
            ),
        ],
    )
    name = Quantity(
        type=str,
        description='''
        A short and descriptive name for this source.
        '''
    )
    material_source = SubSection(
        section_def=MaterialSource,
    )
    evaporation_source = SubSection(
        section_def=EvaporationSource,
    )



class SubstrateTemperature(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x='process_time',
            y='temperature',
        ),
    )
    temperature = Quantity(
        type=float,
        unit='kelvin',
        shape=['*'],
        a_eln=ELNAnnotation(
            defaultDisplayUnit='celsius',
        ),
    )
    process_time = Quantity(
        type=float,
        unit='second',
        shape=['*'],
        a_eln=ELNAnnotation(
            defaultDisplayUnit='second',
        ),
    )
    measurement_type = Quantity(
        type=MEnum(
            'Heater thermocouple',
            'Pyrometer',
        )
    )


class Substrate(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x='temperature/process_time',
            y='temperature/temperature',
        ),
    )
    substrate = Quantity(
        description='''
        The thin film stack that is being evaporated on.
        ''',
        type=ThinFilmStack,
    )
    thin_film = Quantity(
        description='''
        The thin film that is being created during this step.
        ''',
        type=ThinFilm,
    )
    temperature = SubSection(
        section_def=SubstrateTemperature,
    )
    heater = Quantity(
        type=MEnum(
            'No heating',
            'Halogen lamp',
            'Filament',
            'Resistive element',
            'CO2 laser',
        )
    )
    distance_to_source = Quantity(
        type=float,
        unit='meter',
        shape=['*'],
        # a_eln=ELNAnnotation(
        #     defaultDisplayUnit='millimeter',
        # ),
    )


class Pressure(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x='process_time',
            y='pressure',
        ),
    )
    pressure = Quantity(
        type=float,
        unit='pascal',
        shape=['*'],
        a_eln=ELNAnnotation(
            defaultDisplayUnit='millibar',
        ),
    )
    process_time = Quantity(
        type=float,
        unit='second',
        shape=['*'],
        a_eln=ELNAnnotation(
            defaultDisplayUnit='second',
        ),
    )


class GasFlow(ArchiveSection):
    gas = SubSection(
        section_def=PureSubstanceSection,
    )
    flow = Quantity(
        type=float,
        unit='meter ** 3 / second',
        shape=['*'],
    )
    process_time = Quantity(
        type=float,
        unit='second',
        shape=['*'],
        # a_eln=ELNAnnotation(
        #     defaultDisplayUnit='second',
        # ),
    )


class ChamberEnvironment(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x='pressure/process_time',
            y='pressure/pressure',
        ),
    )
    gas_flow = SubSection(
        section_def=GasFlow,
        repeats=True,
    )
    pressure = SubSection(
        section_def=Pressure,
    )


class VaporDepositionStep(ActivityStep): # physical vapor deposition
    '''
    A step of any physical vapor deposition process.
    '''
    m_def = Section()
    creates_new_thin_film = Quantity(
        type=bool,
        description='''
        Whether or not this step creates a new thin film.
        ''',
        default=False,
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
    )
    duration = Quantity(
        type=float,
        unit='second'
    )
    sources = SubSection(
        section_def=Source,
        repeats=True,
    )
    substrate = SubSection(
        section_def=Substrate,  #### in next commit, I will think and refine better this name and/or structure
        repeats=True,
    )
    environment = SubSection(
        section_def=ChamberEnvironment,
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        '''
        The normalizer for the `PVDStep` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(VaporDepositionStep, self).normalize(archive, logger)


class VaporDeposition(SampleDeposition):   # physical vapor deposition
    '''
    A synthesis technique where vaporized molecules or atoms condense on a surface,
    forming a thin layer. The process is purely physical; no chemical reaction occurs
    at the surface. [database_cross_reference: https://orcid.org/0000-0002-0640-0422]

    Synonyms:
     - PVD
     - physical vapor deposition
    '''
    m_def = Section(
        links=["http://purl.obolibrary.org/obo/CHMO_0001356"],
        a_plot=[
            dict(
                x='steps/:/environment/pressure/process_time',
                y='steps/:/environment/pressure/pressure',
            ),
            dict(
                x='steps/:/source/:/evaporation_source/power/process_time',
                y='steps/:/source/:/evaporation_source/power/power',
            ),
        ],
    )
    steps = SubSection(
        description='''
        The steps of the deposition process.
        ''',
        section_def=VaporDepositionStep,
        repeats=True,
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        '''
        The normalizer for the `PhysicalVaporDeposition` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(VaporDeposition, self).normalize(archive, logger)


m_package.__init_metainfo__()
