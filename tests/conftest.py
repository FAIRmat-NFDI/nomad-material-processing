import pytest
from nomad.config import config
from nomad.config.models.plugins import SchemaPackageEntryPoint


@pytest.fixture(scope='session', autouse=True)
def import_schema_packages():
    config.load_plugins()
    for entry_point in config.plugins.entry_points.filtered_values():
        if isinstance(entry_point, SchemaPackageEntryPoint):
            entry_point.load()
