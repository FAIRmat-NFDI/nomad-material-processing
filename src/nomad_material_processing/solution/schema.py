from typing import TYPE_CHECKING, Union
from nomad.units import ureg
import numpy as np
from nomad.datamodel.data import (
    ArchiveSection,
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    SectionProperties,
    Filter,
)
from nomad.datamodel.metainfo.basesections import (
    Component,
    CompositeSystem,
    CompositeSystemReference,
    Process,
    ProcessStep,
    PureSubstanceComponent,
)
from nomad.metainfo import (
    Datetime,
    MEnum,
    Quantity,
    Section,
    SubSection,
)
from structlog.stdlib import BoundLogger
from nomad_material_processing.solution.utils import (
    create_archive,
)

if TYPE_CHECKING:
    from structlog.stdlib import BoundLogger


class BaseSolutionComponent(ArchiveSection):
    m_def = Section(
        description="""
        Base class to put together `SolutionComponent` and `SolutionComponentReference`
        classes.
        """,
    )


class MolarConcentration(ArchiveSection):
    """
    The molar concentration of a component in a solution.
    """

    theoretical_concentration = Quantity(
        type=np.float64,
        description=(
            'The expected concentration calculated from the component moles and '
            'total volume.'
        ),
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='mol / liter',
            minValue=0,
        ),
        unit='mol / liter',
    )
    observed_concentration = Quantity(
        type=np.float64,
        description=(
            'The concentration observed or measured with some characterization technique.'
        ),
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='mol / liter',
            minValue=0,
        ),
        unit='mol / liter',
    )


class SolutionComponent(BaseSolutionComponent, PureSubstanceComponent):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'substance_name',
                    'container_mass',
                    'gross_mass',
                    'mass',
                    'mass_fraction',
                ],
            ),
        ),
    )
    mass = Quantity(
        type=np.float64,
        description='The mass of the material without the container.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram',
            minValue=0,
        ),
        unit='gram',
    )
    molar_concentration = SubSection(section_def=MolarConcentration)


class SolidSolutionComponent(SolutionComponent):
    pass


