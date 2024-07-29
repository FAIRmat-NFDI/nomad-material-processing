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
    InstrumentReference,
    Process,
    ProcessStep,
    PureSubstanceComponent,
    PubChemPureSubstanceSection,
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

    calculated_concentration = Quantity(
        type=np.float64,
        description=(
            'The expected concentration calculated from the component moles and '
            'total volume.'
        ),
        a_eln=ELNAnnotation(
            defaultDisplayUnit='mol / liter',
        ),
        unit='mol / liter',
    )
    measured_concentration = Quantity(
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


class BaseSolutionComponent(Component):
    pass


class SolutionComponent(PureSubstanceComponent, BaseSolutionComponent):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'substance_name',
                    'component_role',
                    'volume',
                    'density',
                    'mass',
                    'molar_concentration',
                ],
                visible=Filter(
                    exclude=[
                        'mass_fraction',
                    ],
                ),
            ),
        ),
    )
    component_role = Quantity(
        type=MEnum(
            'Solvent',
            'Solute',
        ),
        default='Solvent',
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
    molar_concentration = SubSection(section_def=MolarConcentration)
    pure_substance = SubSection(section_def=PubChemPureSubstanceSection)

    def compute_moles(self, logger: 'BoundLogger' = None) -> Union[Quantity, None]:
        """
        Compute the moles of a component in the solution.

        Args:
            component (SolutionComponent): component to compute the moles for.
            logger (BoundLogger): A structlog logger.

        Returns:
            Union[Quantity, None]: The moles of the component in the solution.
        """

        if not self.pure_substance.molecular_mass:
            if logger:
                logger.warning(
                    f'Could not calculate moles of the "{self.name}" as molecular '
                    'mass is missing.'
                )
            return
        if not self.mass:
            if logger:
                logger.warning(
                    f'Could not calculate moles of the "{self.name}" as mass is '
                    'missing.'
                )
            return
        moles = self.mass.to('grams') / (
            self.pure_substance.molecular_mass.to('Da').magnitude * ureg('g/mol')
        )
        return moles

    def compute_molar_concentration(
        self, volume: Quantity, logger: 'BoundLogger'
    ) -> None:
        """
        Compute the molar concentration of the component in a given volume of solution.

        Args:
            volume (Quantity): The volume of the solution.
            logger (BoundLogger): A structlog logger.
        """
        if not volume:
            logger.warning(
                f'Volume of the solution is missing, can not calculate the '
                f'concentration of the component {self.name}.'
            )
            return
        if not self.molar_concentration:
            self.molar_concentration = MolarConcentration()
        moles = self.compute_moles(logger)
        if moles:
            self.molar_concentration.calculated_concentration = moles / volume

    def normalize(self, archive, logger: BoundLogger) -> None:
        PureSubstanceComponent.normalize(self, archive, logger)
        if self.volume and self.density:
            self.mass = self.volume.to('liters') * self.density.to('grams/liter')


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
                    'calculated_volume',
                    'measured_volume',
                    'mass',
                    'density',
                    'ph_value',
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
    density = Quantity(
        description='The density of the solution.',
        type=np.float64,
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram / milliliter',
            minValue=0,
        ),
        unit='gram / milliliter',
    )
    mass = Quantity(
        description='The mass of the solution.',
        type=np.float64,
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram',
            minValue=0,
        ),
        unit='gram',
    )
    calculated_volume = Quantity(
        description="""The final expected volume of the solution, which is the sum of
        volume of its liquid components.
        """,
        type=np.float64,
        a_eln=dict(
            defaultDisplayUnit='milliliter',
        ),
        unit='milliliter',
    )
    measured_volume = Quantity(
        description='The volume of the solution as observed or measured.',
        type=np.float64,
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='milliliter',
            minValue=0,
        ),
        unit='milliliter',
    )
    components = SubSection(
        section_def=BaseSolutionComponent,
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

    @staticmethod
    def combine_components(component_list, logger: 'BoundLogger' = None) -> None:
        """
        Combine multiple `SolutionComponent` instances with the same CAS number.
        Following properties are accumulated for combined components: mass, volume.
        """
        combined_components = {}
        unprocessed_components = []
        for component in component_list:
            if not component.pure_substance or not component.pure_substance.cas_number:
                unprocessed_components.append(component)
                continue
            comparison_key = component.pure_substance.cas_number
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
            else:
                combined_components[comparison_key] = component

        combined_components = list(combined_components.values())
        combined_components.extend(unprocessed_components)

        return combined_components

    def compute_volume(self, logger: 'BoundLogger') -> None:
        """
        Compute the volume of the solution.

        Args:
            logger (BoundLogger): A structlog logger.
        """
        self.calculated_volume = 0 * ureg('milliliter')
        for component in self.components:
            if isinstance(component, (SolutionComponent, SolutionComponentReference)):
                if component.volume:
                    self.calculated_volume += component.volume

    def normalize(self, archive, logger) -> None:
        self.solvents, self.solutes = [], []

        self.compute_volume(logger)
        if self.measured_volume:
            volume = self.measured_volume
        else:
            volume = self.calculated_volume

        for component in self.components:
            if isinstance(component, SolutionComponent):
                component.mass_fraction = None
                component.compute_molar_concentration(volume, logger)
                if component.component_role == 'Solvent':
                    self.solvents.append(component.m_copy())
                elif component.component_role == 'Solute':
                    self.solutes.append(component.m_copy())
            elif isinstance(component, SolutionComponentReference):
                # add solutes and solvents from the solution
                # while taking the volume used into account
                if component.reference:
                    scaler = 1
                    if component.volume:
                        # update scaler based on the volume used
                        if component.reference.measured_volume:
                            total_available_volume = component.reference.measured_volume
                        else:
                            total_available_volume = (
                                component.reference.calculated_volume
                            )
                        if total_available_volume:
                            scaler = component.volume / total_available_volume

                    if component.reference.solvents:
                        for solvent in component.reference.solvents:
                            self.solvents.append(solvent.m_copy())
                            if self.solvents[-1].volume:
                                self.solvents[-1].volume *= scaler
                            if self.solvents[-1].mass:
                                self.solvents[-1].mass *= scaler
                            self.solvents[-1].compute_molar_concentration(
                                volume, logger
                            )
                    if component.reference.solutes:
                        for solute in component.reference.solutes:
                            self.solutes.append(solute.m_copy())
                            if self.solutes[-1].volume:
                                self.solutes[-1].volume *= scaler
                            if self.solutes[-1].mass:
                                self.solutes[-1].mass *= scaler
                            self.solutes[-1].compute_molar_concentration(volume, logger)

        self.solvents = self.combine_components(self.solvents, logger)
        self.solutes = self.combine_components(self.solutes, logger)

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


class SolutionComponentReference(SolutionReference, BaseSolutionComponent):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'reference',
                    'lab_id',
                    'volume',
                ],
                visible=Filter(
                    exclude=[
                        'mass_fraction',
                        'mass',
                    ],
                ),
            ),
        )
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

    def normalize(self, archive, logger):
        if self.reference:
            if not self.name:
                self.name = self.reference.name
            # assume entire volume of the solution is used
            if self.reference.measured_volume:
                available_volume = self.reference.measured_volume
            elif self.reference.calculated_volume:
                available_volume = self.reference.calculated_volume
            else:
                available_volume = None
        if not self.volume and available_volume:
            self.volume = available_volume
        if self.volume and available_volume:
            if self.volume > available_volume:
                logger.warning(
                    f'The volume used for the "{self.name}" is greater than the '
                    'available volume of the solution. Setting it to the available '
                    'volume.'
                )
            self.volume = available_volume
        super().normalize(archive, logger)


