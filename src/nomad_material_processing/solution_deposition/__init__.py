from nomad.config.models.plugins import SchemaPackageEntryPoint


class SolutionDepositionSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_material_processing.solution_deposition.general import m_package

        return m_package


class FlowGeometrySchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_material_processing.solution_deposition.flow_geometry import (
            m_package,
        )

        return m_package


schema = SolutionDepositionSchemaPackageEntryPoint(
    name='Solution Deposition Schema',
    description='Base sections for deposition from liquid solutions.',
)

flow_geometry_schema = FlowGeometrySchemaPackageEntryPoint(
    name='Solution Deposition Flow Geometry Schema',
    description='Mixins describing how a fluid flows onto a film.',
)