class LiquidSolutionComponent(SolutionComponent):
    m_def = Section(
        description="""
        The liquid component of a mixed material.
        """,
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'substance_name',
                    'volume',
                    'density',
                    'purity_percentage',
                ],
            ),
        ),
    )
    volume = Quantity(
        type=np.float64,
        description='The volume of the liquid component.',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='milliliter',
            minValue=0,
        ),
        unit='milliliter',
    )
    density = Quantity(
        type=np.float64,
        description='The density of the liquid component.',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram / liter',
            minValue=0,
        ),
        unit='gram / liter',
    )
    purity_percentage = Quantity(
        type=np.float64,
        description='The purity of the liquid component in fraction.',
        a_eln=dict(
            component='NumberEditQuantity',
            maxValue=100,
            minValue=0,
        ),
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        super().normalize(archive, logger)
        if self.volume and self.density:
            self.mass = self.volume.to('liters') * self.density.to('grams/liter')


class Solution(CompositeSystem, EntryData):
    """
    Base class for a solution
    """

    m_def = Section(
        description="""
        The resulting liquid obtained after the Solution preparation steps.
        """,
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'datetime',
                    'lab_id',
                    'ph_value',
                    'theoretical_volume',
                    'observed_volume',
                    'description',
                    'components',
                    'elemental_composition',
                    'solvents',
                    'solutes',
                ],
            ),
        ),
    )
    ph_value = Quantity(
        description='The pH value of the solution.',
        type=np.float64,
        a_eln=dict(
            component='NumberEditQuantity',
            minValue=0,
            maxValue=14,
        ),
    )
    theoretical_volume = Quantity(
        description="""The final expected volume of the solution, which is the sum of
        volume of its liquid components.
        """,
        type=np.float64,
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='milliliter',
            minValue=0,
        ),
        unit='milliliter',
    )
    observed_volume = Quantity(
        description='The final observed volume of the solution.',
        type=np.float64,
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='milliliter',
            minValue=0,
        ),
        unit='milliliter',
    )
    solvents = SubSection(
        link='https://doi.org/10.1351/goldbook.S05751',
        section_def=BaseSolutionComponent,
        description="""
        The term applied to the whole initial liquid phase containing the extractant.
        """,
        repeats=True,
    )
    solutes = SubSection(
        link='https://doi.org/10.1351/goldbook.S05744',
        section_def=BaseSolutionComponent,
        description="""
        The minor component of a solution which is regarded as having been dissolved
        by the solvent.
        """,
        repeats=True,
    )

    def compute_theoretical_volume(self, logger: 'BoundLogger') -> None:
        """
        Compute the theoretical volume of the solution.

        Args:
            logger (BoundLogger): A structlog logger.
        """
        self.theoretical_volume = 0 * ureg('milliliter')
        for component in self.components:
            if isinstance(component, LiquidSolutionComponent):
                if not component.volume:
                    logger.warning(f'Volume of component {component.name} is missing.')
                    continue
                self.theoretical_volume += component.volume

    @staticmethod
    def compute_component_moles(
        component: Union[LiquidSolutionComponent, SolidSolutionComponent],
        logger: 'BoundLogger' = None,
    ) -> Union[Quantity, None]:
        """
        Compute the moles of a component in the solution.

        Args:
            component (Union[LiquidSolutionComponent, SolidSolutionComponent]): component
                to compute the moles for.
            logger (BoundLogger): A structlog logger.

        Returns:
            Union[Quantity, None]: The moles of the component in the solution.
        """

        if not component.pure_substance.molecular_mass:
            if logger:
                logger.warning(
                    f'Could not calculate moles of the "{component.name}" as molecular '
                    'mass is missing.'
                )
            return
        if not component.mass:
            if logger:
                logger.warning(
                    f'Could not calculate moles of the "{component.name}" as mass is '
                    'missing.'
                )
            return
        moles = component.mass.to('grams') / (
            component.pure_substance.molecular_mass.to('Da').magnitude * ureg('g/mol')
        )
        return moles

    def normalize(self, archive, logger) -> None:
        # TODO combine together the same type of components

        # get total volume of the solution
        self.compute_theoretical_volume(logger)
        if self.observed_volume:
            volume = self.observed_volume
        else:
            volume = self.theoretical_volume

        # get molar concentration of components
        for idx, component in enumerate(self.components):
            if isinstance(component, (LiquidSolutionComponent, SolidSolutionComponent)):
                if not component.molar_concentration:
                    self.components[idx].molar_concentration = MolarConcentration()
                molar_concentration = None
                if not volume:
                    logger.warning(
                        f'Volume of the solution is missing, could not calculate the '
                        f'concentration of the component {component.name}.'
                    )
                else:
                    moles = self.compute_component_moles(component, logger)
                    if moles:
                        molar_concentration = moles / volume
                self.components[
                    idx
                ].molar_concentration.theoretical_concentration = molar_concentration

        self.elemental_composition = []
        super().normalize(archive, logger)


class SolutionReference(CompositeSystemReference):
    """
    A section used for referencing the Solution.
    """

    reference = Quantity(
        type=Solution,
        description='A reference to a NOMAD `Solution` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='Solution Reference',
        ),
    )


class SolutionComponentReference(BaseSolutionComponent, SolutionReference):
    m_def = Section(
        description="""
        Reference to another solution used as component in the solution preparation.
        """,
    )


class SolutionPreparationStep(ProcessStep):
    m_def = Section(
        description="""
        Class to put together the steps of a solution preparation.
        """,
    )


