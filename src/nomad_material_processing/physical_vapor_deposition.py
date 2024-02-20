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
    CompositeSystemReference,
    ReadableIdentifiers,
)

from nomad_material_processing.vapor_deposition import (
    EvaporationSource,
    VaporDepositionSource,
    SampleParameters,
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

m_package = Package(name="Physical Vapor Deposition")


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


class PVDEvaporationSource(EvaporationSource):
    m_def = Section(
        a_plot=dict(
            x="power/process_time",
            y="power/power",
        ),
    )
    power = SubSection(
        section_def=SourcePower,
    )


class ImpingingFlux(ArchiveSection):
    m_def = Section(
        a_plot=dict(
            x="process_time",
            y="rate",
        ),
    )
    rate = Quantity(
        type=float,
        unit="mol/meter ** 2/second",
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
            "Quartz Crystal Microbalance",
        )
    )


class PVDSource(VaporDepositionSource):
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
    vapor_source = SubSection(
        section_def=PVDEvaporationSource,
        description="""
        Example: A heater, a filament, a laser, etc.
        """,
    )
    impinging_flux = SubSection(
        section_def=ImpingingFlux,
        description="""
        The deposition rate of the material onto the substrate (mol/area/time).
        """,
        repeats=True,
    )


class PVDSampleParameters(SampleParameters):
    heater = Quantity(
        description="""
        What is the substrate heated by.
        """,
        type=MEnum(
            "No heating",
            "Halogen lamp",
            "Filament",
            "Resistive element",
            "CO2 laser",
        ),
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


class PVDStep(VaporDepositionStep):
    """
    A step of any physical vapor deposition process.
    """

    sources = SubSection(
        section_def=PVDSource,
        repeats=True,
    )
    sample_parameters = SubSection(
        section_def=PVDSampleParameters,
        repeats=True,
    )

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        """
        The normalizer for the `PVDStep` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super(PVDStep, self).normalize(archive, logger)


class PhysicalVaporDeposition(VaporDeposition):
    """
    A synthesis technique where vaporized molecules or atoms condense on a surface,
    forming a thin layer. The process is purely physical; no chemical reaction occurs
    at the surface. [database_cross_reference: https://orcid.org/0000-0002-0640-0422]

    Synonyms:
     - PVD
     - physical vapor deposition
    """

    m_def = Section(
        links=["http://purl.obolibrary.org/obo/CHMO_0001356"],
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
        section_def=PVDStep,
        repeats=True,
    )

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        """
        The normalizer for the `PhysicalVaporDeposition` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super(PhysicalVaporDeposition, self).normalize(archive, logger)


class PLDTarget(CompositeSystem):
    target_id = SubSection(
        section_def=ReadableIdentifiers,
    )


class PLDTargetReference(CompositeSystemReference):
    lab_id = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            label="Target ID",
        ),
    )
    reference = Quantity(
        type=PLDTarget,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
        ),
    )


class PLDLaser(PVDEvaporationSource):
    wavelength = Quantity(
        type=float,
        unit="meter",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit="nanometer",
        ),
    )
    repetition_rate = Quantity(
        type=float,
        unit="hertz",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit="hertz",
        ),
    )
    spot_size = Quantity(
        type=float,
        unit="meter ** 2",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit="millimeter ** 2",
        ),
    )
    pulses = Quantity(
        description="""
        The total number of laser pulses during the deposition step.
        """,
        type=int,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
        ),
    )


class PLDSource(PVDSource):
    material = SubSection(
        section_def=PLDTargetReference,
        description="""
        The source of the material that is being evaporated.
        Example: A sputtering target, a powder in a crucible, etc.
        """,
    )
    vapor_source = SubSection(
        section_def=PLDLaser,
        description="""
        Section containing the details of the laser source.
        """,
    )


class PLDStep(PVDStep):
    sources = SubSection(
        section_def=PLDSource,
        repeats=True,
    )


