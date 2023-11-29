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
import numpy as np
from nomad.metainfo import (
    Package,
    Quantity,
    Section,
    SubSection,
)
from nomad.datamodel.metainfo.basesections import (
    ElementalComposition,
    SynthesisMethod,
    CompositeSystem,
)
from nomad.datamodel.data import (
    ArchiveSection,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
)
from nomad.datamodel.metainfo.workflow import (
    Link,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name='Material Processing')


class Geometry(ArchiveSection):
    '''
    Geometrical shape attributes of a system.
    Sections derived from `Geometry` represent concrete geometrical shapes.
    '''
    m_def = Section(
    )
    volume = Quantity(
        type=float,
        description='The measure of the amount of space occupied in 3D space.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
        ),
        unit='meter ** 3',
    )


class Parallelepiped(Geometry):
    '''
    Six-faced polyhedron with each pair of opposite faces parallel and equal in size, 
    characterized by rectangular sides and parallelogram faces.
    '''
    m_def = Section(
    )
    height = Quantity(
        type=float,
        description='The z dimension of the parallelepiped.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='millimeter',
            label='Height (z)',
        ),
        unit='meter',
    )
    width = Quantity(
        type=float,
        description='The x dimension of the parallelepiped.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='millimeter',
            label='Width (x)',
        ),
        unit='meter',
    )
    length = Quantity(
        type=float,
        description='The y dimension of the parallelepiped.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='millimeter',
            label='Length (y)',
        ),
        unit='meter'
    )
    surface_area = Quantity(
        type=float,
        description='''
        The product of length and width, representing the total exposed area of the
        primary surface.
        ''',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='millimeter ** 2',
            label='Surface Area (x*y)',
        ),
        unit='meter ** 2',
    )


class Miscut(ArchiveSection):
    '''
    The miscut in a crystalline substrate refers to 
    the intentional deviation from a specific crystallographic orientation, 
    commonly expressed as the angular displacement of a crystal plane.
    '''
    angle = Quantity(
        type=float,
        description='''
        The angular displacement from the crystallographic orientation of the substrate.
        ''',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='deg',
            label='Miscut Angle',
        ),
        unit='deg',
    )
    angle_deviation = Quantity(
        type=float,
        description='The ± uncertainty in the angular displacement.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='deg',
            label='± Miscut Angle Deviation',
        ),
        unit='deg',
    )
    orientation = Quantity(
        type=str,
        description='The direction of the miscut in Miller index, [hkl].',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            label='Miscut Orientation [hkl]',
        )
    )


class Dopant(ElementalComposition):
    '''
    A dopant element in a crystalline structure 
    is a foreign atom intentionally introduced into the crystal lattice.
    '''
    doping_level = Quantity(
        type=float,
        description='The chemical doping level.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='1 / cm ** 3',
        ),
        unit='1 / m ** 3',
    )


class CrystalProperties(ArchiveSection):
    '''
    Characteristics arising from the ordered arrangement of atoms in a crystalline structure.
    These properties are defined by factors such as crystal symmetry, lattice parameters, 
    and the specific arrangement of atoms within the crystal lattice.
    '''


class SubstrateCrystalProperties(CrystalProperties):
    '''
    Crystallographic parameters such as orientation, miscut, and surface structure.
    '''
    orientation = Quantity(
        type=str,
        description='''
        Alignment of crystal lattice with respect to a vector normal to the surface 
        specified using Miller indices.
        ''',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            label='Substrate Orientation (hkl)',
        ),
    )
    miscut = SubSection(
        section_def=Miscut,
        description='''
        Section describing any miscut of the substrate with respect to the substrate
        orientation.
        ''',
    )


class Substrate(CompositeSystem):
    '''
    A thin free standing sheet of material. Not to be confused with the substrate role
    during a deposition, which can be a `Substrate` with `ThinFilm`(s) on it.
    '''
    m_def = Section()
    supplier = Quantity(
        type=str,
        description='The supplier of the current substrate specimen.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            label='Name of Supplier',
        )
    )
    supplier_id = Quantity(
        type=str,
        description='An ID string that is unique from the supplier.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            label='Supplier ID',
        ),
    )
    lab_id = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            label='Substrate ID',
        ),
    )


class CrystallineSubstrate(Substrate):
    '''
    The substrate defined in this class is composed of periodic arrangement of atoms
    and shows typical features of a crystal structure.
    '''
    m_def = Section()
    geometry = SubSection(
        section_def=Geometry,
        description='Section containing the geometry of the substrate.',
    )
    crystal_properties = SubSection(
        section_def=SubstrateCrystalProperties,
        description='Section containing the crystal properties of the substrate.',
    )
    dopants = SubSection(
        section_def=Dopant,
        repeats=True,
        description='''
        Repeating section containing information on any dopants in the substrate.
        ''',
    )


class ThinFilm(CompositeSystem):
    '''
    A thin film of material which exists as part of a stack.
    '''
    m_def = Section()

    geometry = SubSection(
        section_def=Geometry,
        description='Section containing the geometry of the thin film.',
    )


class ThinFilmStack(CompositeSystem):
    '''
    A stack of `ThinFilm`(s). Typically deposited on a `Substrate`.
    '''
    m_def = Section()
    substrate = Quantity(
        type=Substrate,
        description='''
        The substrate which the thin film layers of the thin film stack are deposited
        on.
        ''',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
        ),
    )
    layers = Quantity(
        type=ThinFilm,
        description='''
        An ordered list (starting at the substrate) of the thin films making up the
        thin film stacks.
        ''',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
        ),
        shape=["*"],
    )


class SampleDeposition(SynthesisMethod):
    '''
    The process of the settling of particles (atoms or molecules) from a solution,
    suspension or vapour onto a pre-existing surface, resulting in the growth of a
    new phase. [database_cross_reference: https://orcid.org/0000-0002-0640-0422]

    Synonyms:
     - deposition
    '''
    m_def = Section(
        links=[
            "http://purl.obolibrary.org/obo/CHMO_0001310"
        ],)

    def is_serial(self) -> bool:
        '''
        Method for determining if the steps are serial. Can be overwritten by sub class.
        Default behavior is to return True if all steps start after the previous one.

        Returns:
            bool: Whether or not the steps are serial.
        '''
        start_times = []
        durations = []
        for step in self.steps:
            if step.start_time is None or step.duration is None:
                return False
            start_times.append(step.start_time.timestamp())
            durations.append(step.duration.to('s').magnitude)
        start_times = np.array(start_times)
        durations = np.array(durations)
        end_times = start_times + durations
        diffs = start_times[1:] - end_times[:-1]
        if np.any(diffs < 0):
            return False
        return True

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        '''
        The normalizer for the `SampleDeposition` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super().normalize(archive, logger)
        if self.is_serial():
            tasks = []
            previous = None
            for step in self.steps:
                task = step.to_task()
                task.outputs = [Link(name=step.name, section=step)]
                if previous is not None:
                    task.inputs = [Link(name=previous.name, section=previous)]
                tasks.append(task)
                previous=step
            archive.workflow2.tasks = tasks


m_package.__init_metainfo__()
