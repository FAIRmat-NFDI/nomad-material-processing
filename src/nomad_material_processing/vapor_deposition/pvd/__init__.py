#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from nomad.config.models.plugins import SchemaPackageEntryPoint


class GeneralPvdSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_material_processing.vapor_deposition.pvd.general import m_package

        return m_package


schema = GeneralPvdSchemaPackageEntryPoint(
    name='General PVD Schema',
    description="""Schema package containing basic classes used
    in the vapor_deposition submodule.""",
)


class MbeSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_material_processing.vapor_deposition.pvd.mbe import m_package

        return m_package


mbe_schema = MbeSchemaPackageEntryPoint(
    name='Mbe Schema',
    description="""Schema package containing basic classes used
    in the MBE submodule.""",
)


class PldSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_material_processing.vapor_deposition.pvd.pld import m_package

        return m_package


pld_schema = PldSchemaPackageEntryPoint(
    name='Pld Schema',
    description="""Schema package containing basic classes used
    in the PLD submodule.""",
)


class SputteringSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_material_processing.vapor_deposition.pvd.sputtering import m_package

        return m_package


sputtering_schema = SputteringSchemaPackageEntryPoint(
    name='Sputtering Schema',
    description="""Schema package containing basic classes used
    in the sputtering submodule.""",
)


class ThermalSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_material_processing.vapor_deposition.pvd.thermal import m_package

        return m_package


thermal_schema = ThermalSchemaPackageEntryPoint(
    name='Thermal Schema',
    description="""Schema package containing basic classes used
    in the thermal submodule.""",
)
