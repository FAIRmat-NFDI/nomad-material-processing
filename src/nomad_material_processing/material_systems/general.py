"""
Module containing NOMAD classes for material systems.
To be moved to a more general plugin in the future.
"""

from typing import TYPE_CHECKING

import numpy as np
from ase.data import chemical_symbols
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
    CompositeSystem,
    PubChemPureSubstanceSection,
    PureSubstanceComponent,
)
from nomad.metainfo import (
    MEnum,
    Quantity,
    SchemaPackage,
    Section,
    SubSection,
)

if TYPE_CHECKING:
    from nomad.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

m_package = SchemaPackage(
    aliases=[
        'nomad_material_processing.material_systems',
    ],
)


class CrystalProperties(ArchiveSection):
    """
    Contains properties of a crystal structure.
    """


class Crystal(PureSubstanceComponent):
    # TODO should inherit from PureSubstance(System) instead, but since we are using
    # it as a component of DopedCrystal(CompositeSystem), it needs to be a component.
    # This will be fixed in the future when components are also made into systems in
    # base sections.

    m_def = Section(
        description='A pure substance having a crystalline structure.',
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'substance_name',
                    'molecular_formula',
                    'pure_substance',
                    'crystal_properties',
                ]
            )
        ),
    )
    molecular_formula = Quantity(
        type=str,
        description='Molecular formula of the component.',
        a_eln={'component': 'StringEditQuantity'},
    )
    pure_substance = SubSection(
        section_def=PubChemPureSubstanceSection,
    )
    crystal_properties = SubSection(
        section_def=CrystalProperties,
        description='Properties of the crystalline structure.',
    )

    def normalize(self, archive, logger: 'BoundLogger') -> None:
        # make PubChem API calls when required
        if self.pure_substance is None or self.pure_substance.iupac_name is None:
            pure_substance = PubChemPureSubstanceSection()
            if self.molecular_formula is not None:
                pure_substance.molecular_formula = self.molecular_formula
            pure_substance.normalize(archive, logger)
            if pure_substance.iupac_name is not None:
                # material was found in PubChem database
                self.pure_substance = pure_substance
                self.molecular_formula = pure_substance.molecular_formula
        super().normalize(archive, logger)


class ElementalImpurity(Crystal):
    """
    Section for elemental impurity in a crystal.
    """

    m_def = Section(
        description="""
        An elemental impurity added in small quantities which substitutes another
        element in the host crystal.
        """,
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'system',
                    'molecular_formula',
                    'substitution_element',
                    'nominal_concentration',
                    'measured_concentration',
                ],
            )
        ),
    )
    molecular_formula = Quantity(
        type=MEnum(chemical_symbols[1:]),
        description='The symbol of the impurity element, e.g., Pr.',
        a_eln=dict(component='AutocompleteEditQuantity'),
    )
    substitution_element = Quantity(
        type=MEnum(chemical_symbols[1:]),
        description=('The element in the host crystal that is being replaced.'),
        a_eln=dict(component='AutocompleteEditQuantity'),
    )
    nominal_concentration = Quantity(
        type=np.float64,
        description=(
            'Atomic fraction of solute element with respect to the '
            'substitution element determined during preparation. '
            'For example, 0.01 at. fraction Pr-doped LiYF4 is equivalent to '
            'Li(Pr0.01Y0.99)F4, where Y is the substitution element.'
        ),
        a_eln={
            'component': 'NumberEditQuantity',
            'minValue': 0,
            'maxValue': 1,
            'defaultDisplayUnit': 'dimensionless',
        },
        unit='dimensionless',
    )
    measured_concentration = Quantity(
        type=np.float64,
        description=(
            'Atomic fraction of solute element with respect to the '
            'substitution element measured in the prepared sample using techniques'
            'like Transmission Spectrophotometry.'
        ),
        a_eln={
            'component': 'NumberEditQuantity',
            'minValue': 0,
            'maxValue': 1,
            'defaultDisplayUnit': 'dimensionless',
        },
        unit='dimensionless',
    )


