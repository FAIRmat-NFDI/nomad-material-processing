from typing import TYPE_CHECKING

from nomad.datamodel.data import ArchiveSection
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    Filter,
    SectionProperties,
)
from nomad.datamodel.metainfo.basesections import (
    PubChemPureSubstanceSection,
    PureSubstanceComponent,
)
from nomad.metainfo import Quantity, SchemaPackage, Section, SubSection

if TYPE_CHECKING:
    from nomad.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

m_package = SchemaPackage()

# Rounded gas specifications, such as 5 % in 95 %, sum to 1 within this tolerance.
MOLE_FRACTION_SUM_TOLERANCE = 1e-3


class GasComponent(PureSubstanceComponent):
    """A pure substance contained in a gas or gas mixture."""

    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                visible=Filter(
                    exclude=['mass', 'mass_fraction'],
                ),
            ),
        ),
    )

    mole_fraction = Quantity(
        type=float,
        unit='dimensionless',
        description='The amount of substance of this component divided by the total '
        'amount of substance of the gas. For ideal gases this equals the volume '
        'fraction, in which gas compositions are commonly specified. Leave it empty '
        'for the one component that makes up the balance of the gas.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='percent',
            minValue=0,
        ),
    )
    pure_substance = SubSection(
        section_def=PubChemPureSubstanceSection,
        description='The pure substance that is the component.',
    )


class Gas(ArchiveSection):
    """
    A gas or gas mixture, such as the atmosphere of a glovebox including its measured
    impurities, or a premixed process gas.

    The gas is a condition of the activity that contains it, not a material entity
    of the entry. It therefore does not derive an elemental composition, which NOMAD
    would add to the searchable material of the containing entry.
    """

    m_def = Section(
        links=['https://purl.archive.org/tfsco/TFSCO_00002107'],
    )

    name = Quantity(
        type=str,
        description='The name of the gas, such as "Nitrogen", "Air" or "Forming gas '
        '5 % H2 in N2". The name does not set the components.',
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
            props=dict(suggestions=['Nitrogen', 'Argon', 'Air']),
        ),
    )
    components = SubSection(
        section_def=GasComponent,
        repeats=True,
        description='The pure substances contained in the gas.',
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        Fills the mole fraction of the one component without it as the balance of the
        gas and warns when the mole fractions do not sum to 1.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)
        missing = [c for c in self.components if c.mole_fraction is None]
        if len(missing) > 1:
            return
        total = sum(
            c.mole_fraction.magnitude
            for c in self.components
            if c.mole_fraction is not None
        )
        if len(missing) == 1 and total <= 1:
            missing[0].mole_fraction = 1 - total
        elif self.components and abs(total - 1) > MOLE_FRACTION_SUM_TOLERANCE:
            logger.warning(
                f'The mole fractions of gas "{self.name}" sum to {total:.4f} '
                'instead of 1.'
            )


m_package.__init_metainfo__()
