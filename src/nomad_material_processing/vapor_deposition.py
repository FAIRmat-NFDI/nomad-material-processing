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
    ThinFilmStackReference,
    ThinFilmStack,
    ThinFilmReference,
    ThinFilm,
)

from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name="Vapor Deposition")


class MaterialEvaporationRate(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x="process_time",
            y="rate",
        ),
    )
    rate = Quantity(
        type=float,
        unit="mol/meter ** 2/second",
        shape=["*"]
    )
    process_time = Quantity(
        type=float,
        unit="second",
        shape=["*"],
    )
    measurement_type = Quantity(
        type=MEnum(
            "Assumed",
            "Quartz Crystal Microbalance",
            "RHEED",
            "Mass Flow Controller",
        )
    )


class SourceMaterial(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x="rate/process_time",
            y="rate/rate",
        ),
    )
    material = Quantity(
        description="""
        The material that is being evaporated.
        """,
        type=CompositeSystem,
    )
    rate = SubSection(
        section_def=MaterialEvaporationRate,
    )


class SourcePower(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x="process_time",
            y="power",
        ),
    )
    power = Quantity(
        type=float,
        unit="watt",
        shape=["*"],
    )
    process_time = Quantity(
        type=float,
        unit="second",
        shape=["*"],
    )


class EvaporationSource(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x="power/process_time",
            y="power/power",
        ),
    )
    power = SubSection(
        section_def=SourcePower,
    )


class VaporDepositionSource(ArchiveSection):
    m_def = Section(
        a_plot=[
            dict(
                x=[
                    "evaporation_source/power/process_time",
                    "material_source/rate/process_time",
                ],
                y=[
                    "evaporation_source/power/power",
                    "material_source/rate/rate",
                ],
            ),
        ],
    )
    name = Quantity(
        type=str,
        description="""
        A short and descriptive name for this source.
        """,
    )
    material_source = SubSection(
        section_def=SourceMaterial,
    )
    evaporation_source = SubSection(
        section_def=SourceEvaporation,
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
        unit="kelvin", ########### the unit can change from user to user ###############
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
        )
    )


class SubstrateSetup(PlotSection, ArchiveSection):
    m_def = Section(
        a_plotly_graph_object={
            "data": {"x": "temperature/process_time", "y": "temperature/temperature"},
            "layout": {"title": {"text": "Plotly Graph Object"}},
            "label": "Plotly Graph Object",
            "index": 1,
        },
    )

    # which of the folllwoing two?

    thin_film = Quantity(
        description="""
        The thin film that is being created during this step.
        """,
        type=ThinFilm,
    )
    layers = SubSection(
        description="""
        An ordered list (starting at the substrate) of the thin films making up the
        thin film stacks.
        """,
        section_def=ThinFilmReference,
        repeats=True,
    )
    temperature = SubSection(
        section_def=SubstrateTemperature,
    )
    heater = Quantity(
        type=MEnum(
            "No heating",
            "Halogen lamp",
            "Filament",
            "Resistive element",
            "CO2 laser",
        )
    )
    distance_to_source = Quantity(
        type=float,
        unit="meter",
        description="""
        The distance between the substrate and all the sources.
        In the case of multiple sources, the distances are listed in the same order as the
        sources are listed in the parent `VaporDepositionStep` section.
        """,
        shape=["*"],
    )
    substrate_specimen = SubSection(
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
        unit="second"
    )
    sources = SubSection(
        section_def=VaporDepositionSource,
        repeats=True,
    )
    substrate = SubSection(
        section_def=SubstrateSetup,  
        repeats=True,
    )
    environment = SubSection(
        section_def=ChamberEnvironment,
    )

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        """
        The normalizer for the `PVDStep` class.

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
                http://purl.obolibrary.org/obo/CHMO_0001314,
                http://purl.obolibrary.org/obo/CHMO_0001356,
        ],
        a_plot=[
            dict(
                x="steps/:/environment/pressure/process_time",
                y="steps/:/environment/pressure/pressure",
            ),
            dict(
                x="steps/:/source/:/evaporation_source/power/process_time",
                y="steps/:/source/:/evaporation_source/power/power",
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
