from typing import TYPE_CHECKING, Union

from nomad.datamodel.data import (
    ArchiveSection,
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    Filter,
    SectionProperties,
)
from nomad.datamodel.metainfo.basesections import (
    Component,
    CompositeSystem,
    CompositeSystemReference,
    InstrumentReference,
    Process,
    ProcessStep,
    PubChemPureSubstanceSection,
    PureSubstanceComponent,
    SystemComponent,
)
from nomad.metainfo import (
    Datetime,
    MEnum,
    Quantity,
    SchemaPackage,
    Section,
    SubSection,
)
from nomad.units import ureg

from nomad_material_processing.solution.utils import (
    create_archive,
    create_unique_filename,
)

if TYPE_CHECKING:
    from nomad.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

from nomad.config import config

m_package = SchemaPackage(
    aliases=[
        'nomad_material_processing.solution',
    ],
)

configuration = config.get_plugin_entry_point(
    'nomad_material_processing.solution:schema'
)


class MolarConcentration(ArchiveSection):
    """
    The molar concentration of a component in a solution.
    """

    m_def = Section(
        description='The molar concentration of a component in a solution.',
    )
    calculated_concentration = Quantity(
        type=float,
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
        type=float,
        description=(
            """The concentration observed or measured
            with some characterization technique."""
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
    Section for description of solution storage conditions.
    """

    m_def = Section(
        description='The storage conditions of the solution.',
    )
    start_date = Quantity(
        type=Datetime,
        description='The start date and time of the storage.',
        a_eln=ELNAnnotation(
            component='DateTimeEditQuantity',
        ),
    )
    end_date = Quantity(
        type=Datetime,
        description='The expiry date and time of the storage.',
        a_eln=ELNAnnotation(
            component='DateTimeEditQuantity',
        ),
    )
    temperature = Quantity(
        type=float,
        description='The temperature of the storage.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius',
        ),
        unit='kelvin',
    )
    atmosphere = Quantity(
        type=str,
        description='The atmosphere of the storage.',
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['Ar', 'N2', 'Air'],
            ),
        ),
    )
    comments = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='RichTextEditQuantity',
        ),
    )


class BaseSolutionComponent(Component):
    """
    Base class for a component added to the solution.
    """

    volume = Quantity(
        type=float,
        description='The volume of the liquid component.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='milliliter',
            minValue=0,
        ),
        unit='liter',
    )


class SolutionComponent(PureSubstanceComponent, BaseSolutionComponent):
    """
    Section for a component added to the solution.
    """

    # TODO get the density of the component automatically if not provided
    m_def = Section(
        description='A component added to the solution.',
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
        """,  # noqa: E501
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )
    mass = Quantity(
        type=float,
        description='The mass of the component without the container.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram',
            minValue=0,
        ),
        unit='kilogram',
    )
    density = Quantity(
        type=float,
        description='The density of the liquid component.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram / liter',
            minValue=0,
        ),
        unit='kilogram / liter',
    )
    molar_concentration = SubSection(section_def=MolarConcentration)
    pure_substance = SubSection(section_def=PubChemPureSubstanceSection)

    def _calculate_moles(self, logger: 'BoundLogger' = None) -> Union[Quantity, None]:
        """
        A private method to calculate the moles of a component in the solution.

        Args:
            component (SolutionComponent): The component to calculate the moles for.
            logger (BoundLogger): A structlog logger.

        Returns:
            Union[Quantity, None]: The moles of the component in the solution.
        """
        if self.volume and self.density:
            self.mass = self.volume * self.density

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
        moles = self.mass / (self.pure_substance.molecular_mass * ureg.N_A)
        return moles.to_base_units()

    def calculate_molar_concentration(
        self, volume: Quantity, logger: 'BoundLogger' = None
    ) -> None:
        """
        Calculate the molar concentration of the component
        in a given volume of solution.

        Args:
            volume (Quantity): The volume of the solution.
            logger (BoundLogger): A structlog logger.
        """
        if not volume:
            if logger:
                logger.warning(
                    f'Volume of the solution is missing, can not calculate the '
                    f'concentration of the component {self.name}.'
                )
            return
        if not self.molar_concentration:
            self.molar_concentration = MolarConcentration()
        moles = self._calculate_moles(logger)
        if moles:
            self.molar_concentration.calculated_concentration = moles / volume

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        Normalize method for the `SolutionComponent` section. Sets the mass if volume
        and density are provided.

        Args:
            archive (EntryArchive): A NOMAD archive.
            logger (BoundLogger): A structlog logger.
        """
        if self.substance_name and self.pure_substance is None:
            self.pure_substance = PubChemPureSubstanceSection(name=self.substance_name)
            self.pure_substance.normalize(archive, logger)
        if self.volume and self.density:
            self.mass = self.volume * self.density
        super().normalize(archive, logger)


class Solution(CompositeSystem, EntryData):
    """
    Section for decribing liquid solutions.
    """

    # TODO make the solvents, solutes, and elemental_composition subsection noneditable.
    m_def = Section(
        description='A homogeneous liquid mixture composed of two or more substances.',
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'datetime',
                    'lab_id',
                    'ph_value',
                    'calculated_volume',
                    'measured_volume',
                    'mass',
                    'density',
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
        type=float,
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            minValue=0,
            maxValue=14,
        ),
    )
    density = Quantity(
        description='The density of the solution.',
        type=float,
        a_eln=ELNAnnotation(
            defaultDisplayUnit='gram / milliliter',
        ),
        unit='kilogram / liter',
    )
    mass = Quantity(
        description='The mass of the solution.',
        type=float,
        a_eln=ELNAnnotation(
            defaultDisplayUnit='gram',
        ),
        unit='kilogram',
    )
    calculated_volume = Quantity(
        description="""The final expected volume of the solution, which is the sum of
        volume of its liquid components.
        """,
        type=float,
        a_eln=ELNAnnotation(
            defaultDisplayUnit='milliliter',
        ),
        unit='liter',
    )
    measured_volume = Quantity(
        description='The volume of the solution as observed or measured.',
        type=float,
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='milliliter',
            minValue=0,
        ),
        unit='liter',
    )
    components = SubSection(
        section_def=BaseSolutionComponent,
        description='The components of the solution',
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
        Combine multiple `SolutionComponent` instances with the same PubChem CID number.
        Following properties are accumulated for combined components: mass, volume.
        If the mass or volume is not provided for a component, it is not combined.

        Args:
            component_list (list): A list of `SolutionComponent` instances.
            logger (BoundLogger): A structlog logger.
        """
        combined_components = {}
        unprocessed_components = []
        for component in component_list:
            if not component.pure_substance.pub_chem_cid:
                unprocessed_components.append(component.m_copy(deep=True))
                continue
            comparison_key = component.pure_substance.pub_chem_cid
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
                combined_components[comparison_key] = component.m_copy(deep=True)

        combined_components = list(combined_components.values())
        combined_components.extend(unprocessed_components)

        return combined_components

    def calculate_volume(self, logger: 'BoundLogger' = None) -> None:
        """
        Calculate the volume of the solution by adding the volumes of its components.

        Args:
            logger (BoundLogger): A structlog logger.
        """
        self.calculated_volume = ureg.Quantity(0, 'milliliter')
        for component in self.components:
            if not component.volume:
                if component.component_role == 'Solvent' and logger:
                    logger.warning(
                        f'The volume of the solvent component "{component.name}" is '
                        'missing.'
                    )
                continue
            self.calculated_volume += component.volume

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:  # noqa: PLR0912, PLR0915
        """
        Normalize method for the `Solution` section. Calculate the total volume of the
        solution. Populates the solvents and solutes with the components based on the
        `component_role`. If a component doesn't have pure_substance section, it is
        skipped. In case of components that are solutions, the quantity of their
        solvents and solutes is scaled based on their quantity used. Combines the
        components with the same PubChem CID. Set the mass, density, and elemental
        composition of the solution.

        Args:
            archive (EntryArchive): A NOMAD archive.
            logger (BoundLogger): A structlog logger.
        """
        self.solvents, self.solutes = [], []

        self.calculate_volume(logger)
        volume = self.calculated_volume
        if self.measured_volume:
            volume = self.measured_volume

        for component in self.components:
            if isinstance(component, SolutionComponent):
                if not component.pure_substance or not component.mass:
                    logger.warning(
                        f'Either the pure_substance sub_section or mass for the '
                        f'component "{component.name}" is missing. Not adding it to '
                        f'the "{component.component_role.lower()}' + 's' + '" list.'
                    )
                    continue
                component.mass_fraction = None
                component.calculate_molar_concentration(volume, logger)
                if component.component_role == 'Solvent':
                    self.solvents.append(component.m_copy(deep=True))
                elif component.component_role == 'Solute':
                    self.solutes.append(component.m_copy(deep=True))
            elif isinstance(component, SolutionComponentReference):
                # add solutes and solvents from the solution
                # while taking the volume used into account
                if component.system:
                    scaler = 1
                    if component.volume:
                        # update scaler based on the volume used
                        total_available_volume = component.system.calculated_volume
                        if component.system.measured_volume:
                            total_available_volume = component.system.measured_volume
                        if total_available_volume:
                            scaler = component.volume / total_available_volume

                    if component.system.solvents:
                        for solvent in component.system.solvents:
                            self.solvents.append(solvent.m_copy(deep=True))
                            if self.solvents[-1].volume:
                                self.solvents[-1].volume *= scaler
                            if self.solvents[-1].mass:
                                self.solvents[-1].mass *= scaler
                    if component.system.solutes:
                        for solute in component.system.solutes:
                            self.solutes.append(solute.m_copy(deep=True))
                            if self.solutes[-1].volume:
                                self.solutes[-1].volume *= scaler
                            if self.solutes[-1].mass:
                                self.solutes[-1].mass *= scaler

        self.solvents = self.combine_components(self.solvents, logger)
        self.solutes = self.combine_components(self.solutes, logger)

        for component in self.solvents:
            component.calculate_molar_concentration(volume, logger)
        for component in self.solutes:
            component.calculate_molar_concentration(volume, logger)

        mass = 0
        self.mass = None
        self.density = None
        for component in self.solvents + self.solutes:
            mass += component.mass
        if mass:
            self.mass = mass
            if volume:
                self.density = self.mass / volume

        # TODO check if the elemental_composition is adjusted based on the volume used
        # of the starter solutions
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


