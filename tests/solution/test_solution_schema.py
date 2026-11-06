import pytest
from nomad.client import normalize_all, parse
from nomad.datamodel.metainfo.basesections import (
    PubChemPureSubstanceSection,
    PureSubstanceSection,
)
from nomad.units import ureg

from nomad_material_processing.solution.general import (
    Solution,
    SolutionComponent,
    SolutionComponentReference,
)


@pytest.fixture(autouse=True)
def mock_pubchem(monkeypatch):
    """Use fixed enrichment data without querying PubChem."""
    substances = {
        'Water': (962, 'H2O', 18.010564684),
        'Sodium Chloride': (5234, 'ClNa', 57.95862196),
    }

    def normalize_pubchem(section, archive, logger):
        if section.name not in substances:
            pytest.fail(f'No mocked PubChem data for {section.name!r}.')
        cid, formula, molecular_mass = substances[section.name]
        section.pub_chem_cid = cid
        section.molecular_formula = formula
        section.molecular_mass = molecular_mass * ureg('Da')

        # Run the parent normalization as
        # PubChemPureSubstanceSection inherits from PureSubstanceSection
        PureSubstanceSection.normalize(section, archive, logger)

    monkeypatch.setattr(PubChemPureSubstanceSection, 'normalize', normalize_pubchem)


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

    assert archive.data.mass.to('kg').magnitude == pytest.approx(1.0, rel=1e-3)
    assert archive.data.molar_concentration.calculated_concentration.to(
        'mol/l'
    ).magnitude == pytest.approx(55.523, rel=1e-3)


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
    starter_water_amount = starter_solution_archive.data.solvents[0].amount_of_substance
    starter_salt_concentration = starter_solution_archive.data.solutes[
        0
    ].molar_concentration.calculated_concentration
    starter_salt_mass = starter_solution_archive.data.solutes[0].mass

    assert starter_water_concentration.to('mol/l').magnitude == pytest.approx(
        55.523, rel=1e-3
    )
    assert starter_water_amount.to('mol').magnitude == pytest.approx(
        0.5 * 55.523, rel=1e-3
    )
    assert starter_salt_concentration.to('mol/l').magnitude == pytest.approx(
        0.345, rel=1e-3
    )
    assert starter_salt_mass.to('kg').magnitude == pytest.approx(0.01, rel=1e-3)

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
    assert main_solution_archive.data.solvents[
        0
    ].molar_concentration.calculated_concentration.to(
        'mol/l'
    ).magnitude == pytest.approx(
        starter_water_concentration.to('mol/l').magnitude, rel=1e-3
    )
    assert main_solution_archive.data.solvents[0].amount_of_substance.to(
        'mol'
    ).magnitude == pytest.approx(starter_water_amount.to('mol').magnitude / 5, rel=1e-3)
    assert main_solution_archive.data.solutes[
        0
    ].molar_concentration.calculated_concentration.to(
        'mol/l'
    ).magnitude == pytest.approx(
        starter_salt_concentration.to('mol/l').magnitude, rel=1e-3
    )
    assert main_solution_archive.data.solutes[0].mass.to(
        'kg'
    ).magnitude == pytest.approx(starter_salt_mass.to('kg').magnitude / 5, rel=1e-3)

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
    assert main_solution_archive.data.solvents[
        0
    ].molar_concentration.calculated_concentration.to(
        'mol/l'
    ).magnitude == pytest.approx(
        starter_water_concentration.to('mol/l').magnitude, rel=1e-3
    )
    assert main_solution_archive.data.solvents[0].amount_of_substance.to(
        'mol'
    ).magnitude == pytest.approx(
        (starter_water_amount.to('mol').magnitude / 5) * 2, rel=1e-3
    )
    assert main_solution_archive.data.solutes[
        0
    ].molar_concentration.calculated_concentration.to(
        'mol/l'
    ).magnitude == pytest.approx(
        starter_salt_concentration.to('mol/l').magnitude / 2, rel=1e-3
    )
    assert main_solution_archive.data.solutes[0].mass.to(
        'kg'
    ).magnitude == pytest.approx(starter_salt_mass.to('kg').magnitude / 5, rel=1e-3)

    # finally, quantities in the starter solution should stay the same
    # after all normalizations
    assert starter_solution_archive.data.solvents[
        0
    ].molar_concentration.calculated_concentration.to(
        'mol/l'
    ).magnitude == pytest.approx(
        starter_water_concentration.to('mol/l').magnitude, rel=1e-3
    )
    assert starter_solution_archive.data.solvents[0].amount_of_substance.to(
        'mol'
    ).magnitude == pytest.approx(starter_water_amount.to('mol').magnitude, rel=1e-3)
    assert starter_solution_archive.data.solutes[
        0
    ].molar_concentration.calculated_concentration.to(
        'mol/l'
    ).magnitude == pytest.approx(
        starter_salt_concentration.to('mol/l').magnitude, rel=1e-3
    )
    assert starter_solution_archive.data.solutes[0].mass.to(
        'kg'
    ).magnitude == pytest.approx(starter_salt_mass.to('kg').magnitude, rel=1e-3)


if __name__ == '__main__':
    test_solution()
