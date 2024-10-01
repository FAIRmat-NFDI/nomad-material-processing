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
    Quantity,
    SchemaPackage,
    Section,
)

from nomad_material_processing.vapor_deposition.pvd.general import (
    PhysicalVaporDeposition,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad.config import config
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
    Filter,
    SectionProperties,
)
from nomad.datamodel.metainfo.basesections import (
    CompositeSystem,
    ReadableIdentifiers,
    SystemComponent,
)
from nomad.metainfo import (
    Datetime,
    SubSection,
)

from nomad_material_processing.general import (
    Geometry,
)
from nomad_material_processing.vapor_deposition.pvd.general import (
    PVDEvaporationSource,
    PVDSource,
    SourcePower,
)

m_package = SchemaPackage(name='Sputter Deposition')

configuration = config.get_plugin_entry_point(
    'nomad_material_processing.vapor_deposition.pvd:sputtering_schema',
)


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
        links=['http://purl.obolibrary.org/obo/CHMO_0001364'],
    )
    method = Quantity(
        type=str,
        default='Sputter Deposition',
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `SputterDeposition` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)


class Magnetron(PVDEvaporationSource):
    """
    A representation of the magnetron device.
    """

    m_def = Section(
        a_plot=dict(
            x='power/time',
            y='power/value',
        ),
    )

    power = SourcePower()

    Description = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='RichTextEditQuantity',
        ),
    )


class SputteringTarget(CompositeSystem, EntryData):
    """
    A representation of the target material used in sputtering. It cointains the target
    ID, the delivery date and the actual date where the target was installed
    inside the chamber.
    """

    m_def = Section(a_eln={'hide': ['datetime']})

    target_id = SubSection(
        section_def=ReadableIdentifiers,
    )

    geometry = SubSection(
        section_def=Geometry,
        description='Section containing the geometry of the target.',
    )

    delivery_date = Quantity(
        type=Datetime,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.DateEditQuantity,
        ),
    )

    installation_date = Quantity(
        type=Datetime,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.DateEditQuantity,
        ),
    )


class SputteringTargetComponent(SystemComponent):
    m_def = Section(a_eln={'hide': ['mass_fraction', 'mass']})

    lab_id = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            label='Target ID',
        ),
    )
    system = Quantity(
        type=SputteringTarget,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
        ),
    )


class SputteringSource(PVDSource):
    """
    A representation of both the magentron and the target material, which works as
    a source of atoms for sputtering.
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            hide=['name'],
            properties=SectionProperties(
                visible=Filter(exclude=['impinging_flux', 'vapor_molar_flow_rate'])
            ),
        ),
        links=['http://purl.obolibrary.org/obo/CHMO_0002896'],
    )

    vapor_source = SubSection(section_def=Magnetron, repeats=True)


m_package.__init_metainfo__()
