from nomad.datamodel.data import ArchiveSection
from nomad.datamodel.metainfo.annotations import ELNAnnotation
from nomad.metainfo import Quantity, SchemaPackage

m_package = SchemaPackage()


class ImpingingJet(ArchiveSection):
    """
    Mixin for steps in which a fluid jet from a nozzle, such as a gas from an air knife
    or a liquid from a pipette, impinges on the film.
    """

    flow_rate = Quantity(
        type=float,
        unit='meter**3 / second',
        links=['https://purl.archive.org/tfsco/TFSCO_00002012'],
        description='The volumetric flow rate of the fluid through the nozzle.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='liter / minute',
            minValue=0,
        ),
    )
    nozzle_distance = Quantity(
        type=float,
        unit='meter',
        links=['https://purl.archive.org/tfsco/TFSCO_00003303'],
        description='The distance between the nozzle outlet and the substrate.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            minValue=0,
        ),
    )
    impingement_angle = Quantity(
        type=float,
        unit='degree',
        links=['https://purl.archive.org/tfsco/TFSCO_00005746'],
        description='The angle between the jet and the substrate surface.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='degree',
        ),
    )


m_package.__init_metainfo__()
