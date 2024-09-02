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

from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
)
from nomad.datamodel.metainfo.basesections import (
    CompositeSystem,
    ReadableIdentifiers,
    SystemComponent,
)
from nomad.metainfo import (
    Quantity,
    SchemaPackage,
    Section,
    SubSection,
)

from nomad_material_processing.vapor_deposition.pvd.general import (
    PhysicalVaporDeposition,
    PVDEvaporationSource,
    PVDSource,
    PVDStep,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad.config import config

m_package = SchemaPackage(name='Pulsed Laser Deposition')

configuration = config.get_plugin_entry_point(
    'nomad_material_processing.vapor_deposition.pvd:pld_schema',
)


class PLDTarget(CompositeSystem):
    target_id = SubSection(
        section_def=ReadableIdentifiers,
    )


class PLDTargetComponent(SystemComponent):
    lab_id = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            label='Target ID',
        ),
    )
    system = Quantity(
        type=PLDTarget,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
        ),
    )


class PLDLaser(PVDEvaporationSource):
    wavelength = Quantity(
        type=float,
        unit='meter',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='nanometer',
        ),
    )
    repetition_rate = Quantity(
        type=float,
        unit='hertz',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='hertz',
        ),
    )
    spot_size = Quantity(
        type=float,
        unit='meter ** 2',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='millimeter ** 2',
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
        section_def=PLDTargetComponent,
        description="""
        The source of the material that is being evaporated.
        Example: A sputtering target, a powder in a crucible, etc.
        """,
        repeats=True,
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
        links=['http://purl.obolibrary.org/obo/CHMO_0001363'],
    )
    method = Quantity(
        type=str,
        default='Pulsed Laser Deposition',
    )
    steps = SubSection(
        description="""
        The steps of the deposition process.
        """,
        section_def=PLDStep,
        repeats=True,
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `PulsedLaserDeposition` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)


m_package.__init_metainfo__()