class SolutionComponentReference(SystemComponent, BaseSolutionComponent):
    """
    Section for referencing a solution that is being used as a component.
    """

    m_def = Section(
        description='A reference to the solution that is being used as a component.',
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'system',
                    'volume',
                    'mass',
                ],
                visible=Filter(
                    exclude=[
                        'mass_fraction',
                    ],
                ),
            ),
        ),
    )
    system = Quantity(
        type=Solution,  # Reference(System.m_def)
        description='A reference to the solution.',
        a_eln=dict(component='ReferenceEditQuantity'),
    )
    mass = Quantity(
        type=float,
        description='The mass of the solution used.',
        a_eln=ELNAnnotation(
            defaultDisplayUnit='gram',
            minValue=0,
        ),
        unit='kilogram',
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        Normalize method for the `SolutionComponentReference` section. Sets the name and
        volume of the component solution based on the reference.

        Args:
            archive (EntryArchive): A NOMAD archive.
            logger (BoundLogger): A structlog logger.
        """
        if self.system:
            if not self.name:
                self.name = self.system.name
            available_volume = self.system.calculated_volume
            if self.system.measured_volume:
                available_volume = self.system.measured_volume
            if not self.volume:
                # assume entire volume of the solution is used
                self.volume = available_volume
            elif self.volume > available_volume:
                logger.warning(
                    f'The volume used for the "{self.name}" is greater than the '
                    'available volume of the solution. Setting it to the available '
                    'volume.'
                )
                self.volume = available_volume
            if self.system.density:
                self.mass = self.system.density * self.volume
        super().normalize(archive, logger)


class SolutionPreparationStep(ProcessStep):
    """
    Base section for steps of a solution preparation process.
    """


class MeasurementMethodology(ArchiveSection):
    """
    Base section for measurement methodology. This class can be extended to describe
    specific measurement methodologies, associated errors bounds, and instrument used.
    """

    instrument = SubSection(section_def=InstrumentReference)


class Pipetting(MeasurementMethodology):
    """
    Section for pipetting of liquids.
    """

    # TODO populate `pipette_volume` from the instrument
    pipette_volume = Quantity(
        type=float,
        description='The volume of the pipette used.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='milliliter',
            minValue=0,
        ),
        unit='liter',
    )


class Scaling(MeasurementMethodology):
    """
    Section for scaling or weighing substances.
    """

    # TODO populate `precision` from the instrument
    precision = Quantity(
        type=float,
        description='The precision of the weighing instrument.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram',
            minValue=0,
        ),
        unit='kilogram',
    )
    container_mass = Quantity(
        type=float,
        description='The mass of the container.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram',
            minValue=0,
        ),
        unit='kilogram',
    )
    gross_mass = Quantity(
        type=float,
        description='The mass of the material including the container.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram',
            minValue=0,
        ),
        unit='kilogram',
    )


class AddSolutionComponent(SolutionPreparationStep):
    """
    Section for adding a component to the solution.
    """

    m_def = Section(
        description='Step for adding a component to the solution.',
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

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        Normalize method for the `AddSolutionComponent` section. Sets the name of the
        step based on component name or component role.

        Args:
            archive (EntryArchive): A NOMAD archive.
            logger (BoundLogger): A structlog logger.
        """
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
            and self.solution_component.system
        ):
            solution = self.solution_component.system
            if not self.name:
                if solution.name:
                    self.name = f'Add {solution.name}'
                else:
                    self.name = 'Add Solution'

        super().normalize(archive, logger)


