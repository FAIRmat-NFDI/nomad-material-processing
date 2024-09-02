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

from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
)
from nomad.metainfo import (
    Quantity,
    SchemaPackage,
    Section,
    SubSection,
)

from nomad_material_processing.general import (
    TimeSeries,
)
from nomad_material_processing.vapor_deposition.pvd.general import (
    PhysicalVaporDeposition,
    PVDEvaporationSource,
    PVDSource,
    PVDStep,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad.config import config

m_package = SchemaPackage(name='Thermal Evaporation')

configuration = config.get_plugin_entry_point(
    'nomad_material_processing.vapor_deposition.pvd:thermal_schema',
)


class ThermalEvaporationHeaterTemperature(TimeSeries):
    """
    The temperature of the heater during the deposition process.
    """

    m_def = Section(
        a_plot=dict(
            # x=['time', 'set_time'],
            # y=['value', 'set_value'],
            x='time',
            y='value',
        ),
    )
    value = Quantity(
        type=float,
        unit='kelvin',
        shape=['*'],
    )
    set_value = Quantity(
        type=float,
        description='The set value(s) (i.e. the intended values) set.',
        shape=['*'],
        unit='kelvin',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            label='Set value',
            defaultDisplayUnit='celsius',
        ),
    )


class ThermalEvaporationHeater(PVDEvaporationSource):
    m_def = Section(
        a_plot=dict(
            x=[
                'temperature/time',
                'power/time',
            ],
            y=[
                'temperature/value',
                'power/value',
            ],
            lines=[
                dict(
                    mode='lines',
                    line=dict(
                        color='rgb(25, 46, 135)',
                    ),
                ),
                dict(
                    mode='lines',
                    line=dict(
                        color='rgb(0, 138, 104)',
                    ),
                ),
            ],
        ),
    )
    temperature = SubSection(
        section_def=ThermalEvaporationHeaterTemperature,
    )


class ThermalEvaporationSource(PVDSource):
    m_def = Section(
        a_plot=dict(
            x=[
                'impinging_flux/:/time',
                'vapor_source/temperature/time',
            ],
            y=[
                'impinging_flux/:/value',
                'vapor_source/temperature/value',
            ],
            lines=[
                dict(
                    mode='lines',
                    line=dict(
                        color='rgb(25, 46, 135)',
                    ),
                ),
                dict(
                    mode='lines',
                    line=dict(
                        color='rgb(0, 138, 104)',
                    ),
                ),
            ],
        ),
    )
    vapor_source = SubSection(
        section_def=ThermalEvaporationHeater,
    )


class ThermalEvaporationStep(PVDStep):
    m_def = Section(
        a_plot=[
            dict(
                x='sources/:/impinging_flux/:/time',
                y='sources/:/impinging_flux/:/value',
            ),
            dict(
                x='sources/:/vapor_source/temperature/time',
                y='sources/:/vapor_source/temperature/value',
            ),
            dict(
                x='sources/:/vapor_source/power/time',
                y='sources/:/vapor_source/power/value',
            ),
        ],
    )
    sources = SubSection(
        section_def=ThermalEvaporationSource,
        repeats=True,
    )


class ThermalEvaporation(PhysicalVaporDeposition):
    """
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
    """

    m_def = Section(
        links=['http://purl.obolibrary.org/obo/CHMO_0001360'],
        a_plot=[
            dict(
                x='steps/:/sources/:/impinging_flux/:/time',
                y='steps/:/sources/:/impinging_flux/:/value',
            ),
            dict(
                x='steps/:/sources/:/vapor_source/temperature/time',
                y='steps/:/sources/:/vapor_source/temperature/value',
            ),
            dict(
                x='steps/:/environment/pressure/time',
                y='steps/:/environment/pressure/value',
                layout=dict(
                    yaxis=dict(
                        type='log',
                    ),
                ),
            ),
        ],
    )
    method = Quantity(
        type=str,
        default='Thermal Evaporation',
    )
    steps = SubSection(
        description="""
        The steps of the deposition process.
        """,
        section_def=ThermalEvaporationStep,
        repeats=True,
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `ThermalEvaporation` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)


m_package.__init_metainfo__()
