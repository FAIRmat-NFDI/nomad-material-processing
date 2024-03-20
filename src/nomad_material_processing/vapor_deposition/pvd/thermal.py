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
)
from nomad.datamodel.data import (
    ArchiveSection,
)

from nomad_material_processing.vapor_deposition.pvd import (
    PVDEvaporationSource,
    PVDSource,
    PVDStep,
    PhysicalVaporDeposition,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name="Thermal Evaporation")


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