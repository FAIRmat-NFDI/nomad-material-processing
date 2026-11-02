import pytest
from nomad.client import normalize_all, parse
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.basesections import PubChemPureSubstanceSection
from nomad.metainfo import SubSection
from nomad.units import ureg
from structlog.testing import capture_logs

from nomad_material_processing.gas.general import Gas, GasComponent


class GasUsingEntry(EntryData):
    atmosphere = SubSection(section_def=Gas)


def normalize_atmosphere(gas):
    archive = parse('tests/data/test_solution.archive.yaml')[0]
    archive.data = GasUsingEntry(atmosphere=gas)
    with capture_logs() as logs:
        normalize_all(archive)
    return archive, logs


def gas_component(formula, mole_fraction=None):
    return GasComponent(
        pure_substance=PubChemPureSubstanceSection(molecular_formula=formula),
        mole_fraction=mole_fraction,
    )


def mole_fractions(gas):
    return {
        component.pure_substance.molecular_formula: component.mole_fraction.magnitude
        for component in gas.components
    }


def sum_warnings(logs, gas_name):
    return [
        log
        for log in logs
        if log['log_level'] == 'warning' and gas_name in log['event']
    ]


def test_balance_component_completes_the_gas():
    archive, _ = normalize_atmosphere(
        Gas(
            name='Nitrogen',
            components=[
                gas_component('N2'),
                gas_component('O2', 1 * ureg('ppm')),
                gas_component('H2O', 0.5 * ureg('ppm')),
            ],
        )
    )

    assert mole_fractions(archive.data.atmosphere) == pytest.approx(
        {'N2': 1 - 1.5e-6, 'O2': 1e-6, 'H2O': 0.5e-6}
    )
    # The gas surrounds the entry's sample; it is not the entry's material.
    assert archive.results.material is None


def test_mole_fractions_not_summing_to_one_are_reported():
    _, logs = normalize_atmosphere(
        Gas(
            name='Incomplete gas',
            components=[
                gas_component('H2', 5 * ureg('percent')),
                gas_component('N2', 90 * ureg('percent')),
            ],
        )
    )

    assert sum_warnings(logs, 'Incomplete gas')


def test_balance_is_not_filled_when_the_other_components_exceed_one():
    archive, logs = normalize_atmosphere(
        Gas(
            name='Overfull gas',
            components=[
                gas_component('N2'),
                gas_component('H2', 20 * ureg('percent')),
                gas_component('Ar', 90 * ureg('percent')),
            ],
        )
    )

    assert archive.data.atmosphere.components[0].mole_fraction is None
    assert sum_warnings(logs, 'Overfull gas')
