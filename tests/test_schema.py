import glob
import os.path
import sys

from nomad.client import normalize_all, parse


def test_schema():
    test_files = glob.glob(
        os.path.join(os.path.dirname(__file__), 'data', '*.archive.yaml')
    )
    for test_file in test_files:
        sys.stdout.write(f'Test file: {test_file}')
        entry_archive = parse(test_file)[0]
        normalize_all(entry_archive)
