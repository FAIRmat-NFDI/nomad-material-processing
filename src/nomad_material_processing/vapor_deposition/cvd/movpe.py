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

from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
    SectionProperties,
)
from nomad.datamodel.metainfo.plot import PlotSection
from nomad.metainfo import (
    Quantity,
    SchemaPackage,
    Section,
    SubSection,
)

from nomad_material_processing.vapor_deposition.cvd.general import (
    ChemicalVaporDeposition,
    CVDSource,
    CVDStep,
    Rotation,
)
from nomad_material_processing.vapor_deposition.general import (
    ChamberEnvironment,
    Pressure,
    SampleParameters,
    SubstrateHeater,
    Temperature,
    VolumetricFlowRate,
)

if TYPE_CHECKING:
    pass

from nomad.config import config

m_package = SchemaPackage()

configuration = config.get_plugin_entry_point(
    'nomad_material_processing.vapor_deposition.cvd:movpe_schema',
)


class FilamentTemperature(Temperature):
    """
    Temperature of a heated element used to keep the substrate hot.
    """

    value = Quantity(
        type=float,
        unit='kelvin',
        a_eln=ELNAnnotation(
            defaultDisplayUnit='celsius',
        ),
        shape=['*'],
    )
    set_value = Quantity(
        type=float,
        description='The set value(s) (i.e. the intended values) set.',
        shape=['*'],
        unit='kelvin',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='celsius',
            label='Set value',
        ),
    )


class MovpeSampleParameters(SampleParameters):
    filament_temperature = SubSection(
        section_def=FilamentTemperature,
    )


class MovpeChamberEnvironment(ChamberEnvironment):
    uniform_gas_flow_rate = SubSection(
        section_def=VolumetricFlowRate,
    )
    pressure = SubSection(
        section_def=Pressure,
    )
    throttle_valve = SubSection(
        section_def=Pressure,
    )
    rotation = SubSection(
        section_def=Rotation,
    )
    heater = SubSection(
        section_def=SubstrateHeater,
    )


class StepMovpe(CVDStep, PlotSection):
    """
    Growth step for MOVPE
    """

    m_def = Section(
        a_eln=None,
    )
    sample_parameters = SubSection(
        section_def=MovpeSampleParameters,
        repeats=True,
    )
    sources = SubSection(
        section_def=CVDSource,
        repeats=True,
    )
    environment = SubSection(
        section_def=MovpeChamberEnvironment,
    )


class Movpe(ChemicalVaporDeposition, EntryData):
    """
    Metal-organic Vapor Phase Epitaxy (MOVPE) is a chemical vapor deposition method
    used to produce single- or multi-layered thin films.
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'method',
                    'datetime',
                    'end_time',
                    'duration',
                ],
            ),
        ),
        label_quantity='lab_id',
    )
    method = Quantity(
        type=str,
        default='MOVPE',
    )
    steps = SubSection(
        section_def=StepMovpe,
        repeats=True,
    )


m_package.__init_metainfo__()