class AddSolid(SolutionPreparationStep):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'start_time',
                    'component_role',
                    'comment',
                    'duration',
                    'material',
                ],
            ),
        ),
    )
    component_role = Quantity(
        type=MEnum(
            'Solvent',
            'Solute',
        ),
        description="""
        The role of the component added to the solution.
        | role | description |
        | ------------- | ----------- |
        | Solvent       | The term applied to the whole initial liquid phase containing the extractant. |
        | Solute        | The minor component of a solution which is regarded as having been dissolved by the solvent. |
        """,
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )

    solution_component = SubSection(section_def=SolidSolutionComponent)

    def normalize(self, archive, logger):
        if not self.name:
            if self.component_role:
                self.name = f'Add {self.component_role}'
            else:
                self.name = 'Add Solid Component'

        if self.solution_component:
            archive.data.solution_components.append(self.solution_component)
            if self.component_role == 'Solute':
                archive.data.solutes.append(self.solution_component)
            elif self.component_role == 'Solvent':
                archive.data.solvents.append(self.solution_component)

        super().normalize(archive, logger)


class AddLiquid(SolutionPreparationStep):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'start_time',
                    'component_role',
                    'comment',
                    'duration',
                    'material',
                ],
            ),
        ),
    )
    component_role = Quantity(
        type=MEnum(
            'Solvent',
            'Solute',
        ),
        description="""
        The role of the component added to the solution.
        | role | description |
        | ------------- | ----------- |
        | Solvent       | The term applied to the whole initial liquid phase containing the extractant. |
        | Solute        | The minor component of a solution which is regarded as having been dissolved by the solvent. |
        """,
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )

    solution_component = SubSection(section_def=LiquidSolutionComponent)

    def normalize(self, archive, logger):
        if not self.name:
            if self.component_role:
                self.name = f'Add {self.component_role}'
            else:
                self.name = 'Add Liquid Component'

        if self.solution_component:
            archive.data.solution_components.append(self.solution_component)
            if self.component_role == 'Solute':
                archive.data.solutes.append(self.solution_component)
            elif self.component_role == 'Solvent':
                archive.data.solvents.append(self.solution_component)

        super().normalize(archive, logger)


class AddSolution(SolutionPreparationStep):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'start_time',
                    'comment',
                    'duration',
                    'material',
                ],
            ),
        ),
    )

    solution_component = SubSection(section_def=SolutionReference)

    def normalize(self, archive, logger):
        if not self.name:
            self.name = 'Add Solution'

        if self.solution_component:
            component = self.solution_component.reference
            archive.data.solution_components.extend(component.components)
            archive.data.solvents.extend(component.solvents)
            archive.data.solutes.extend(component.solutes)

        super().normalize(archive, logger)


class Agitation(SolutionPreparationStep):
    m_def = Section(
        a_eln=None,
    )
    temperature = Quantity(
        type=np.float64,
        description='The temperature of the mixing process.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius',
        ),
        unit='celsius',
    )
    container_type = Quantity(
        type=str,
        description='The type of container used for mixing.',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )

    def normalize(self, archive, logger):
        if not self.name:
            self.name = 'Agitation'
        return super().normalize(archive, logger)


class Sonication(Agitation):
    frequency = Quantity(
        type=np.float64,
        description='The frequency of the sonication instrument.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='Hz',
        ),
        unit='Hz',
    )

    def normalize(self, archive, logger):
        if not self.name:
            self.name = 'Sonication'
        return super().normalize(archive, logger)


class MechanicalStirring(Agitation):
    rotation_speed = Quantity(
        type=np.float64,
        description='The rotation speed of the mixing process.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='rpm',
        ),
        unit='rpm',
    )

    def normalize(self, archive, logger):
        if not self.name:
            self.name = 'Mechanical Stirring'
        return super().normalize(archive, logger)


