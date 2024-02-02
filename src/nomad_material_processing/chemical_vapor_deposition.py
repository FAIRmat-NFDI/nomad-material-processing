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


class CVDMaterialEvaporationRate(MaterialEvaporationRate):
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
    flow = Quantity(  ############### I need this, let's discuss if it must be here or in CVD module
        type=float,
        a_eln=ELNAnnotation(
            defaultDisplayUnit="cm ** 3 / minute",
        ),
        unit="cm ** 3 / minute",
    )


class CVDSourceMaterial(SourceMaterial):
    m_def = Section(
        a_plot=dict(
            x="rate/process_time",
            y="rate/rate",
        ),
    )

    rate = SubSection(
        section_def=CVDMaterialEvaporationRate,
    )


# TODO remove this placeholder class and use the parent one
class CVDSourceEvaporation(SourceEvaporation):
    pass


class CVDSource(VaporDepositionSource):
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
        section_def=CVDSourceMaterial,
    )
    evaporation_source = SubSection(
        section_def=CVDSourceEvaporation,
    )


# TODO remove this placeholder class and use the parent one
class PVDSubstrate(Substrate):
    pass


class CVDPressure(ArchiveSection):
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


class CVDGasFlow(ArchiveSection):
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


class CVDStep(VaporDepositionStep):
    """
    A step of any physical vapor deposition process.
    """

    sources = SubSection(
        section_def=CVDSource,
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
        super(CVDStep, self).normalize(archive, logger)


class ChemicalVaporDeposition(VaporDeposition):
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
        section_def=CVDStep,
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
        super(ChemicalVaporDeposition, self).normalize(archive, logger)


m_package.__init_metainfo__()