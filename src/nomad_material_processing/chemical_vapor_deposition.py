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
    EvaporationSource,
    VaporDepositionSource,

)


if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name="Chemical Vapor Deposition")


class Temperature(TimeSeries):
    """
    Generic Temperature monitoring
    """

    m_def = Section(
        label_quantity="set_value",
        a_plot=dict(
            x="time",
            y="value",
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

    m_def = Section(label_quantity="set_value")


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


class Pressure(TimeSeries):
    """
    Generic Pressure monitoring
    """
    m_def = Section(
        a_plot=dict(
            x="time",
            y="value",
        ),
    )
    set_value = Quantity(
        type=float,
        description="The value scalar set for this parameter.",
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
            defaultDisplayUnit="mbar",
        ),
        unit="pascal",
    )
    value = Quantity(
        type=float,
        description="FILL THE DESCRIPTION",
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
            defaultDisplayUnit="mbar",
        ),
        unit="pascal",
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


class PartialVaporPressure(Pressure):
    """
    The Partial Vapor Pressure (or Equilibrium Vapor Pressure), p, is the pressure exerted 
    by a vapor in thermodynamic equilibrium with its condensed phases (solid or liquid) 
    at a given temperature in a closed system. 
    
    It can be approximately calculated by the semiempirical Antoine equation.
    It is a relation between the vapor pressure and temperature of pure substances.
    log10(p) = A - [B / (T + C)]
    https://en.wikipedia.org/wiki/Vapor_pressure
    The August-Antoine equation is a simplified version of the Antoine equation,
    sometimes used to calculate Partial Vapor Pressure. 
    This assumes a temperature-independent heat of vaporization, i.e., C = 0. 
    https://en.wikipedia.org/wiki/Antoine_equation
    """
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


class MassFlowRate(TimeSeries):
    """
    Mass flow rate is the mass of a substance which passes per unit of time.

    It is measured with a Mass Flow Controller (MFC).
    It is a mass flow meter (i.e. the sensor) 
    combined with control valve and feedback electronics between sensor and valve. 
    Why would you control mass flow instead of volume flow?
    Simply because in many research and production processes, 
    the important variable is mass and not volume.

    To meet users' preferences for expressing compressible gas flow as volume flow anyway, 
    conditions are agreed upon under which mass flow is converted into volume flow.
    These "normal" reference conditions are a temperature of 0 celsius
    and an absolute pressure of 1 atm.
    For this reason, the unit of this class are sccm - 
    standard cubic centimeters per minute.
    """
    measurement_type = Quantity(
        type=str,
        default="Mass Flow Controller",
    )
    set_value = Quantity(
        type=float,
        description="Mass flow rate set with mass flow controller.",
        a_eln={
            "component": "NumberEditQuantity",
            "defaultDisplayUnit": "cm ** 3 / minute",
        },
        unit="cm ** 3 / minute",
        shape=["*"],
    )
    value = Quantity(
        type=float,
        description="Mass flow rate read with mass flow controller.",
        a_eln={
            "component": "NumberEditQuantity",
            "defaultDisplayUnit": "cm ** 3 / minute",
        },
        unit="cm ** 3 / minute",
        shape=["*"],
    )


class MolarFlowRate(TimeSeries):  # from VAPOR RATE in VD module
    """
    Molar flow rate is the amount of a substance which passes per unit of time.

    The article cited below explains the equation used in MOVPE to calculate the molar flow rate.

    F_r = F_c*P_r / (P_0 - P_r)

    where:

    F_r is the molar flow rate,
    F_c is the carrier gas flow rate,
    P_r is the partial vapor pressure of the precursor,
    P_0 is the total pressure exiting the bubbler.

    Reference:
    Journal of Vacuum Science & Technology A 8, 800 (1990); doi: 10.1116/1.576921

    """
    set_value = Quantity(
        type=float,
        description="Set molar flow rate",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit="mol / minute",
        ),
        shape=["*"],
        unit="mol / minute",
        label="Molar flux",
    )
    value = Quantity(
        type=float,
        description="Read molar flow rate",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit="mol / minute",
        ),
        shape=["*"],
        unit="mol / minute",
    )


class VolumeFlowRate(TimeSeries):  # from GAS FLOW in VD module
    """
    the volume of fluid that is passing through a given cross sectional area per unit time
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


class VaporRate(TimeSeries):  # from VAPOR RATE in VD module
    measurement_type = Quantity(
        type=MEnum(
            "Assumed",
            "Mass Flow Controller",
        ),
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.EnumEditQuantity,
        ),
    )
    set_value = Quantity(
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
    value = Quantity(
        type=float,
        description="FILL THE DESCRIPTION",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit="mol / minute",
        ),
        shape=["*"],
        unit="mol / minute",
    )
    time = Quantity(
        type=float,
        unit="second",
        shape=["*"],
    )


class MassFlowController(TimeSeries):
    """
    Mass flow rate is the mass of a substance which passes per unit of time.
    It is measured with a Mass Flow Controller (MFC).

    When the parameter recorded is not yet better specified, we use this class.
    """

    set_value = Quantity(
        type=float,
        description="Flux of material with mass flow controller.",
        a_eln={
            "component": "NumberEditQuantity",
            "defaultDisplayUnit": "cm ** 3 / minute",
        },
        unit="cm ** 3 / minute",
    )
    value = Quantity(
        type=float,
        description="Flux of material with mass flow controller.",
        a_eln={
            "component": "NumberEditQuantity",
            "defaultDisplayUnit": "cm ** 3 / minute",
        },
        unit="cm ** 3 / minute",
    )
    time = Quantity(
        type=float,
        unit="second",
        shape=["*"],
    )


class CVDEvaporationSource(EvaporationSource):
    pressure = SubSection(
        section_def=Pressure,
    )
    temperature = SubSection(
        section_def=Temperature,
    )


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

    precursor_partial_pressure = SubSection(
        section_def=PartialVaporPressure,
    )

    carrier_gas_flow = SubSection(
        section_def=MassFlowRate,
        description="""
        The rate of the carrier gas entering the.
        """,
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

    pass


class CVDSource(VaporDepositionSource):
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
        section_def=VolumeFlowRate,
        description="""
        The flow of the push valve.
        """,
    )
    carrier_purge_valve = SubSection(
        section_def=VolumeFlowRate,
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
        section_def=VaporRate,
        description="""
        The rate of the material being evaporated (mol/time).
        """,
    )


m_package.__init_metainfo__()
