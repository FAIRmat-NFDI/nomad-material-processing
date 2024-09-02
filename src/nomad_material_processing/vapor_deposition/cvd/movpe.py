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
from typing import (
    TYPE_CHECKING,
)

from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
)
from nomad.datamodel.metainfo.basesections import (
    PubChemPureSubstanceSection,
    PureSubstanceComponent,
)
from nomad.metainfo import (
    Quantity,
    SchemaPackage,
    Section,
    SubSection,
)

from nomad_material_processing.general import (
    TimeSeries,
)
from nomad_material_processing.vapor_deposition.general import (
    EvaporationSource,
    GasFlow,
    MolarFlowRate,
    Pressure,
    Temperature,
    VaporDepositionSource,
    VolumetricFlowRate,
)

if TYPE_CHECKING:
    pass

from nomad.config import config

m_package = SchemaPackage()

configuration = config.get_plugin_entry_point(
    'nomad_material_processing.vapor_deposition.cvd:movpe_schema',
)


m_package.__init_metainfo__()
