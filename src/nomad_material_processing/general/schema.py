from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum

import numpy as np
from nomad.datamodel.data import EntryData, ArchiveSection

from nomad.metainfo import (
    Quantity,
    SubSection,
    Section,
    MEnum,
)

from nomad.datamodel.metainfo.basesections import (
    CompositeSystem,
    ProcessStep,
    Process,
    CompositeSystemReference,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
)

from nomad.metainfo import (
    SectionProxy,
    Reference,
)


class Recipe(ArchiveSection):
    """
    A Recipe for a material processing experiment.

    This class will be subclassed for each process that needs a recipe.

    The subclass will inherit Recipe and a specific Process class.

    The only difference between the Recipe and the actual Process is that
    the datetime and the input samples Entities are hidden in the Recipe.
    """

    pass


class EtchingStep(ProcessStep):
    """
    A step of etching process.
    """

    m_def = Section()
    duration = Quantity(
        type=np.float64,
        description='The elapsed time since the annealing process started.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='minute'
        ),
        unit='second',
    )
    temperature = Quantity(
        type=np.float64,
        description='The temperature of the etching process.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'celsius'},
        unit='celsius',
    )
    agitation = Quantity(
        type=MEnum(
            'Magnetic Stirring',
            'Sonication',
        ),
        description='The agitation method used during the etching process.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.EnumEditQuantity,
        ),
    )
    etching_reagents = SubSection(section_def=CompositeSystem, repeats=True)


class Etching(Process, EntryData):
    """
    Selectively remove material from a surface using chemical or physical processes
    to create specific patterns or structures.
    """

    m_def = Section(
        a_eln=None,
        links=['http://purl.obolibrary.org/obo/CHMO_0001558'],
    )
    recipe = Quantity(
        type=Reference(SectionProxy('EtchingRecipe')),
        description=""" The recipe used for the process. If a recipe is found,
           all the data is copied from the Recipe within the Process.
           """,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
        ),
    )
    steps = SubSection(
        description="""
        The steps of the etching process.
        """,
        section_def=EtchingStep,
        repeats=True,
    )


class EtchingRecipe(Etching, Recipe, EntryData):
    """
    A Recipe for an etching process.
    """

    m_def = Section(
        a_eln={'hide': ['datetime', 'samples']},
    )


class AnnealingStep(ProcessStep):
    """
    A step of annealing process.
    """

    m_def = Section()
    duration = Quantity(
        type=np.float64,
        description='The elapsed time since the annealing process started.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='minute'
        ),
        unit='second',
    )
    temperature = Quantity(
        type=np.float64,
        description='The temperature of the etching process.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'celsius'},
        unit='celsius',
    )


class Annealing(Process, EntryData):
    """
    Heat treatment process used to alter the material's properties,
    such as reducing defects, improving crystallinity, or relieving internal stresses.
    """

    m_def = Section(
        links=['http://purl.obolibrary.org/obo/CHMO_0001465'],
    )
    recipe = Quantity(
        type=Reference(SectionProxy('AnnealingRecipe')),
        description=""" The recipe used for the process. If a recipe is found,
           all the data is copied from the Recipe within the Process.
           """,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
        ),
    )
    duration = Quantity(
        type=np.float64,
        description='The elapsed time since the annealing process started.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='minute'
        ),
        unit='second',
    )
    steps = SubSection(
        description="""
        The steps of the annealing process.
        """,
        section_def=AnnealingStep,
        repeats=True,
    )


class AnnealingRecipe(Annealing, Recipe, EntryData):
    """
    A Recipe for an annealing process.
    """

    m_def = Section(
        a_eln={'hide': ['datetime', 'samples']},
    )


class CleaningStep(ProcessStep):
    """
    A step of cleaning process.
    """

    m_def = Section()
    duration = Quantity(
        type=np.float64,
        description='The elapsed time since the cleaning process started.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='minute'
        ),
        unit='second',
    )
    temperature = Quantity(
        type=np.float64,
        description='The temperature of the cleaning process.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'celsius'},
        unit='celsius',
    )
    agitation = Quantity(
        type=MEnum(
            'Magnetic Stirring',
            'Sonication',
        ),
        description='The agitation method used during the cleaning process.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.EnumEditQuantity,
        ),
    )
    cleaning_reagents = SubSection(
        section_def=CompositeSystemReference,
    )


class Cleaning(Process, EntryData):
    """
    Surface cleaning in thin film material science involves removing contaminants
    and residues from a substrate's surface to ensure proper adhesion
    and uniformity of the thin film deposition.
    """

    m_def = Section(
        a_eln={'hide': ['steps']},
    )
    recipe = Quantity(
        type=Reference(SectionProxy('CleaningRecipe')),
        description=""" The recipe used for the process. If a recipe is found,
           all the data is copied from the Recipe within the Process.
           """,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
        ),
    )
    duration = Quantity(
        type=np.float64,
        description='The elapsed time since the annealing process started.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='minute'
        ),
        unit='second',
    )
    steps = SubSection(
        description="""
        The steps of the cleaning process.
        """,
        section_def=CleaningStep,
        repeats=True,
    )


class CleaningRecipe(Cleaning, Recipe, EntryData):
    """
    A Recipe for an cleaning process.
    """

    m_def = Section(
        a_eln={'hide': ['datetime', 'samples']},
    )
