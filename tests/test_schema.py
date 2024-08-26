import glob
import os.path

import pytest
from nomad.client import normalize_all, parse

test_files = glob.glob(
    os.path.join(os.path.dirname(__file__), 'data', '*.archive.yaml')
)


@pytest.mark.parametrize('test_file', test_files)
def test_schema(test_file):
    entry_archive = parse(test_file)[0]
    normalize_all(entry_archive)
