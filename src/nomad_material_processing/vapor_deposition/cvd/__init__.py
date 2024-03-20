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
    MolarFlowRate,
    VolumetricFlowRate,
    Pressure,
    Temperature,

)


if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name="Chemical Vapor Deposition")


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


class BubblerMolarFlowRate(MolarFlowRate):
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
    value = MolarFlowRate.value.m_copy()
    set_value = MolarFlowRate.set_value.m_copy()
    set_value.a_eln.defaultDisplayUnit = "mol/minute"


class CVDEvaporationSource(EvaporationSource):
    pressure = SubSection(
        section_def=Pressure,
    )
    temperature = SubSection(
        section_def=Temperature,
    )
    total_flow_rate = SubSection(
        section_def=VolumetricFlowRate,
        description="""
        The total flow rate exiting the source. 
        It can be the sum of precursor and carrier gas or only a gas, 
        depending on the nature of the source.
        """,
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
    carrier_gas = SubSection(
        section_def=PubChemPureSubstanceSection,
    )
    carrier_push_flow_rate = SubSection(
        section_def=VolumetricFlowRate,
        description="""
        The flow through the push valve.
        """,
    )
    carrier_purge_flow_rate = SubSection(
        section_def=VolumetricFlowRate,
        description="""
        The flow through the purge valve.
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
    carrier_gas = SubSection(
        section_def=PubChemPureSubstanceSection,
    )
    carrier_push_flow_rate = SubSection(
        section_def=VolumetricFlowRate,
        description="""
        The flow through the push valve.
        """,
    )
    carrier_purge_flow_rate = SubSection(
        section_def=VolumetricFlowRate,
        description="""
        The flow through the purge valve.
        """,
    )
    pass


class GasSupply(CVDEvaporationSource):
    """
    In chemical vapor deposition (CVD), the gas supply plays a critical role 
    in providing the necessary precursor molecules for the deposition process. 
    These precursor gases are typically delivered to the reaction chamber 
    through various methods depending on the specific setup and requirements 
    of the CVD process.
    """
    pass


class GasLine(GasSupply):
    """
    Gas lines are used to transport the precursor gases from their source to the reaction chamber. 
    These lines are often made of materials that are compatible with the precursor gases 
    and can withstand the process conditions. 
    They may also be heated or insulated to maintain the gases at the desired temperature 
    and prevent condensation or undesired reactions within the lines.
    """
    pass


class GasCylinder(GasSupply):
    """
    Contains the precursor gases under pressure. 
    These cylinders are connected to the CVD chamber through a system of valves, 
    regulators, and tubing. 
    The flow rate of each gas can be controlled precisely using flow meters 
    or mass flow controllers to achieve the desired deposition conditions.
    """
    pass


class CVDSource(VaporDepositionSource):
    vapor_source = SubSection(
        section_def=CVDEvaporationSource,
        description="""
        Example: A heater, a filament, a laser, a bubbler, etc.
        """,
    )


m_package.__init_metainfo__()