class Agitation(SolutionPreparationStep):
    """
    Section for agitation or mixing step.
    """

    m_def = Section(
        description='Generic agitation or mixing step for solution preparation.',
    )
    temperature = Quantity(
        type=float,
        description='The temperature of the mixing process.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius',
        ),
        unit='kelvin',
    )
    container_type = Quantity(
        type=str,
        description='The type of container used for mixing.',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        Normalize method for the `Agitation` section. Sets the name of the step.

        Args:
            archive (EntryArchive): A NOMAD archive.
            logger (BoundLogger): A structlog logger.
        """
        if not self.name:
            self.name = self.__class__.__name__
        super().normalize(archive, logger)


class Sonication(Agitation):
    """
    Section for sonication step.
    """

    m_def = Section(
        description='Sonication step for solution preparation.',
    )
    frequency = Quantity(
        type=float,
        description='The frequency of the sonication instrument.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='Hz',
        ),
        unit='Hz',
    )


class MechanicalStirring(Agitation):
    """
    Section for mechanical stirring step.
    """

    m_def = Section(
        description='Mechanical stirring step for solution preparation.',
    )
    rotation_speed = Quantity(
        type=float,
        description='The rotation speed of the stirrer.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='rpm',
        ),
        unit='rpm',
    )


class SolutionPreparation(Process, EntryData):
    """
    Section for solution preparation. This section can be used to describe the steps
    involved in preparing a solution and create a `Solution` entry based on them.
    """

    # TODO populate the instruments section based on the steps.methodology.instrument
    m_def = Section(
        description='Section for describing steps of solution preparation.',
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
                    'solution_name',
                    'datetime',
                    'end_time',
                    'lab_id',
                    'location',
                    'description',
                    'steps',
                    'solution',
                    'instruments',
                ],
            ),
        ),
    )
    solution_name = Quantity(
        type=str,
        description='The name of the solution.',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
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

    def create_solution_entry(
        self, solution: 'Solution', archive: 'EntryArchive', logger: 'BoundLogger'
    ) -> str:
        """
        Create an entry using the solution section and return the reference to it.

        Args:
            solution (Solution): The solution section.
            archive (EntryArchive): A NOMAD archive.
            logger (BoundLogger): A structlog logger.

        Returns:
            str: The reference to the solution entry.
        """
        from nomad.datamodel import EntryArchive

        if self.solution_name:
            solution_file_name = (
                f'{self.solution_name.lower().replace(" ", "_")}.archive.json'
            )
        else:
            solution_file_name = create_unique_filename(
                archive=archive, prefix='unnamed_solution'
            )
            self.solution_name = solution_file_name.split('.')[0].replace('_', ' ')
        solution_entry = EntryArchive(data=solution, m_context=archive.m_context)
        solution_reference = create_archive(
            entry_dict=solution_entry.m_to_dict(with_root_def=True),
            context=archive.m_context,
            filename=solution_file_name,
            file_type='json',
            logger=logger,
            overwrite=True,
        )

        return solution_reference

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        Normalize method for the `SolutionPreparation` section. Sets the solution name,
        creates a `Solution` section, and adds the solution components to it. Then,
        creates an entry for the solution and adds a reference to it.

        Args:
            archive (EntryArchive): A NOMAD archive.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)

        if not any(isinstance(s, AddSolutionComponent) for s in self.steps):
            return

        # prepare the solution
        components = [
            step.solution_component.m_copy(deep=True)
            for step in self.steps
            if isinstance(step, AddSolutionComponent)
        ]
        if not components:
            return
        solution = Solution(
            name=self.solution_name,
            components=components,
        )
        solution.normalize(archive, logger)
        if not self.solution:
            self.solution = SolutionReference()
        self.solution.reference = self.create_solution_entry(solution, archive, logger)


m_package.__init_metainfo__()
