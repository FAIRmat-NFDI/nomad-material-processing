from nomad.client import parse, normalize_all
from nomad.units import ureg
from nomad.datamodel.metainfo.basesections import PubChemPureSubstanceSection

from nomad_material_processing.solution import (
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
        volume=1000 * ureg('ml'),
        density=1.0 * ureg('g/ml'),
        pure_substance=PubChemPureSubstanceSection(
            name='Water',
        ),
    )
    normalize_all(archive)

    volume = 1 * ureg('liter')
    archive.data.compute_molar_concentration(volume)

    assert round(archive.data.mass, 3) == 1.000 * ureg('kg')
    assert round(
        archive.data.molar_concentration.calculated_concentration, 3
    ) == 55.523 * ureg('mol/l')


def test_solution():
    starter_solution_archive = parse('tests/data/test_solution.archive.yaml')[0]
    water = PubChemPureSubstanceSection(name='Water')
    salt = PubChemPureSubstanceSection(name='Sodium Chloride')
    starter_solution = Solution(
        name='Starter solution',
        components=[
            SolutionComponent(
                volume=500 * ureg('ml'),
                density=1.0 * ureg('g/ml'),
                pure_substance=water,
            ),
            SolutionComponent(
                mass=10 * ureg('g'),
                pure_substance=salt,
                component_role='Solute',
            ),
        ],
    )
    starter_solution_archive.data = starter_solution
    normalize_all(starter_solution_archive)
    starter_water_concentration = round(
        starter_solution_archive.data.solvents[
            0
        ].molar_concentration.calculated_concentration,
        3,
    )
    starter_salt_concentration = round(
        starter_solution_archive.data.solutes[
            0
        ].molar_concentration.calculated_concentration,
        3,
    )
    starter_salt_mass = round(starter_solution_archive.data.solutes[0].mass, 3)
    assert round(starter_water_concentration, 3) == 55.523 * ureg('mol/l')
    assert round(starter_salt_concentration, 3) == 0.345 * ureg('mol/l')
    assert round(starter_salt_mass, 3) == 10.0 * ureg('g')

    ## making the main solution using starter solution
    main_solution_archive = parse('tests/data/test_solution.archive.yaml')[0]

    # step 1: portioning the starter solution (one fifth)
    main_solution_archive.data = Solution(
        name='Diluted Solution',
        components=[
            SolutionComponentReference(
                system=starter_solution,
                volume=100 * ureg('ml'),
            ),
        ],
    )
    normalize_all(main_solution_archive)
    assert (
        round(
            main_solution_archive.data.solvents[
                0
            ].molar_concentration.calculated_concentration,
            3,
        )
        == starter_water_concentration
    )
    assert (
        round(
            main_solution_archive.data.solutes[
                0
            ].molar_concentration.calculated_concentration,
            3,
        )
        == starter_salt_concentration
    )
    assert round(main_solution_archive.data.solutes[0].mass, 3) == starter_salt_mass / 5

    # step 2: diluting the solution (double the volume of water)
    main_solution_archive.data = Solution(
        name='Diluted Solution',
        components=[
            SolutionComponentReference(
                system=starter_solution,
                volume=100 * ureg('ml'),
            ),
            SolutionComponent(
                volume=100 * ureg('ml'),
                density=1.0 * ureg('g/ml'),
                pure_substance=water,
            ),
        ],
    )
    normalize_all(main_solution_archive)
    assert (
        round(
            main_solution_archive.data.solvents[
                0
            ].molar_concentration.calculated_concentration,
            3,
        )
        == starter_water_concentration
    )
    assert round(
        main_solution_archive.data.solutes[
            0
        ].molar_concentration.calculated_concentration,
        2,
    ) == round(starter_salt_concentration / 2, 2)
    assert round(main_solution_archive.data.solutes[0].mass, 3) == starter_salt_mass / 5

    # finally, quantities in the starter solution should stay the same
    # after all normalizations
    assert (
        round(
            starter_solution_archive.data.solvents[
                0
            ].molar_concentration.calculated_concentration,
            3,
        )
        == starter_water_concentration
    )
    assert (
        round(
            starter_solution_archive.data.solutes[
                0
            ].molar_concentration.calculated_concentration,
            3,
        )
        == starter_salt_concentration
    )
    assert round(starter_solution_archive.data.solutes[0].mass, 3) == starter_salt_mass


if __name__ == '__main__':
    test_solution()
