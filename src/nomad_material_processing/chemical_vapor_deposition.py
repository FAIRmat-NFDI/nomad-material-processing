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

from nomad.datamodel.data import (
    ArchiveSection,
)
from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure

from nomad.datamodel.metainfo.basesections import (
    PubChemPureSubstanceSection,
)
from nomad_material_processing import (
    TimeSeries,
)
from nomad_material_processing.vapor_deposition import (
    VaporRate,
    EvaporationSource,
    VaporDepositionSource,
)
from nomad_material_processing import (
    TimeSeries,
)


if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name="Chemical Vapor Deposition")


class Pressure(TimeSeries):
    m_def = Section(
        a_plot=dict(
            x="process_time",
            y="pressure",
        ),
    )
    set_value = Quantity(
        type=float,
        description="FILL THE DESCRIPTION",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "mbar"},
        unit="pascal",
    )
    value = Quantity(
        type=float,
        unit="pascal",
        shape=["*"],
    )
    time = Quantity(
        type=float,
        unit="second",
        shape=["*"],
    )


class Temperature(TimeSeries):
    """
    Generic Temperature monitoring
    """

    m_def = Section(
        label_quantity="set_value",
        a_plot=dict(
            x="process_time",
            y="temperature",
        ),
    )
    measurement_type = Quantity(
        type=MEnum(
            "Heater thermocouple",
            "Pyrometer",
            "Assumed",
        ),
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.EnumEditQuantity,
        ),
    )
    set_value = Quantity(
        type=float,
        description="The value scalar set for this parameter.",
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
            defaultDisplayUnit="celsius",
        ),
        unit="kelvin",
    )
    value = Quantity(
        type=float,
        description="The value array detected in time for temperature.",
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
            defaultDisplayUnit="celsius",
        ),
        unit="kelvin",
    )
    time = Quantity(
        type=float,
        description="The time array when parameter is detected.",
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
            defaultDisplayUnit="minute",
        ),
        unit="second",
    )


class Rotation(TimeSeries):
    """
    Rotation
    """

    m_def = Section(label_quantity="set_value")

    set_value = Quantity(
        type=float,
        description="The value scalar set for this parameter.",
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
            defaultDisplayUnit="rpm",
        ),
        unit="rpm",
    )
    value = Quantity(
        type=float,
        description="FILL THE DESCRIPTION",
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
            defaultDisplayUnit="rpm",
        ),
        unit="rpm",
    )
    time = Quantity(
        type=float,
        description="The time array when parameter is detected.",
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
            defaultDisplayUnit="minute",
        ),
        unit="second",
    )


class CVDGasFlow(TimeSeries):  # from GAS FLOW in VD module
    """
    Gas Flow
    """

    set_value = Quantity(
        type=float,
        description="The value scalar set for this parameter.",
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
            defaultDisplayUnit="meter ** 3 / second",
        ),
        unit="meter ** 3 / second",
    )
    value = Quantity(
        type=float,
        description="FILL THE DESCRIPTION",
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
            defaultDisplayUnit="meter ** 3 / second",
        ),
        unit="meter ** 3 / second",
    )
    time = Quantity(
        type=float,
        description="The time array when parameter is detected.",
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
            defaultDisplayUnit="minute",
        ),
        unit="second",
    )


class CVDEvaporationSource(EvaporationSource):
    pass