class MixedCrystal(CompositeSystem, EntryData):
    m_def = Section(
        links=['https://doi.org/10.1351/goldbook.M03940'],
        description=(
            'A crystal containing other constituents (impurities) which fit into and '
            'are distributed in the lattice of the host crystal.'
        ),
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'datetime',
                    'lab_id',
                    'molecular_formula',
                    'description',
                    'host',
                    'impurities',
                    'elemental_composition',
                    'crystal_properties',
                ],
                visible=Filter(
                    exclude=[
                        'components',
                    ],
                ),
            ),
        ),
    )
    molecular_formula = Quantity(
        type=str,
        description="""Molecular formula of the mixed crystal. Impurity concentrations
        is expressed relatively as fraction of substitution element. For example, 1 at.%
        Pr-doped LiYF4 is expressed as Li(Pr0.01Y0.99)F4.
        """,
        a_eln={'component': 'StringEditQuantity'},
    )
    host = SubSection(
        section_def=Crystal,
    )
    impurities = SubSection(
        section_def=ElementalImpurity,
        repeats=True,
    )
    crystal_properties = SubSection(
        section_def=CrystalProperties,
        description='Properties of the crystalline structure.',
    )

    def adjust_composition_for_impurity_substitution(
        self, archive: 'EntryArchive', logger: 'BoundLogger'
    ):
        """
        Adjust the atomic fraction of each element based on each impurity substitution.
        Dopants are solutes which are added in small quantities to the solvent.
        Dopant concentration is given as a percentage of the substitution element.
        It can be the measured concentration (first preference) or the nominal
        concentration.
        """

        # TODO: different calculation is required when one impurity substitutes multiple
        # elements in the host crystal (or) when multiple impurities substitute the same
        # element in the host crystal. Only the first case is currently handled.
        # There could be a third situation which is a mix of the two.

        if not self.host:
            return
        if not self.impurities:
            return
        for impurity in self.impurities:
            if impurity.measured_concentration is not None:
                impurity_concentration = impurity.measured_concentration
            elif impurity.nominal_concentration is not None:
                impurity_concentration = impurity.nominal_concentration
            else:
                continue

            # find the substitution element and the impurity in the elemental
            # composition and adjust their atomic fractions
            for element_substituted in self.elemental_composition:
                if element_substituted.element == impurity.substitution_element:
                    for element_substituting in self.elemental_composition:
                        if element_substituting.element == impurity.molecular_formula:
                            if element_substituting.atomic_fraction is None:
                                element_substituting.atomic_fraction = 0
                            element_substituting.atomic_fraction += (
                                impurity_concentration
                                * element_substituted.atomic_fraction
                            )
                            element_substituted.atomic_fraction -= (
                                element_substituting.atomic_fraction
                            )
                            break
                    break

    @staticmethod
    def derive_molecular_formula(host, impurities):
        """
        Derive the molecular formula of the solid solution based on impurity
        substitutions.
        """
        if host.molecular_formula:
            molecular_formula = host.molecular_formula
        else:
            return ''
        for impurity in impurities:
            if (
                impurity.molecular_formula is None
                or impurity.substitution_element is None
            ):
                continue
            if impurity.measured_concentration is not None:
                impurity_concentration = impurity.measured_concentration
            elif impurity.nominal_concentration is not None:
                impurity_concentration = impurity.nominal_concentration
            else:
                continue
            fractional_symbol = (
                '('
                + impurity.molecular_formula
                + f'{round(impurity_concentration.magnitude, 2):.2f}'
                + ' '
                + impurity.substitution_element
                + f'{round(1 - impurity_concentration.magnitude, 2):.2f}'
                + ')'
            )
            molecular_formula = molecular_formula.replace(
                impurity.substitution_element, fractional_symbol
            )

        return molecular_formula

    def normalize(self, archive, logger: 'BoundLogger') -> None:
        self.components = []
        self.elemental_composition = []
        if self.host:
            self.components.append(self.host)
        if self.impurities:
            for impurity in self.impurities:
                self.components.append(impurity)
        super().normalize(archive, logger)

        if self.host and self.impurities:
            self.adjust_composition_for_impurity_substitution(archive, logger)
            # reset the mass fractions and recalculate them
            for element in self.elemental_composition:
                element.mass_fraction = None
            super().normalize(archive, logger)

            self.molecular_formula = self.derive_molecular_formula(
                host=self.host, impurities=self.impurities
            )


class PolyCrystal(Crystal):
    """
    Section for a polycrystalline material.
    """

    # TODO add more properties specific to polycrystallinty

    m_def = Section(
        description='A pure substance having a polycrystalline structure.',
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'substance_name',
                    'molecular_formula',
                    'pure_substance',
                    'crystal_properties',
                ]
            )
        ),
    )
    grain_size = Quantity(
        type=float,
        description='Average grain size of the polycrystalline material.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'micrometer'},
        unit='meter',
    )


class MixedPolyCrystal(MixedCrystal):
    """
    Section for a mixed crystal with polycrystalline structure.
    """

    m_def = Section(
        description=('A polycrystalline substance doped with impurities.'),
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'datetime',
                    'lab_id',
                    'molecular_formula',
                    'description',
                    'host',
                    'impurities',
                    'elemental_composition',
                    'crystal_properties',
                ],
                visible=Filter(
                    exclude=[
                        'components',
                    ],
                ),
            ),
        ),
    )
    host = SubSection(
        section_def=PolyCrystal,
    )


m_package.__init_metainfo__()
