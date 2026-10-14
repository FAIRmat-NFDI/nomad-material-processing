"""
Functional tests of the solution schema: what a user enters, and what the normalizers
derive from it. The expected values follow from the physical definitions, not from
the implementation.
"""

import pytest
from nomad.client import normalize_all, parse
from nomad.datamodel.metainfo.basesections import PubChemPureSubstanceSection
from nomad.units import ureg

from nomad_material_processing.solution.general import (
    Solution,
    SolutionComponent,
    SolutionComponentReference,
)

WATER_CID = 962
SODIUM_CHLORIDE_CID = 5234


def normalized(data):
    """Normalizes `data` as the data section of an entry and returns it."""
    archive = parse('tests/data/test_solution.archive.yaml')[0]
    archive.data = data
    normalize_all(archive)
    return archive.data


def assert_quantity(actual, expected, rel=1e-9):
    assert actual is not None
    assert actual.to(expected.units).magnitude == pytest.approx(
        expected.magnitude, rel=rel
    )


def water(volume=0.5 * ureg('L')):
    return SolutionComponent(
        name='Water',
        component_role='Solvent',
        volume=volume,
        density=1.0 * ureg('g/mL'),
        pure_substance=PubChemPureSubstanceSection(name='Water'),
    )


def sodium_chloride(mass=10 * ureg('g')):
    return SolutionComponent(
        name='Sodium Chloride',
        component_role='Solute',
        mass=mass,
        pure_substance=PubChemPureSubstanceSection(name='Sodium Chloride'),
    )


@pytest.fixture
def salt_water():
    """10 g NaCl dissolved in 0.5 L of pipetted water."""
    return normalized(
        Solution(name='Salt water', components=[water(), sodium_chloride()])
    )


def portion(solution, volume, extra_components=()):
    return normalized(
        Solution(
            name='Portion',
            components=[
                SolutionComponentReference(system=solution, volume=volume),
                *extra_components,
            ],
        )
    )


# Components


def test_component_mass_from_volume_and_density():
    component = normalized(water(volume=0.5 * ureg('L')))
    assert_quantity(component.mass, 0.5 * ureg('kg'))


def test_component_substance_looked_up_by_name():
    component = normalized(
        SolutionComponent(substance_name='Water', volume=1 * ureg('mL'))
    )
    assert component.pure_substance.pub_chem_cid == WATER_CID


@pytest.mark.xfail(
    strict=True,
    reason='Uses the monoisotopic mass instead of the molar mass;',
)
@pytest.mark.parametrize('given', ['mass', 'amount_of_substance'])
def test_component_mass_and_amount_related_by_molar_mass(given):
    mass = 10 * ureg('g')
    amount = mass / (58.44 * ureg('g/mol'))  # molar mass of NaCl
    component = normalized(
        SolutionComponent(
            component_role='Solute',
            pure_substance=PubChemPureSubstanceSection(name='Sodium Chloride'),
            **{given: mass if given == 'mass' else amount},
        )
    )
    assert_quantity(component.mass, mass)
    assert_quantity(component.amount_of_substance, amount)


# Solutions


def test_components_classified_by_role(salt_water):
    assert [c.pure_substance.pub_chem_cid for c in salt_water.solvents] == [WATER_CID]
    assert [c.pure_substance.pub_chem_cid for c in salt_water.solutes] == [
        SODIUM_CHLORIDE_CID
    ]


def test_solution_volume_is_sum_of_liquid_volumes():
    solution = normalized(
        Solution(
            components=[
                water(volume=0.3 * ureg('L')),
                water(volume=0.2 * ureg('L')),
                sodium_chloride(),
            ]
        )
    )
    assert_quantity(solution.calculated_volume, 0.5 * ureg('L'))


def test_solution_mass_and_density(salt_water):
    assert_quantity(salt_water.mass, 0.51 * ureg('kg'))
    assert_quantity(salt_water.density, 0.51 * ureg('kg') / (0.5 * ureg('L')))


def test_concentration_is_amount_per_solution_volume(salt_water):
    for component in salt_water.solvents + salt_water.solutes:
        assert_quantity(
            component.molar_concentration.calculated_concentration,
            component.amount_of_substance / (0.5 * ureg('L')),
        )


def test_measured_volume_is_used_as_solution_volume():
    solution = normalized(
        Solution(
            components=[water(), sodium_chloride()],
            measured_volume=0.6 * ureg('L'),
        )
    )
    salt = solution.solutes[0]
    assert_quantity(
        salt.molar_concentration.calculated_concentration,
        salt.amount_of_substance / (0.6 * ureg('L')),
    )
    assert_quantity(solution.density, 0.51 * ureg('kg') / (0.6 * ureg('L')))


def test_components_of_same_substance_are_merged():
    first, second = water(volume=0.3 * ureg('L')), water(volume=0.2 * ureg('L'))
    solution = normalized(Solution(components=[first, second, sodium_chloride()]))

    assert len(solution.solvents) == 1
    merged = solution.solvents[0]
    assert_quantity(merged.volume, 0.5 * ureg('L'))
    assert_quantity(merged.mass, 0.5 * ureg('kg'))
    assert_quantity(
        merged.amount_of_substance,
        first.amount_of_substance + second.amount_of_substance,
    )


# Solutions made from other solutions


def test_portion_of_solution(salt_water):
    starter_values = [
        (c.mass, c.amount_of_substance, c.molar_concentration.calculated_concentration)
        for c in salt_water.solvents + salt_water.solutes
    ]

    result = portion(salt_water, 0.1 * ureg('L'))

    assert_quantity(result.components[0].mass, salt_water.density * 0.1 * ureg('L'))
    for component, (mass, amount, concentration) in zip(
        result.solvents + result.solutes, starter_values
    ):
        assert_quantity(component.mass, mass / 5)
        assert_quantity(component.amount_of_substance, amount / 5)
        assert_quantity(
            component.molar_concentration.calculated_concentration, concentration
        )
    # The starter solution is not changed.
    for component, (mass, amount, concentration) in zip(
        salt_water.solvents + salt_water.solutes, starter_values
    ):
        assert_quantity(component.mass, mass)
        assert_quantity(component.amount_of_substance, amount)
        assert_quantity(
            component.molar_concentration.calculated_concentration, concentration
        )


def test_whole_solution_used_if_no_volume_given(salt_water):
    result = portion(salt_water, None)

    assert_quantity(result.components[0].volume, 0.5 * ureg('L'))
    assert_quantity(result.solutes[0].mass, 10 * ureg('g'))


def test_dilution(salt_water):
    starter_salt = salt_water.solutes[0].molar_concentration.calculated_concentration

    result = portion(
        salt_water, 0.1 * ureg('L'), extra_components=[water(volume=0.1 * ureg('L'))]
    )

    assert len(result.solvents) == 1
    assert_quantity(result.calculated_volume, 0.2 * ureg('L'))
    assert_quantity(
        result.solutes[0].molar_concentration.calculated_concentration,
        starter_salt / 2,
    )
