from nomad.datamodel.data import ArchiveSection
from nomad.datamodel.metainfo.annotations import ELNAnnotation
from nomad.datamodel.metainfo.basesections import CompositeSystemReference, ProcessStep
from nomad.metainfo import Quantity, SchemaPackage, Section, SubSection

from nomad_material_processing.gas.general import Gas
from nomad_material_processing.general import SampleDeposition, ThinFilmReference
from nomad_material_processing.solution.general import SolutionReference
from nomad_material_processing.solution_deposition.flow_geometry import ImpingingJet

m_package = SchemaPackage()


class SolutionProcessingEnvironment(ArchiveSection):
    """The ambient conditions surrounding the sample during a deposition step."""

    atmosphere = SubSection(
        section_def=Gas,
        links=['https://purl.archive.org/tfsco/TFSCO_00001012'],
        description='The gas surrounding the sample, such as the nitrogen of a '
        'glovebox or ambient air, including measured impurities such as oxygen and '
        'water traces.',
    )
    temperature = Quantity(
        type=float,
        unit='kelvin',
        description='The ambient temperature, as opposed to the temperature of the '
        'sample or of the dispensed solution.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius',
        ),
    )
    pressure = Quantity(
        type=float,
        unit='pascal',
        links=['https://purl.archive.org/tfsco/TFSCO_00002027'],
        description='The ambient pressure.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            minValue=0,
        ),
    )
    relative_humidity = Quantity(
        type=float,
        unit='dimensionless',
        links=['https://purl.archive.org/tfsco/TFSCO_00001011'],
        description='The relative humidity of the ambient gas.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='percent',
            minValue=0,
        ),
    )


class SolutionProcessingStep(ProcessStep):
    """
    An operation within a solution deposition process, either depositing a liquid or
    treating the deposited film, for example by drying or annealing.
    """

    sample_temperature = Quantity(
        type=float,
        unit='kelvin',
        links=['https://purl.archive.org/tfsco/TFSCO_00009996'],
        description='The actual temperature of the sample during this step, as '
        'opposed to the set temperature of a heat source.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius',
        ),
    )
    environment = SubSection(
        section_def=SolutionProcessingEnvironment,
        description='The ambient conditions during this step that differ from the '
        'environment of the process. Each value given here overrides the '
        'corresponding process value for this step; values left empty are taken '
        'from the process environment. A step atmosphere replaces the process '
        'atmosphere as a whole.',
    )


class DepositionStep(SolutionProcessingStep):
    """A step in which a liquid solution is deposited onto the sample."""

    m_def = Section(
        links=['https://purl.archive.org/tfsco/TFSCO_00002051'],
    )

    solution = SubSection(
        section_def=SolutionReference,
        links=['http://purl.obolibrary.org/obo/CHEBI_75958'],
        description='The solution deposited during this step.',
    )
    solution_temperature = Quantity(
        type=float,
        unit='kelvin',
        links=['https://purl.archive.org/tfsco/TFSCO_00007018'],
        description='The temperature of the solution when it is deposited.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius',
        ),
    )

    deposited_layer = SubSection(
        section_def=ThinFilmReference,
        links=['https://purl.archive.org/tfsco/TFSCO_00000007'],
        description='The thin film deposited during this step. '
        'Film composition and geometry belong to the referenced film.',
    )


class TreatmentStep(SolutionProcessingStep):
    """
    A step in which the deposited film is treated, for example with an antisolvent,
    by drying or by annealing.
    """


class AntisolventTreatmentStep(TreatmentStep):
    """
    A step in which an antisolvent is applied to the wet film to extract the solvent
    and induce crystallization.
    """

    m_def = Section(
        links=['https://purl.archive.org/tfsco/TFSCO_00001052'],
    )

    antisolvent = SubSection(
        section_def=SolutionReference,
        links=['https://purl.archive.org/tfsco/TFSCO_00002155'],
        description='The antisolvent applied during this step.',
    )
    antisolvent_temperature = Quantity(
        type=float,
        unit='kelvin',
        description='The temperature of the antisolvent when it is applied.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius',
        ),
    )


