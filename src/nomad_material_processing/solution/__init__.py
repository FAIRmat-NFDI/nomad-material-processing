from nomad.config.models.plugins import SchemaPackageEntryPoint


class SolutionSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_material_processing.solution.general import m_package

        return m_package


schema = SolutionSchemaPackageEntryPoint(
    name='Solution Schema',
    description='Schema package containing classes for liquid solutions.',
)