class SolutionPreparation(Process, EntryData):
    """
    Solution preparation class
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                visible=Filter(
                    exclude=[
                        'method',
                        'samples',
                    ],
                ),
                order=[
                    'name',
                    'datetime',
                    'end_time',
                    'lab_id',
                    'location',
                    'description',
                    'steps',
                    'solution_components',
                    'solvents',
                    'solutes',
                    'instruments',
                ],
            ),
        ),
    )
    solvents = SubSection(
        link='https://doi.org/10.1351/goldbook.S05751',
        section_def=BaseSolutionComponent,
        description="""
        The term applied to the whole initial liquid phase containing the extractant.
        """,
        repeats=True,
    )
    solutes = SubSection(
        link='https://doi.org/10.1351/goldbook.S05744',
        section_def=BaseSolutionComponent,
        description="""
        The minor component of a solution which is regarded as having been dissolved
        by the solvent.
        """,
        repeats=True,
    )
    solution_components = SubSection(
        section_def=BaseSolutionComponent,
        repeats=True,
    )
    solution = SubSection(
        section_def=SolutionReference,
    )
    steps = SubSection(
        section_def=SolutionPreparationStep,
        description="""
        Ordered list of steps of the solution preparation process.
        """,
        repeats=True,
    )

    def create_solution_entry(self, archive, logger):
        from nomad.datamodel.datamodel import EntryArchive

        solution = Solution()
        solution.name = f'Solution created from {archive.data.name} entry'
        solution_file_name = (
            f'solution_{archive.data.name.replace(" ", "_")}.archive.json'
        )

        solution.components = self.solution_components
        solution.solutes = self.solutes
        solution.solvents = self.solvents

        solution.normalize(archive, logger)

        solution_entry = EntryArchive(data=solution)
        solution_reference = create_archive(
            entry_dict=solution_entry.m_to_dict(with_root_def=True),
            context=archive.m_context,
            filename=solution_file_name,
            file_type='json',
            logger=logger,
            overwrite=True,
        )

        return solution_reference

    def normalize(self, archive, logger) -> None:
        super().normalize(archive, logger)

        self.solvents = []
        self.solutes = []
        self.solution_components = []

        for step in self.steps:
            if isinstance(step, (AddSolid, AddLiquid, AddSolution)):
                step.normalize(archive, logger)

        if not self.solution:
            self.solution = SolutionReference()
        self.solution.reference = self.create_solution_entry(archive, logger)


class SolutionStorage(ArchiveSection):
    """
    Solution storage class
    """

    start_date = Quantity(
        type=Datetime,
        a_eln=dict(
            component='DateTimeEditQuantity',
        ),
    )

    end_date = Quantity(
        type=Datetime,
        a_eln=dict(
            component='DateTimeEditQuantity',
        ),
    )

    storage_condition = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity',
        ),
    )
    temperature = Quantity(
        type=np.float64,
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius',
        ),
        unit='celsius',
    )

    atmosphere = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['Ar', 'N2', 'Air'],
            ),
        ),
    )

    comments = Quantity(
        type=str,
        a_eln=dict(
            component='RichTextEditQuantity',
        ),
    )


# class SolutionPreparationIKZ(Process, EntryData):
#     """
#     Solution preparation class
#     """

#     method = Quantity(
#         type=MEnum('Shaker', 'Ultrasoncic', 'Waiting', 'Stirring'),
#         shape=[],
#         a_eln=dict(
#             component='EnumEditQuantity',
#         ),
#         # categories=[IKZCategory],
#     )
#     description = Quantity(
#         type=str,
#         description='The description of the solution preparation.',
#         a_eln={'component': 'StringEditQuantity'},
#     )
#     atmosphere = Quantity(
#         type=str,
#         description='The atmosphere used for the solution preparation.',
#         a_eln={'component': 'StringEditQuantity'},
#     )
#     intended_tot_volume = Quantity(
#         type=float,
#         description='The planned total volume of the solution.',
#         a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'liter'},
#         unit='liter',
#     )
#     obtained_tot_volume = Quantity(
#         type=float,
#         description='The obtained total volume of the solution.',
#         a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'liter'},
#         unit=' liter',
#     )
#     solution = SubSection(
#         section_def=SolutionReference,
#         description="""
#         The obtained solution, composed by the sum of each mixing step.
#         """,
#     )
#     steps = SubSection(
#         section_def=SolutionPreparationStep,
#         repeats=True,
#     )
