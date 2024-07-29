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


class SolutionComponent(PureSubstanceComponent):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'substance_name',
                    'component_role',
                    'purity_fraction',
                    'mass',
                    'mass_fraction',
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
    mass = Quantity(
        type=np.float64,
        description='The mass of the component without the container.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram',
            minValue=0,
        ),
        unit='gram',
    )
    purity_fraction = Quantity(
        type=np.float64,
        description='The purity of the component in fraction.',
        a_eln=dict(
            component='NumberEditQuantity',
            maxValue=100,
            minValue=0,
        ),
    )
    molar_concentration = SubSection(section_def=MolarConcentration)


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
                    'component_role',
                    'purity_fraction',
                    'volume',
                    'density',
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

    def normalize(self, archive, logger: BoundLogger) -> None:
        super().normalize(archive, logger)
        if self.volume and self.density:
            self.mass = self.volume.to('liters') * self.density.to('grams/liter')


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


class Solution(CompositeSystem, EntryData):
    """
    Base class for a solution
    """

    # TODO make the solvents, solutes, and elemental_composition sub-section non-editable.

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
    components = SubSection(
        section_def=SolutionComponent,
        description="""
        The components of the solution.
        """,
        repeats=True,
    )
    solvents = SubSection(
        link='https://doi.org/10.1351/goldbook.S05751',
        section_def=SolutionComponent,
        description="""
        The term applied to the whole initial liquid phase containing the extractant.
        """,
        repeats=True,
    )
    solutes = SubSection(
        link='https://doi.org/10.1351/goldbook.S05744',
        section_def=SolutionComponent,
        description="""
        The minor component of a solution which is regarded as having been dissolved
        by the solvent.
        """,
        repeats=True,
    )
    solution_storage = SubSection(
        section_def=SolutionStorage,
        description="""
        The storage conditions of the solution.
        """,
    )

    def combine_solution_components(self, logger: 'BoundLogger') -> None:
        """
        Combine the solution components with the same IUPAC name.
        Following properties are accumulated for combined components: mass, volume.
        """
        combined_components = {}
        unprocessed_components = []
        for component in self.components:
            if not component.pure_substance or not component.pure_substance.iupac_name:
                unprocessed_components.append(component)
                continue
            comparison_key = component.pure_substance.iupac_name
            if comparison_key in combined_components:
                for prop in ['mass', 'volume']:
                    val1 = getattr(combined_components[comparison_key], prop, None)
                    val2 = getattr(component, prop, None)
                    if val1 and val2:
                        setattr(combined_components[comparison_key], prop, val1 + val2)
                    elif val1:
                        setattr(combined_components[comparison_key], prop, val1)
                    elif val2:
                        setattr(combined_components[comparison_key], prop, val2)
                for prop in ['component_role']:
                    # combine the component role (solvent or solute) if they are the same
                    val1 = getattr(combined_components[comparison_key], prop, None)
                    val2 = getattr(component, prop, None)
                    if val1 and val2 and val1 == val2:
                        setattr(combined_components[comparison_key], prop, val1)
                    else:
                        setattr(combined_components[comparison_key], prop, None)
            else:
                combined_components[comparison_key] = component

        self.components = list(combined_components.values())
        self.components.extend(unprocessed_components)

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
        component: SolutionComponent,
        logger: 'BoundLogger' = None,
    ) -> Union[Quantity, None]:
        """
        Compute the moles of a component in the solution. If purity fraction of component
        is provided, the calculated moles is multiplied with it.

        Args:
            component (SolutionComponent): component to compute the moles for.
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
        if getattr(component, 'purity_fraction', None):
            moles *= component.purity_fraction
        return moles

    def normalize(self, archive, logger) -> None:
        self.combine_solution_components(logger)

        self.compute_theoretical_volume(logger)
        if self.observed_volume:
            volume = self.observed_volume
        else:
            volume = self.theoretical_volume

        # get molar concentration of components
        for idx, component in enumerate(self.components):
            if isinstance(component, SolutionComponent):
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

        # fill the solvents and solutes
        self.solvents, self.solutes = [], []
        for component in self.components:
            if component.component_role == 'Solvent':
                self.solvents.append(component)
            elif component.component_role == 'Solute':
                self.solutes.append(component)

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
                    'duration',
                    'comment',
                    'solution_component',
                ],
            ),
        ),
    )
    solution_component = SubSection(section_def=SolutionComponent)

    def normalize(self, archive, logger):
        if not self.name and self.solution_component:
            if self.solution_component.name:
                self.name = f'Add {self.solution_component.name}'
            elif self.solution_component.component_role:
                self.name = f'Add {self.solution_component.component_role}'
            else:
                self.name = 'Add Solid Component'

        super().normalize(archive, logger)


class AddLiquid(SolutionPreparationStep):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'start_time',
                    'duration',
                    'comment',
                    'solution_component',
                ],
            ),
        ),
    )
    solution_component = SubSection(section_def=LiquidSolutionComponent)

    def normalize(self, archive, logger):
        if not self.name and self.solution_component:
            if self.solution_component.name:
                self.name = f'Add {self.solution_component.name}'
            elif self.solution_component.component_role:
                self.name = f'Add {self.solution_component.component_role}'
            else:
                self.name = 'Add Liquid Component'

        super().normalize(archive, logger)


class AddSolution(SolutionPreparationStep):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'start_time',
                    'volume',
                    'duration',
                    'comment',
                    'solution_component',
                ],
            ),
        ),
    )

    volume = Quantity(
        type=np.float64,
        description='The volume of the solution used.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='milliliter',
            minValue=0,
        ),
        unit='milliliter',
    )
    solution_component = SubSection(section_def=SolutionReference)

    def normalize(self, archive, logger):
        if self.solution_component and self.solution_component.reference:
            if not self.name:
                if self.solution_component.reference.name:
                    self.name = f'Add {self.solution_component.reference.name}'
                else:
                    self.name = 'Add Solution'
            if not self.volume and self.solution_component.reference.theoretical_volume:
                # assume entire volume of the solution is used
                self.volume = self.solution_component.reference.theoretical_volume

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
        super().normalize(archive, logger)


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
        super().normalize(archive, logger)


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
        super().normalize(archive, logger)


class SolutionPreparation(Process, EntryData):
    """
    Solution preparation class
    """

    # TODO make the solution and solution_reference sub-sections non-editable.

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
                    'solution',
                    'solution_reference',
                    'instruments',
                ],
            ),
        ),
    )
    solution = SubSection(
        section_def=Solution,
    )
    solution_reference = SubSection(
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

        solution_file_name = (
            f'solution_{archive.data.name.replace(" ", "_")}.archive.json'
        )

        solution_entry = EntryArchive(data=archive.data.solution)
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
        component_added = False
        for step in self.steps:
            if isinstance(step, (AddSolid, AddLiquid, AddSolution)):
                component_added = True
                break
        if not component_added:
            return

        # prepare the solution
        if not self.solution:
            self.solution = Solution()
        self.solution.solutes = []
        self.solution.solvents = []
        self.solution.components = []
        for step in self.steps:
            if isinstance(step, (AddSolid, AddLiquid)):
                if step.solution_component:
                    self.solution.components.append(step.solution_component)
            elif isinstance(step, AddSolution):
                # add components from the solution while taking the volume used into
                # account
                try:
                    component = step.solution_component.reference.m_copy()
                except AttributeError:
                    logger.error(
                        f'Could not copy the solution reference for the step {step.name}.'
                    )
                    continue
                if not component.components:
                    continue
                try:
                    scaler = (
                        step.volume
                        / step.solution_component.reference.theoretical_volume
                    )
                    for idx, comp in enumerate(component.components):
                        if getattr(comp, 'mass', None):
                            component.components[idx].mass = comp.mass * scaler
                        if getattr(comp, 'volume', None):
                            component.components[idx].volume = comp.volume * scaler
                except Exception as e:
                    logger.warning(
                        f'Could not scale the components for the step {step.name}.\n{e}.'
                    )
                self.solution.components.extend(component.components)
        if not self.solution.name:
            self.solution.name = f'Solution from {self.name}'
        self.solution.normalize(archive, logger)

        # create a reference to the solution
        if self.solution and not self.solution_reference:
            self.solution_reference = SolutionReference()
        self.solution_reference.reference = self.create_solution_entry(archive, logger)