class ImpingingJetAntisolventTreatmentStep(AntisolventTreatmentStep, ImpingingJet):
    """An antisolvent treatment in which a jet of antisolvent impinges on the film."""


class DryingStep(TreatmentStep):
    """A step in which the solvent evaporates from the wet film."""

    m_def = Section(
        links=['https://purl.archive.org/tfsco/TFSCO_00008011'],
    )


class NaturalDryingStep(DryingStep):
    """
    A drying step in which the solvent evaporates into the surrounding atmosphere
    without a gas stream, a vacuum or an additional heat source.
    """


class ImpingingJetDryingStep(DryingStep, ImpingingJet):
    """
    A drying step in which a gas jet from a nozzle, such as an air knife or a round
    nozzle, impinges on the wet film to induce crystallization.
    """

    m_def = Section(
        links=['https://purl.archive.org/tfsco/TFSCO_00001077'],
    )

    gas = SubSection(
        section_def=Gas,
        description='The gas of the jet.',
    )
    nozzle_pressure = Quantity(
        type=float,
        unit='pascal',
        links=['https://purl.archive.org/tfsco/TFSCO_00005022'],
        description='The gas pressure applied to the nozzle.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='bar',
            minValue=0,
        ),
    )


class VacuumDryingStep(DryingStep):
    """
    A drying step in which the pressure around the wet film is reduced to induce
    crystallization. The reached pressure is the pressure of the step environment.
    """

    m_def = Section(
        links=['https://purl.archive.org/tfsco/TFSCO_00002048'],
    )


class AnnealingStep(TreatmentStep):
    """
    A step in which the film is heated by a heat source such as a hot plate or an
    oven, optionally in a solvent vapor.
    """

    m_def = Section(
        links=['https://purl.archive.org/tfsco/TFSCO_00001033'],
    )

    heater_temperature = Quantity(
        type=float,
        unit='kelvin',
        description='The set temperature of the heat source, such as a hot plate or '
        'an oven. The actual sample temperature can be lower.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius',
        ),
    )


class ParameterVariation(ArchiveSection):
    """
    A step that some samples of the process went through instead of one of its nominal
    steps, for example one temperature of an annealing series.

    The replacing step takes the place of the replaced step for the named samples and
    is complete by itself: it takes no values from the replaced step, so a value left
    empty is not recorded for these samples. The replaced step still applies to all
    other samples, and all other steps still apply to the named samples.
    """

    replaced_step = Quantity(
        type=SolutionProcessingStep,
        description='The nominal process step that the named samples did not go '
        'through.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )
    samples = SubSection(
        section_def=CompositeSystemReference,
        repeats=True,
        description='The samples that went through the replacing step instead of the '
        'replaced step.',
    )
    replacing_step = SubSection(
        section_def=SolutionProcessingStep,
        description='The complete step that the named samples went through instead of '
        'the replaced step. It may be of another step type. Values left empty are not '
        'taken from the replaced step.',
    )


class SolutionDeposition(SampleDeposition):
    """Deposition of material from a liquid solution onto an existing surface."""

    m_def = Section(
        links=['http://purl.obolibrary.org/obo/CHMO_0001312'],
    )

    environment = SubSection(
        section_def=SolutionProcessingEnvironment,
        description='The ambient conditions of the process. Each value applies to '
        'every step that does not override it in its own environment.',
    )
    samples = SubSection(
        section_def=CompositeSystemReference,
        repeats=True,
        links=['https://purl.archive.org/tfsco/TFSCO_00005000'],
        description='The samples undergoing the process. A sample is the entity moving '
        'from one process step to the next, as opposed to the substrate, a composite '
        'system serving as the rigid or flexible starting point that holds the thin '
        'film.',
    )
    steps = SubSection(
        section_def=SolutionProcessingStep,
        repeats=True,
        description='The ordered nominal steps of the solution deposition process. '
        'They apply to all samples, except where a parameter variation replaces a step '
        'for some of them.',
    )
    parameter_variations = SubSection(
        section_def=ParameterVariation,
        repeats=True,
        description='The steps that some of the samples of the process went through '
        'instead of nominal steps, such as the members of a parameter series.',
    )


m_package.__init_metainfo__()
