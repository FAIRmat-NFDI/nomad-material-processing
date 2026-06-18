from nomad.config.models.plugins import SchemaPackageEntryPoint


class MaterialSystemsSchemaEntryPoint(SchemaPackageEntryPoint):
    """
    Entry point for lazy loading of the Material Systems schemas.
    """

    def load(self):
        from nomad_material_processing.material_systems.general import m_package

        return m_package


schema = MaterialSystemsSchemaEntryPoint(
    name='Material System Schema',
    description='Schema for material systems.',
)
