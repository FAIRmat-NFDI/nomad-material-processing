from nomad.config.models.plugins import SchemaPackageEntryPoint


class PrecipitationSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_material_processing.sample_solidification.precipitation import m_package

        return m_package


precipitation_schema = PrecipitationSchemaPackageEntryPoint(
    name='Precipitation Schema',
    description="""Schema package containing classes for sample synthesis from
    liquid solutions.""",
)
