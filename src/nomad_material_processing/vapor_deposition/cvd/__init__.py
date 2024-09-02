from nomad.config.models.plugins import SchemaPackageEntryPoint


class CvdSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_material_processing.vapor_deposition.cvd.general import m_package

        return m_package


schema = CvdSchemaPackageEntryPoint(
    name='CVD Schema',
    description='Schema package for general CVD techniques.',
)