class BubblerEvaporator(CVDEvaporationSource):
    """
    Delivers precursor materials to the reaction chamber.
    It serves as a mechanism for introducing volatile liquid or solid precursors into the gas phase,
    where they can react and deposit onto a substrate surface to form thin films or coatings.

    Key components:
        - Bubbler Vessel: This vessel holds the precursor material.
        - Heating Element: To facilitate vaporization.
        - Gas Inlet and Outlet: Gas delivery system via gas inlet and outlet ports.
        - Temperature Control: Maintain the vapor pressure of the precursor at the desired level.

    Operation:
        - Loading Precursor: The precursor material is loaded into the bubbler vessel
        - Heating: The heating element is activated to form a vapor phase above the liquid or solid.
        - Gas Flow: Carrier gas is bubbled through the precursor material.
        - Transport: The precursor vapor is delivered to the reaction chamber.
          The precursor undergoes decomposition or reaction on the substrate surface,
          leading to thin film growth.
    """

    temperature = Quantity(
        type=float,
        description="Temperature of the bubbler, used to calculate the precursor partial pressure.",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit="mbar",
        ),
        unit="mbar",
    )
    pressure = Quantity(
        type=float,
        description="The back-pressur ein the tube carrying the bubbler material.",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit="mbar",
        ),
        unit="mbar",
    )
    partial_pressure = Quantity(
        type=float,
        description="Calculated with the August-Antoine equation: 1.33322*10^[(A-B)/T].",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit="mbar",
        ),
        unit="mbar",
    )
    dilution = Quantity(
        type=float,
        description="ONLY FOR DOPING PRECURSOR",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit="cm ** 3 / minute",
        ),
        unit="cm ** 3 / minute",
    )
    source = Quantity(
        type=float,
        description="ONLY FOR DOPING PRECURSOR",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit="cm ** 3 / minute",
        ),
        unit="cm ** 3 / minute",
    )
    inject = Quantity(
        type=float,
        description="ONLY FOR DOPING PRECURSOR",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit="cm ** 3 / minute",
        ),
        unit="cm ** 3 / minute",
    )


class FlashEvaporator(CVDEvaporationSource):
    """
    Flash Evaporator Unit: It typically comprises a reservoir where the metalorganic precursor, often in liquid form, is stored.

    Components:

    - Heating Mechanism.
    - Carrier Gas Inlet.
    - Precursor Delivery Pathway.
    - Temperature Control System.

    Operation:

    - Loading of Precursor.
    - Vaporization Process.
    - Carrier Gas Introduction.
    - Transport to Reaction Chamber.
    - Temperature Regulation.
    """

    pressure = SubSection(
        section_def=Pressure,
    )


class CVDVaporRate(VaporRate):
    m_def = Section(
        a_plot=dict(
            x="process_time",
            y="rate",
        ),
    )
    measurement_type = Quantity(
        type=MEnum(
            "Assumed",
            "Mass Flow Controller",
        ),
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.EnumEditQuantity,
        ),
    )
    mass_flow_controller = Quantity(
        type=float,
        description="Flux of material with mass flow controller.",
        a_eln={
            "component": "NumberEditQuantity",
            "defaultDisplayUnit": "cm ** 3 / minute",
        },
        unit="cm ** 3 / minute",
    )
    rate = Quantity(
        type=float,
        description="FILL THE DESCRIPTION",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit="mol / minute",
        ),
        shape=["*"],
        unit="mol / minute",
        label="Molar flux",
    )
    process_time = Quantity(
        type=float,
        unit="second",
        shape=["*"],
    )


class CVDSource(VaporDepositionSource):
    m_def = Section(
        a_plot=dict(
            x="deposition_rate/process_time",
            y="deposition_rate/rate",
        ),
    )
    name = Quantity(
        type=str,
        description="""
        A short and descriptive name for this source.
        """,
    )
    carrier_gas = SubSection(
        section_def=PubChemPureSubstanceSection,
    )
    carrier_push_valve = SubSection(
        section_def=CVDGasFlow,
        description="""
        The flow of the push valve.
        """,
    )
    carrier_purge_valve = SubSection(
        section_def=CVDGasFlow,
        description="""
        The flow of the purge valve.
        """,
    )
    vapor_source = SubSection(
        section_def=CVDEvaporationSource,
        description="""
        Example: A heater, a filament, a laser, a bubbler, etc.
        """,
    )
    vapor_rate = SubSection(
        section_def=CVDVaporRate,
        description="""
        The rate of the material being evaporated (mol/time).
        """,
    )


m_package.__init_metainfo__()
