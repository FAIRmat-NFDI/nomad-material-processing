from nomad.config.models.plugins import SchemaPackageEntryPoint


class GasSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_material_processing.gas.general import m_package

        return m_package


schema = GasSchemaPackageEntryPoint(
    name='Gas Schema',
    description='Schema package containing classes for gases and gas mixtures.',
)
