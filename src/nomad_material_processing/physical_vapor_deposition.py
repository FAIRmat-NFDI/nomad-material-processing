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
    MaterialEvaporationRate,
    SourceMaterial,
    SourceEvaporation,
    VaporDepositionSource,
    Substrate,
    VaporDepositionStep,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name="Physical Vapor Deposition")


class PVDMaterialEvaporationRate(MaterialEvaporationRate):
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
        a_eln=ELNAnnotation(
            defaultDisplayUnit="micromol/m ** 2/second",
        ),
    )


class PVDMaterialSource(SourceMaterial):
    m_def = Section(
        a_plot=dict(
            x="rate/process_time",
            y="rate/rate",
        ),
    )

    rate = SubSection(
        section_def=PVDMaterialEvaporationRate,
    )


# TODO remove this placeholder class and use the parent one
class PVDEvaporationSource(SourceEvaporation):
    pass


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
    name = Quantity(
        type=str,
        description="""
        A short and descriptive name for this source.
        """,
    )
    material_source = SubSection(
        section_def=PVDMaterialSource,
    )
    evaporation_source = SubSection(
        section_def=SourceEvaporation,
    )


# TODO remove this placeholder class and use the parent one
class PVDSubstrate(Substrate):
    pass


class PVDPressure(ArchiveSection):
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


class PVDGasFlow(ArchiveSection):
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


class PVDStep(VaporDepositionStep):
    """
    A step of any physical vapor deposition process.
    """

    sources = SubSection(
        section_def=PVDSource,
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


class PhysicalVaporDeposition(SampleDeposition):
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


class PLDTargetSource(PVDSourceMaterial):
    material = Quantity(
        description="""
        The material that is being evaporated.
        """,
        type=PLDTarget,
        a_eln=ELNAnnotation(
            label="Target", component=ELNComponentEnum.ReferenceEditQuantity
        ),
    )


class PLDLaser(SourceEvaporation):
    wavelength = Quantity(
        type=float,
        unit="meter",
        # a_eln=ELNAnnotation(
        #     defaultDisplayUnit='nanometer',
        # ),
    )
    repetition_rate = Quantity(
        type=float,
        unit="hertz",
        # a_eln=ELNAnnotation(
        #     defaultDisplayUnit='hertz',
        # ),
    )
    spot_size = Quantity(
        type=float,
        unit="meter ** 2",
        # a_eln=ELNAnnotation(
        #     defaultDisplayUnit='millimeter ** 2',
        # ),
    )
    pulses = Quantity(
        description="""
        The total number of laser pulses during the deposition step.
        """,
        type=int,
    )


class PLDSource(PVDSource):
    material_source = SubSection(
        section_def=PLDTargetSource,
    )
    evaporation_source = SubSection(
        section_def=PLDLaser,
    )


class PLDStep(VaporDepositionStep):
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
    method = Quantity(type=str, default="Pulsed Laser Deposition")
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
    method = Quantity(type=str, default="Sputter Deposition")

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
        a_eln=ELNAnnotation(
            defaultDisplayUnit="celsius",
        ),
    )
    process_time = Quantity(
        type=float,
        unit="second",
        shape=["*"],
        a_eln=ELNAnnotation(
            defaultDisplayUnit="second",
        ),
    )


class ThermalEvaporationHeater(SourceEvaporation):
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
                "material_source/rate/process_time",
                "evaporation_source/temperature/process_time",
            ],
            y=[
                "material_source/rate/rate",
                "evaporation_source/temperature/temperature",
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
    material_source = SubSection(
        section_def=PVDSourceMaterial,
    )
    evaporation_source = SubSection(
        section_def=ThermalEvaporationHeater,
    )


class ThermalEvaporationStep(VaporDepositionStep):
    m_def = Section(
        a_plot=[
            dict(
                x="sources/:/material_source/rate/process_time",
                y="sources/:/material_source/rate/rate",
            ),
            dict(
                x="sources/:/evaporation_source/temperature/process_time",
                y="sources/:/evaporation_source/temperature/temperature",
            ),
            dict(
                x="sources/:/evaporation_source/power/process_time",
                y="sources/:/evaporation_source/power/power",
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
                x="steps/:/sources/:/material_source/rate/process_time",
                y="steps/:/sources/:/material_source/rate/rate",
            ),
            # dict(
            #     x='steps/:/sources/:/evaporation_source/temperature/process_time',
            #     y='steps/:/sources/:/evaporation_source/temperature/temperature',
            # ),
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
    method = Quantity(type=str, default="Thermal Evaporation")

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
