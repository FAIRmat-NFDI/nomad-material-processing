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


class BaseSolutionComponent(ArchiveSection):
    m_def = Section(
        description="""
        Base class to put together `SolutionComponent` and `SolutionComponentReference`
        classes.
        """,
    )


class SolutionPreparationStep(ProcessStep):
    m_def = Section(
        description="""
        Class to put together the steps of a solution preparation.
        """,
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
    purity_percentage = Quantity(
        type=np.float64,
        description='The purity of the liquid component in fraction.',
        a_eln=dict(
            component='NumberEditQuantity',
            maxValue=100,
            minValue=0,
        ),
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


class ComponentConcentration(ArchiveSection):
    """
    The concentration of a component in a mixed material.
    """

    component_reference = Quantity(
        type=SolutionComponent,
        description='A reference to a NOMAD `SolutionComponent` sub-section.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )
    theoretical_concentration = Quantity(
        type=np.float64,
        description='The concentration planned for the component.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='mol / liter',
            minValue=0,
        ),
        unit='mol / liter',
    )
    actual_concentration = Quantity(
        type=np.float64,
        description='The concentration calculated from the component moles and total volume.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='mol / liter',
            minValue=0,
        ),
        unit='mol / liter',
    )


class SolutionProperties(ArchiveSection):
    """
    Solution properties class.
    """

    m_def = Section(
        description="""
        The properties of the solution.
        """,
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
    final_volume = Quantity(
        description="""The final volume of the solution, which is the sum of
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
    components_concentration = SubSection(
        section_def=ComponentConcentration,
        repeats=True,
    )


class Solution(CompositeSystem, EntryData):
    """
    Base class for a solution
    """

    m_def = Section(
        description="""
        The resulting liquid obtained after the Solution preparation steps.
        """,
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
    properties = SubSection(section_def=SolutionProperties)

    def normalize(self, archive, logger) -> None:
        # TODO
        # generate the solution properties section
        # - calculate the total volume of the solution
        #   by summing the volumes of the liquid components and solution from references
        # - calculate the actual_concentration of the components
        #   solids: calculate the moles based on molar mass and mass
        #   liquids: calculate the moles based on the volume and density
        #     use the total volume of the solution to calculate the concentration
        #   solution reference: get each component from the reference and recompute the
        #     molarity based on the new concentration
        # also, when adding a new component, always check if it already exists, in which
        # case, update the concentration.
        super(Solution, self).normalize(archive, logger)

        self.components = []
        if self.solutes:
            self.components.extend(self.solutes)
        if self.solvents:
            self.components.extend(self.solvents)


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


class AddMaterial(SolutionPreparationStep):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'start_time',
                    'material_type',
                    'comment',
                    'duration',
                    'material',
                ],
            ),
        ),
    )
    material_type = Quantity(
        type=MEnum(
            'Solvent',
            'Solute',
            'Compound',
        ),
        description="""
        The type of material added to the solution.
        | material type | description |
        | ------------- | ----------- |
        | Solvent       | Solvent added to the solution. |
        | Solute        | Solute added to the solution. |
        | Compound      | A compound that does not dissolve in the solution. |
        """,
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )

    solution_component = SubSection(section_def=BaseSolutionComponent)

    def normalize(self, archive, logger):
        if not self.name:
            if self.material_type:
                self.name = f'Add {self.material_type}'
            else:
                self.name = 'Add Material'
        return super().normalize(archive, logger)
        # TODO based on the material type, add the material to the solvent or solute
        # if the material type is compound, only add it to the components list


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
                    'solvent',
                    'solutes',
                    'steps',
                    'instruments',
                ],
            ),
        ),
    )
    solvents = SubSection(
        link='https://doi.org/10.1351/goldbook.S05751',
        section_def=LiquidSolutionComponent,
        description="""
        The term applied to the whole initial liquid phase containing the extractant.
        """,
        repeats=True,
    )
    solutes = SubSection(
        link='https://doi.org/10.1351/goldbook.S05744',
        section_def=Component,
        description="""
        The minor component of a solution which is regarded as having been dissolved
        by the solvent.
        """,
        repeats=True,
    )
    solution = SubSection(
        section_def=CompositeSystem,
    )
    steps = SubSection(
        section_def=SolutionPreparationStep,
        description="""
        Ordered list of steps of the solution preparation process.
        """,
        repeats=True,
    )

    def normalize(self, archive, logger) -> None:
        # TODO create an entry for the solution once the solvent and solutes are added
        # and update the reference to the solution in the solution section.

        super(SolutionPreparation, self).normalize(archive, logger)


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