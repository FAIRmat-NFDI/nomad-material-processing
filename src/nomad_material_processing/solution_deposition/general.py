from nomad.datamodel.metainfo.annotations import ELNAnnotation
from nomad.datamodel.metainfo.basesections import CompositeSystemReference, ProcessStep
from nomad.metainfo import Quantity, SchemaPackage, Section, SubSection

from nomad_material_processing.general import SampleDeposition, ThinFilmReference
from nomad_material_processing.solution.general import SolutionReference

m_package = SchemaPackage()


class SolutionDepositionStep(ProcessStep):
    """An operation within a deposition process using a liquid solution."""

    solution = SubSection(
        section_def=SolutionReference,
        description='The solution dispensed during this deposition step.',
    )
    dispensed_volume = Quantity(
        type=float,
        unit='meter ** 3',
        description='The volume of solution dispensed during this step, '
        'rather than the total volume of the referenced stock solution.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='microliter',
            minValue=0,
        ),
    )
    substrate = SubSection(
        section_def=CompositeSystemReference,
        description='The existing material surface receiving the deposition, '
        'such as a bare substrate or a thin-film stack.',
    )
    layer = SubSection(
        section_def=ThinFilmReference,
        description='The thin film deposited during this step. '
        'Film composition and geometry belong to the referenced film.',
    )


class SolutionDeposition(SampleDeposition):
    """Deposition of material from a liquid solution onto an existing surface."""

    m_def = Section(
        links=['http://purl.obolibrary.org/obo/CHMO_0001312'],
    )

    steps = SubSection(
        section_def=SolutionDepositionStep,
        repeats=True,
        description='The ordered steps of the solution deposition process.',
    )


m_package.__init_metainfo__()
