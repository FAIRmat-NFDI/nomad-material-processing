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
)

from nomad_material_processing.vapor_deposition import (
    VaporRate,
    EvaporationSource,
    VaporDepositionSource,
    VaporDepositionStep,
    VaporDeposition,
)

from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name="Chemical Vapor Deposition")


class CVDEvaporationSource(EvaporationSource):
    pass


class CVDBubbler(CVDEvaporationSource):
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


class CVDVaporRate(VaporRate):
    m_def = Section(
        a_plot=dict(
            x="process_time",
            y="rate",
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
    measurement_type = Quantity(
        type=MEnum(
            "Assumed",
            "Mass Flow Controller",
        )
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
