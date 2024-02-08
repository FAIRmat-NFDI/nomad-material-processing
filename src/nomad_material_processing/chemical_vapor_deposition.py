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
    CompositeSystem,
    PureSubstanceSection,
    ReadableIdentifiers,
)
from nomad_material_processing import (
    SampleDeposition,
)

from nomad_material_processing.vapor_deposition import (
    VaporRate,
    DepositionRate,
    EvaporationSource,
    VaporDepositionSource,
    SubstrateSetup,
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

m_package = Package(name="Chemical Vapor Deposition")


class CVDEvaporationSource(EvaporationSource):
    pass


class Bubbler(CVDEvaporationSource):
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
        description="Temperature of the bubbler, used to calculate the precursor paartial pressure.",
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
        section_def=VaporRate,
        description="""
        The rate of the material being evaporated (mol/time).
        """,
    )
    deposition_rate = SubSection(
        section_def=DepositionRate,
        description="""
        The deposition rate of the material onto the substrate (mol/area/time).
        """,
    )


class GrowthRate(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x="process_time",
            y="rate",
        ),
    )
    rate = Quantity(
        type=float,
        unit="meter/second",
        shape=["*"],
    )
    process_time = Quantity(
        type=float,
        unit="second",
        shape=["*"],
    )
    measurement_type = Quantity(
        type=MEnum(
            "Assumed",
            "RHEED",
            "Reflectance",
        )
    )


class SubstrateTemperature(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x="process_time",
            y="temperature",
        ),
    )
    temperature = Quantity(
        type=float,
        unit="kelvin",
        shape=["*"],
    )
    process_time = Quantity(
        type=float,
        unit="second",
        shape=["*"],
    )
    measurement_type = Quantity(
        type=MEnum(
            "Heater thermocouple",
            "Pyrometer",
            "Assumed",
        )
    )


class SampleParameters(PlotSection, ArchiveSection):
    m_def = Section(
        a_plotly_graph_object={
            "data": {"x": "temperature/process_time", "y": "temperature/temperature"},
            "layout": {"title": {"text": "Plotly Graph Object"}},
            "label": "Plotly Graph Object",
            "index": 1,
        },
    )
    growth_rate = SubSection(
        section_def=GrowthRate,
        description="""
        The growth rate of the thin film (length/time).
        Measured by in-situ RHEED or Reflection or assumed.
        """,
    )
    temperature = SubSection(
        section_def=SubstrateTemperature,
    )
    layer = SubSection(
        description="""
        The thin film that is being created during this step.
        """,
        section_def=ThinFilmReference,
    )
    substrate = SubSection(
        description="""
        The thin film stack that is being evaporated on.
        """,
        section_def=ThinFilmStackReference,
    )


class Pressure(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x="process_time",
            y="pressure",
        ),
    )
    pressure = Quantity(
        type=float,
        unit="pascal",
        shape=["*"],
    )
    process_time = Quantity(
        type=float,
        unit="second",
        shape=["*"],
    )


class GasFlow(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x="process_time",
            y="flow",
        ),
    )
    gas = SubSection(
        section_def=PureSubstanceSection,
    )
    flow = Quantity(
        type=float,
        unit="meter ** 3 / second",
        shape=["*"],
    )
    process_time = Quantity(
        type=float,
        unit="second",
        shape=["*"],
    )


class SubstrateHeater(ArchiveSection):
    pass


class ChamberEnvironment(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x="pressure/process_time",
            y="pressure/pressure",
        ),
    )
    gas_flow = SubSection(
        section_def=GasFlow,
        repeats=True,
    )
    pressure = SubSection(
        section_def=Pressure,
    )
    heater = SubSection(
        section_def=SubstrateHeater,
    )


class VaporDepositionStep(ActivityStep):
    """
    A step of any vapor deposition process.
    """

    m_def = Section()
    creates_new_thin_film = Quantity(
        type=bool,
        description="""
        Whether or not this step creates a new thin film.
        """,
        default=False,
        a_eln=ELNAnnotation(
            component="BoolEditQuantity",
        ),
    )
    duration = Quantity(
        type=float,
        unit="second",
    )
    sources = SubSection(
        section_def=VaporDepositionSource,
        repeats=True,
    )
    sample_parameters = SubSection(
        section_def=SampleParameters,
        repeats=True,
    )
    environment = SubSection(
        section_def=ChamberEnvironment,
    )

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        """
        The normalizer for the `VaporDepositionStep` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super(VaporDepositionStep, self).normalize(archive, logger)


class VaporDeposition(SampleDeposition):
    """
    VaporDeposition is a general class that encompasses both Physical Vapor Deposition
    (PVD) and Chemical Vapor Deposition (CVD).
    It involves the deposition of material from a vapor phase to a solid thin film or
    coating onto a substrate.
     - material sources:
       Both PVD and CVD involve a source material that is transformed into a vapor phase.
       In PVD, the source material is physically evaporated or sputtered from a solid
       target.
       In CVD, gaseous precursors undergo chemical reactions to produce a solid material
       on the substrate.
     - substrate:
       The substrate is the material onto which the thin film is deposited.
     - environment:
       The process typically takes place in a controlled environment.
       The deposition is usually affected by the pressure in the chamber.
       For some processes additional background gasses are also added.
    """

    m_def = Section(
        links=[
            "http://purl.obolibrary.org/obo/CHMO_0001314",
            "http://purl.obolibrary.org/obo/CHMO_0001356",
        ],
        a_plot=[
            dict(
                x="steps/:/environment/pressure/process_time",
                y="steps/:/environment/pressure/pressure",
            ),
        ],
    )
    steps = SubSection(
        description="""
        The steps of the deposition process.
        """,
        section_def=VaporDepositionStep,
        repeats=True,
    )

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        """
        The normalizer for the `VaporDeposition` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super(VaporDeposition, self).normalize(archive, logger)


m_package.__init_metainfo__()