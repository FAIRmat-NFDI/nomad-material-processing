import itertools
import json
import os

import pytest
from nomad.datamodel.metainfo.basesections import PubChemPureSubstanceSection

# Recorded responses of `PubChemPureSubstanceSection.normalize`, keyed by the
# substance name used in the tests. To add a substance, normalize a section with
# that name once while online and add its `m_to_dict()` (without `name` and
# `cas_number`).
PUBCHEM_RECORDS_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'data', 'pubchem_offline.json'
)


def _load_records() -> tuple[dict, dict]:
    with open(PUBCHEM_RECORDS_PATH) as file:
        by_name = {name.lower(): record for name, record in json.load(file).items()}
    by_cid = {record['pub_chem_cid']: record for record in by_name.values()}
    return by_name, by_cid


@pytest.fixture(autouse=True)
def offline_pubchem(monkeypatch):
    """
    Replaces the PubChem lookup with the recorded responses, so the solution tests
    run offline and give the same result on every run. A substance without a
    record fails the test, even if the normalizer catches the error.
    """
    by_name, by_cid = _load_records()
    missing = []

    def normalize(self, archive, logger):
        if self.pub_chem_cid is not None:
            record = by_cid.get(self.pub_chem_cid)
        else:
            record = by_name.get((self.name or '').lower())
        if record is None:
            message = (
                f'No recorded PubChem data for name={self.name!r}, '
                f'cid={self.pub_chem_cid!r}. Add it to {PUBCHEM_RECORDS_PATH}.'
            )
            missing.append(message)
            raise LookupError(message)
        # Like the live lookup: only fill properties that are not set yet.
        for key, value in record.items():
            if getattr(self, key, None) is None:
                setattr(self, key, value)
        super(PubChemPureSubstanceSection, self).normalize(archive, logger)

    monkeypatch.setattr(PubChemPureSubstanceSection, 'normalize', normalize)
    yield
    if missing:
        pytest.fail('\n'.join(missing))


def input_combinations(inputs: dict) -> list:
    """
    Every way of filling a schema with some of `inputs`: no input, each input alone,
    each pair, and so on up to all of them (2 ** len(inputs) cases). For checking
    that a normalizer handles every combination of entered values:

        @pytest.mark.parametrize('given', input_combinations(INPUTS))
        def test_component(given):
            component = SolutionComponent(**given)

    Each case is a dict of the chosen inputs, named after them (e.g. `mass+volume`,
    or `nothing`), so a failing case shows which inputs were given.
    """
    cases = []
    for size in range(len(inputs) + 1):  # how many of the inputs are given
        for combination in itertools.combinations(inputs.items(), size):
            given = dict(combination)
            cases.append(pytest.param(given, id='+'.join(given) or 'nothing'))
    return cases
