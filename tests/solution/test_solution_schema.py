import pytest
from nomad.client import normalize_all, parse
from nomad.datamodel.metainfo.basesections import PubChemPureSubstanceSection
from nomad.units import ureg

from nomad_material_processing.solution.general import (
    Solution,
    SolutionComponent,
    SolutionComponentReference,
)


def test_solution_component():
    """
    Test molar concentration calculation for a solution component.
    Test mass calculation.
    """
    archive = parse('tests/data/test_solution_component.archive.yaml')[0]
    archive.data = SolutionComponent(
        volume=1.0 * ureg('l'),
        density=1.0 * ureg('kg/l'),
        pure_substance=PubChemPureSubstanceSection(
            name='Water',
        ),
    )
    normalize_all(archive)

    volume = 1 * ureg('liter')
    archive.data.calculate_molar_concentration(volume)

    assert pytest.approx(archive.data.mass, 1e-3) == 1.0 * ureg('kg')
    assert pytest.approx(
        archive.data.molar_concentration.calculated_concentration, 1e-3
    ) == 55.523 * ureg('mol/l')


def test_solution():
    starter_solution_archive = parse('tests/data/test_solution.archive.yaml')[0]
    water = PubChemPureSubstanceSection(name='Water')
    salt = PubChemPureSubstanceSection(name='Sodium Chloride')
    starter_solution = Solution(
        name='Starter solution',
        components=[
            SolutionComponent(
                volume=0.50 * ureg('l'),
                density=1.0 * ureg('kg/l'),
                pure_substance=water,
            ),
            SolutionComponent(
                mass=0.01 * ureg('kg'),
                pure_substance=salt,
                component_role='Solute',
            ),
        ],
    )
    starter_solution_archive.data = starter_solution
    normalize_all(starter_solution_archive)
    starter_water_concentration = starter_solution_archive.data.solvents[
        0
    ].molar_concentration.calculated_concentration
    starter_salt_concentration = starter_solution_archive.data.solutes[
        0
    ].molar_concentration.calculated_concentration
    starter_salt_mass = starter_solution_archive.data.solutes[0].mass

    assert pytest.approx(starter_water_concentration, 1e-3) == 55.523 * ureg('mol/l')
    assert pytest.approx(starter_salt_concentration, 1e-3) == 0.345 * ureg('mol/l')
    assert pytest.approx(starter_salt_mass, 1e-3) == 0.01 * ureg('kg')

    ## making the main solution using starter solution
    main_solution_archive = parse('tests/data/test_solution.archive.yaml')[0]

    # step 1: portioning the starter solution (one fifth)
    main_solution_archive.data = Solution(
        name='Diluted Solution',
        components=[
            SolutionComponentReference(
                system=starter_solution,
                volume=0.1 * ureg('l'),
            ),
        ],
    )
    normalize_all(main_solution_archive)
    assert (
        pytest.approx(
            main_solution_archive.data.solvents[
                0
            ].molar_concentration.calculated_concentration,
            1e-3,
        )
        == starter_water_concentration
    )
    assert (
        pytest.approx(
            main_solution_archive.data.solutes[
                0
            ].molar_concentration.calculated_concentration,
            1e-3,
        )
        == starter_salt_concentration
    )
    assert (
        pytest.approx(main_solution_archive.data.solutes[0].mass, 1e-3)
        == starter_salt_mass / 5
    )

    # step 2: diluting the solution (double the volume of water)
    main_solution_archive.data = Solution(
        name='Diluted Solution',
        components=[
            SolutionComponentReference(
                system=starter_solution,
                volume=0.1 * ureg('l'),
            ),
            SolutionComponent(
                volume=0.1 * ureg('l'),
                density=1.0 * ureg('kg/l'),
                pure_substance=water,
            ),
        ],
    )
    normalize_all(main_solution_archive)
    assert (
        pytest.approx(
            main_solution_archive.data.solvents[
                0
            ].molar_concentration.calculated_concentration,
            1e-3,
        )
        == starter_water_concentration
    )
    assert (
        pytest.approx(
            main_solution_archive.data.solutes[
                0
            ].molar_concentration.calculated_concentration,
            1e-3,
        )
        == starter_salt_concentration / 2
    )
    assert (
        pytest.approx(main_solution_archive.data.solutes[0].mass, 1e-3)
        == starter_salt_mass / 5
    )

    # finally, quantities in the starter solution should stay the same
    # after all normalizations
    assert (
        pytest.approx(
            starter_solution_archive.data.solvents[
                0
            ].molar_concentration.calculated_concentration,
            1e-3,
        )
        == starter_water_concentration
    )
    assert (
        pytest.approx(
            starter_solution_archive.data.solutes[
                0
            ].molar_concentration.calculated_concentration,
            1e-3,
        )
        == starter_salt_concentration
    )
    assert (
        pytest.approx(starter_solution_archive.data.solutes[0].mass, 1e-3)
        == starter_salt_mass
    )


if __name__ == '__main__':
    test_solution()