class PulsedLaserDeposition(PhysicalVaporDeposition):
    """
    A synthesis technique where a high-power pulsed laser beam is focused (inside a
    vacuum chamber) onto a target of the desired composition. Material is then
    vaporized from the target ('ablation') and deposited as a thin film on a
    substrate facing the target.
    [database_cross_reference: https://orcid.org/0000-0002-0640-0422]

    Synonyms:
     - pulsed laser ablation deposition
     - PLD
     - pulsed-laser ablation deposition
     - laser ablation growth
     - PLA deposition
     - pulsed-laser deposition
    """

    m_def = Section(
        links=["http://purl.obolibrary.org/obo/CHMO_0001363"],
    )
    method = Quantity(
        type=str,
        default="Pulsed Laser Deposition",
    )
    steps = SubSection(
        description="""
        The steps of the deposition process.
        """,
        section_def=PLDStep,
        repeats=True,
    )

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        """
        The normalizer for the `PulsedLaserDeposition` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super(PulsedLaserDeposition, self).normalize(archive, logger)


class SputterDeposition(PhysicalVaporDeposition):
    """
    A synthesis technique where a solid target is bombarded with electrons or
    energetic ions (e.g. Ar+) causing atoms to be ejected ('sputtering'). The ejected
    atoms then deposit, as a thin-film, on a substrate.
    [database_cross_reference: https://orcid.org/0000-0002-0640-0422]

    Synonyms:
     - sputtering
     - sputter coating
    """

    m_def = Section(
        links=["http://purl.obolibrary.org/obo/CHMO_0001364"],
    )
    method = Quantity(
        type=str,
        default="Sputter Deposition",
    )

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        """
        The normalizer for the `SputterDeposition` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super(SputterDeposition, self).normalize(archive, logger)


class ThermalEvaporationHeaterTemperature(ArchiveSection):
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


class ThermalEvaporationHeater(PVDEvaporationSource):
    m_def = Section(
        a_plot=dict(
            x=[
                "temperature/process_time",
                "power/process_time",
            ],
            y=[
                "temperature/temperature",
                "power/power",
            ],
            lines=[
                dict(
                    mode="lines",
                    line=dict(
                        color="rgb(25, 46, 135)",
                    ),
                ),
                dict(
                    mode="lines",
                    line=dict(
                        color="rgb(0, 138, 104)",
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
                "deposition_rate/process_time",
                "vapor_source/temperature/process_time",
            ],
            y=[
                "deposition_rate/rate",
                "vapor_source/temperature/temperature",
            ],
            lines=[
                dict(
                    mode="lines",
                    line=dict(
                        color="rgb(25, 46, 135)",
                    ),
                ),
                dict(
                    mode="lines",
                    line=dict(
                        color="rgb(0, 138, 104)",
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
                x="sources/:/deposition_rate/process_time",
                y="sources/:/deposition_rate/rate",
            ),
            dict(
                x="sources/:/vapor_source/temperature/process_time",
                y="sources/:/vapor_source/temperature/temperature",
            ),
            dict(
                x="sources/:/vapor_source/power/process_time",
                y="sources/:/vapor_source/power/power",
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
        links=["http://purl.obolibrary.org/obo/CHMO_0001360"],
        a_plot=[
            dict(
                x="steps/:/sources/:/deposition_rate/process_time",
                y="steps/:/sources/:/deposition_rate/rate",
            ),
            dict(
                x="steps/:/sources/:/vapor_source/temperature/process_time",
                y="steps/:/sources/:/vapor_source/temperature/temperature",
            ),
            dict(
                x="steps/:/environment/pressure/process_time",
                y="steps/:/environment/pressure/pressure",
                layout=dict(
                    yaxis=dict(
                        type="log",
                    ),
                ),
            ),
        ],
    )
    method = Quantity(
        type=str,
        default="Thermal Evaporation",
    )
    steps = SubSection(
        description="""
        The steps of the deposition process.
        """,
        section_def=ThermalEvaporationStep,
        repeats=True,
    )

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        """
        The normalizer for the `ThermalEvaporation` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super(ThermalEvaporation, self).normalize(archive, logger)


m_package.__init_metainfo__()