class SolutionPreparationStep(ProcessStep):
    m_def = Section(
        description="""
        Class to put together the steps of a solution preparation.
        """,
    )


class MeasurementMethodology(ArchiveSection):
    instrument = SubSection(section_def=InstrumentReference)


class Pipetting(MeasurementMethodology):
    pipette_volume = Quantity()  # TODO populate from the instrument section


class Scaling(MeasurementMethodology):
    precision = Quantity()  # TODO populate from the instrument section
    container_mass = Quantity(
        type=np.float64,
        description='The mass of the container.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram',
            minValue=0,
        ),
        unit='gram',
    )
    gross_mass = Quantity(
        type=np.float64,
        description='The mass of the material including the container.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram',
            minValue=0,
        ),
        unit='gram',
    )


class AddSolutionComponent(SolutionPreparationStep):
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
    solution_component = SubSection(section_def=BaseSolutionComponent)
    measurement = SubSection(section_def=MeasurementMethodology)

    def normalize(self, archive, logger):
        if self.solution_component and isinstance(
            self.solution_component, SolutionComponent
        ):
            if not self.name:
                if self.solution_component.name:
                    self.name = f'Add {self.solution_component.name}'
                else:
                    self.name = f'Add {self.solution_component.component_role}'
        elif (
            self.solution_component
            and isinstance(self.solution_component, SolutionComponentReference)
            and self.solution_component.reference
        ):
            solution = self.solution_component.reference
            if not self.name:
                if solution.name:
                    self.name = f'Add {solution.name}'
                else:
                    self.name = 'Add Solution'

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
            if isinstance(step, AddSolutionComponent):
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
            if isinstance(step, AddSolutionComponent):
                if step.solution_component:
                    self.solution.components.append(step.solution_component)

        if not self.solution.name:
            self.solution.name = f'Solution from {self.name}'
        self.solution.normalize(archive, logger)

        # create a reference to the solution
        if self.solution and not self.solution_reference:
            self.solution_reference = SolutionReference()
        self.solution_reference.reference = self.create_solution_entry(archive, logger)

        super().normalize(archive, logger)
