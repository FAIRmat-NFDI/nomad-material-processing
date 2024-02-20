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
)
from nomad.datamodel.metainfo.basesections import (
    ActivityStep,
    PureSubstanceSection,
    CompositeSystemReference,
)
from nomad.datamodel.metainfo.plot import (
    PlotSection,
)
from nomad.datamodel.metainfo.workflow import (
    Link,
    Task,
)
from nomad_material_processing import (
    SampleDeposition,
    ThinFilmStackReference,
    ThinFilmReference,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name="Vapor Deposition")


class VaporRate(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x="process_time",
            y="rate",
        ),
    )
    rate = Quantity(
        type=float,
        unit="mol/second",
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
            "Mass Flow Controller",
        )
    )


class EvaporationSource(ArchiveSection):
    pass


class VaporDepositionSource(ArchiveSection):
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
    material = SubSection(
        section_def=CompositeSystemReference,
        description="""
        The source of the material that is being evaporated.
        Example: A sputtering target, a powder in a crucible, etc.
        """,
    )
    vapor_source = SubSection(
        section_def=EvaporationSource,
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
            "label": "Measured Temperatures",
            "index": 1,
            "dragmode": "pan",
            "data": {
                "type": "scattergl",
                "line": {"width": 2},
                "marker": {"size": 2},
                "mode": "lines+markers",
                "name": "Temperature",
                "x": "#temperature/process_time",
                "y": "#temperature/temperature",
            },
            "layout": {
                "title": {"text": "Measured Temperature"},
                "xaxis": {
                    "showticklabels": True,
                    "fixedrange": True,
                    "ticks": "",
                    "title": {"text": "Process time [s]"},
                    "showline": True,
                    "linewidth": 1,
                    "linecolor": "black",
                    "mirror": True,
                },
                "yaxis": {
                    "showticklabels": True,
                    "fixedrange": True,
                    "ticks": "",
                    "title": {"text": "Temperature [°C]"},
                    "showline": True,
                    "linewidth": 1,
                    "linecolor": "black",
                    "mirror": True,
                },
                "showlegend": False,
            },
            "config": {
                "displayModeBar": False,
                "scrollZoom": False,
                "responsive": False,
                "displaylogo": False,
                "dragmode": False,
            },
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

    def to_task(self) -> Task:
        """
        Returns the task description of this activity step.

        Returns:
            Task: The activity step as a workflow task.
        """
        inputs = [
            Link(
                name=source.material.name,
                section=source.material.reference,
            )
            for source in self.sources
            if source.material is not None and source.material.reference is not None
        ]
        outputs = [
            Link(
                name=parameters.layer.name,
                section=parameters.layer.reference,
            )
            for parameters in self.sample_parameters
            if parameters.layer is not None and parameters.layer.reference is not None
        ]
        return Task(name=self.name, inputs=inputs, outputs=outputs)

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
