from nomad.config.models.plugins import SchemaPackageEntryPoint
from pydantic import Field


class MySchemaPackageEntryPoint(SchemaPackageEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from nomad_synthesis_plugin.schema_packages.mypackage import m_package

        return m_package


mypackage = MySchemaPackageEntryPoint(
    name='MyPackage',
    description='Schema package defined using the new plugin mechanism.',
)


class CrystallizationPackageEntryPoint(SchemaPackageEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from nomad_synthesis_plugin.schema_packages.crystallization import m_package

        return m_package


crystallization = CrystallizationPackageEntryPoint(
    name='Crystallization',
    description='Schema package defined using the new plugin mechanism.',
)
