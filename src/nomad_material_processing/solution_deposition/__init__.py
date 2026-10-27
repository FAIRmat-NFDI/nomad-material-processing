from nomad.config.models.plugins import SchemaPackageEntryPoint


class SolutionDepositionSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_material_processing.solution_deposition.general import m_package

        return m_package


schema = SolutionDepositionSchemaPackageEntryPoint(
    name='Solution Deposition Schema',
    description='Base sections for deposition from liquid solutions.',
)
