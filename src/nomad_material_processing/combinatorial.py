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

import plotly.graph_objects as go
from nomad.datamodel.data import (
    ArchiveSection,
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
)
from nomad.datamodel.metainfo.basesections import (
    Collection,
    CompositeSystem,
    CompositeSystemReference,
    Measurement,
)
from nomad.datamodel.metainfo.plot import (
    PlotlyFigure,
    PlotSection,
)
from nomad.metainfo import (
    Package,
    Quantity,
    Reference,
    Section,
    SubSection, SectionProxy
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name='Combinatorial Synthesis')


class CombinatorialLibrary(CompositeSystem, EntryData, PlotSection):
    """
    A base section for any continuous combinatorial library.
    """

    m_def = Section()

    def plot(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        from nomad.search import (
            MetadataPagination,
            search,
        )

        query = {
            'section_defs.definition_qualified_name:all': [
                'nomad_material_processing.combinatorial.CombinatorialSample'
            ],
            'entry_references.target_entry_id:all': [archive.metadata.entry_id],
        }
        search_result = search(
            owner='all',
            query=query,
            pagination=MetadataPagination(page_size=1),
            user_id=archive.metadata.main_author.user_id,
        )
        references = []
        x_values = []
        y_values = []
        z_values = []
        if search_result.pagination.total > 0:
            for res in search_result.data:
                entry_id = res['entry_id']
                upload_id = res['upload_id']
                reference = f'../../../{upload_id}/entry/id/{entry_id}'
                x, y, z = None, None, None
                for quantity in res['search_quantities']:
                    if quantity['path_archive'] == 'data.position.x':
                        x = quantity['float_value']
                    if quantity['path_archive'] == 'data.position.y':
                        y = quantity['float_value']
                    if quantity['path_archive'] == 'data.position.z':
                        z = quantity['float_value']
                references.append(reference)
                x_values.append(x)
                y_values.append(y)
                z_values.append(z)
            print(f'Found {search_result.pagination.total} activities.')
        fig = go.Figure(
            data=go.Scatter(
                x=x_values,
                y=y_values,
                mode='markers',
                customdata=references,
                marker=dict(color='#2A4CDF'),
                hovertemplate='<a href="%{customdata}">Link</a><extra></extra>',
            )
        )

        # Set plot title and axis labels
        fig.update_layout(
            template='plotly_white',
            hovermode='closest',
            dragmode='zoom',
            title='Scatter Plot of x and y Coordinates',
            xaxis_title='x / m',
            yaxis_title='y / m',
        )
        plot_json = fig.to_plotly_json()
        plot_json['config'] = dict(
            scrollZoom=False,
        )
        self.figures.append(
            PlotlyFigure(
                label='Power, pressure, and temperature',
                figure=plot_json,
            )
        )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `ContinuousCombiLibrary` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)
        self.figures = []
        self.plot(archive, logger)


class CombinatorialSamplePosition(ArchiveSection):
    """
    A section for representing the position of a sample within a continuous
    combinatorial library.
    If nothing else is specified it is the position relative to the center of mass of
    the library.
    """

    m_def = Section()
    x = Quantity(
        type=float,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='mm',
        ),
        unit='m',
    )
    y = Quantity(
        type=float,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='mm',
        ),
        unit='m',
    )
    z = Quantity(
        type=float,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='mm',
        ),
        unit='m',
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `CombinatorialSamplePosition` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)


class CombinatorialLibraryReference(CompositeSystemReference):
    """
    A section containing a reference to a continuous combinatorial library entry.
    """

    m_def = Section(
        label_quantity='lab_id',
    )
    reference = Quantity(
        type=CombinatorialLibrary,
        description="""
        The reference to the combinatorial library entry.
        """,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
            label='Library Reference',
        ),
    )


class CombinatorialSample(CompositeSystem, EntryData):
    """
    A base section for any sample of a continuous combinatorial library.
    """

    m_def = Section()
    sample_number = Quantity(
        type=int,
        description="""
        A unique number for this sample of the combinatorial library.
        """,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
        ),
    )
    lab_id = Quantity(
        type=str,
        description="""
        A unique human readable ID for the sample within the combinatorial library.
        Suggested to be the ID of the library followed by a dash ("-") and the sample
        number.
        """,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            label='Sample ID',
        ),
    )
    library = SubSection(
        section_def=CombinatorialLibraryReference,
        description="""
        The reference to the combinatorial library entry.
        """,
    )
    position = SubSection(
        section_def=CombinatorialSamplePosition,
        description="""
        The position of a sample within the continuous combinatorial library. If nothing
        else is specified it is the position relative to the center of mass of the
        library.
        """,
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `CombinatorialSample` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)


# Discrete combinatorial library classes:
class DiscreteCombinatorialSample(CompositeSystem):
    """
    A base section for any sample of a discrete combinatorial library.
    """

    m_def = Section()

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `CombinatorialSample` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)


class DiscreteCombinatorialSampleReference(CompositeSystemReference):
    """
    A section containing a reference to a discrete combinatorial sample entry.
    """

    m_def = Section(
        label_quantity='sample_number',
    )
    sample_number = Quantity(
        type=int,
        description="""
        A unique number for this sample of the combinatorial library.
        """,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
        ),
    )
    reference = Quantity(
        type=DiscreteCombinatorialSample,
        description="""
        The reference to the combinatorial sample entry.
        """,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
            label='Sample Reference',
        ),
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `CombinatorialSampleReference` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)


class DiscreteCombinatorialLibrary(Collection):
    """
    A base section for a discrete combinatorial library.
    """

    m_def = Section()
    lab_id = Quantity(
        type=str,
        description="""
        A unique human readable ID for the combinatorial library.
        """,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity, label='Library ID'
        ),
    )
    entities = SubSection(
        section_def=DiscreteCombinatorialSampleReference,
        description="""
        All the investigated samples of the combinatorial library.
        """,
        repeats=True,
        a_eln=ELNAnnotation(label='Samples'),
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `DiscreteCombinatorialLibrary` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)


class CombinatorialProperty(ArchiveSection):
    model = Quantity(
        type=str,
        description="""
        The model/calculation method used to calculate the property.
        """,
    )

    analysis = Quantity(
        type=str,
        description="""
        The model used to calculate the property.
        """,
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    measurements = Quantity(
        type=Reference(Measurement.m_def),
        description="""
        List of measurements used to determine the property.
        """,
        shape=['*'],
    )


class Formula(CombinatorialProperty):
    value = Quantity(
        type=str,
        description="""
        The molecular formula of the sample.
        """,
    )


class Thickness(CombinatorialProperty):
    value = Quantity(
        type=float,
        description="""
        The (average) thickness of the sample.
        """,
        unit='m',
    )


class Conductivity(CombinatorialProperty):
    value = Quantity(
        type=float,
        description="""
        The conductivity of the sample.
        """,
        unit='S/m',
    )


class CarrierLifetime(CombinatorialProperty):
    value = Quantity(
        type=float,
        description="""
        The lifetime of the (majority) carriers in the sample.
        """,
        unit='s',
    )


class BandGap(CombinatorialProperty):
    value = Quantity(
        type=float,
        description="""
        The band gap of the sample.
        """,
        unit='eV',
    )


class Synthesis(CombinatorialProperty):
    method = Quantity(
        type=str,
        description="""
        The method used to synthesize the material.
        """,
    )
    temperature = Quantity(
        type=float,
        description="""
        The (maximum) temperature at which the material was synthesized.
        """,
        unit='K',
    )
    pressure = Quantity(
        type=float,
        description="""
        The (average) pressure at which the material was synthesized.
        """,
        unit='Pa',
    )
    atmosphere = Quantity(
        type=str,
        description="""
        The atmosphere in which the material was synthesized.
        """,
    )


class PLPeakPostion(CombinatorialProperty):
    value = Quantity(
        type=float,
        description="""
      The peak position of the photoluminescence spectrum.
      """,
        unit='nm',
    )


class PLFWHM(CombinatorialProperty):
    value = Quantity(
        type=float,
        description="""
      The full width at half maximum of the photoluminescence spectrum.
      """,
        unit='nm',
    )


class PLPeakArea(CombinatorialProperty):
    value = Quantity(
        type=float,
        description="""
      The peak area of the photoluminescence spectrum.
      """,
    )


class PLAbsorbedPowerFlux(CombinatorialProperty):
    value = Quantity(
        type=float,
        description="""
      The (assumed) absorbed power flux of the sample during the photoluminescence
      measurement.
      """,
        unit='W/m^2',
    )


class PLExcitationWavelength(CombinatorialProperty):
    value = Quantity(
        type=float,
        description="""
      The (peak) wavelength of the excitation source used during the photoluminescence
      measurement.
      """,
        unit='nm',
    )


class PLQY(CombinatorialProperty):
    value = Quantity(
        type=float,
        description="""
        The photoluminescence quantum yield of the sample.
        """,
    )


class Photoluminescence(ArchiveSection):
    peak_position = SubSection(section_def=PLPeakPostion)
    fwhm = SubSection(section_def=PLFWHM)
    peak_area = SubSection(section_def=PLPeakArea)
    absorber_power_flux = SubSection(section_def=PLAbsorbedPowerFlux)
    excitation_wavelength = SubSection(section_def=PLExcitationWavelength)
    plqy = SubSection(section_def=PLQY)


class XRayDiffraction(CombinatorialProperty):
    def derive_n_values(self):
        if self.intensity is not None:
            return len(self.intensity)
        if self.scattering_vector is not None:
            return len(self.scattering_vector)
        else:
            return 0

    n_values = Quantity(type=int, derived=derive_n_values)

    intensity = Quantity(
        type=float,
        description="""
        The intensity of the X-ray diffraction pattern.
        """,
        shape=['n_values'],
    )
    scattering_vector = Quantity(
        type=float,
        description="""
        The corresponding scattering vector values of the measured X-ray diffraction
        pattern.
        """,
        shape=['n_values'],
        unit='1/nm',
    )


class ComplexRefractiveIndex(CombinatorialProperty):
    def derive_n_values(self):
        if self.n is not None:
            return len(self.n)
        if self.k is not None:
            return len(self.k)
        if self.photon_wavelength is not None:
            return len(self.photon_wavelength)
        else:
            return 0

    n_values = Quantity(type=int, derived=derive_n_values)

    n = Quantity(
        type=float,
        description="""
        The (real part of the) refractive index of the sample.
        """,
        shape=['n_values'],
    )
    k = Quantity(
        type=float,
        description="""
        The attenuation coefficient of the sample.
        """,
        shape=['n_values'],
    )
    photon_wavelength = Quantity(
        type=float,
        description="""
        The wavelength of the photons used to measure the complex refractive index.
        """,
        unit='nm',
        shape=['n_values'],
    )


class PhotovoltaicEfficiency(CombinatorialProperty):
    value = Quantity(
        type=float,
        description="""
        The (theoretical) efficiency of the sample as a solar cell under AM1.5G.
        """,
    )


class PhotovoltaicShortCircuitCurrentDensity(CombinatorialProperty):
    value = Quantity(
        type=float,
        description="""
        The (theoretical) short circuit current of the sample as a solar cell under
        AM1.5G.
        """,
        unit='A/m^2',
    )


class PhotovoltaicOpenCircuitVoltage(CombinatorialProperty):
    value = Quantity(
        type=float,
        description="""
        The (theoretical) open circuit voltage of the sample as a solar cell under
        AM1.5G.
        """,
        unit='V',
    )


class PhotovoltaicFillFactor(CombinatorialProperty):
    value = Quantity(
        type=float,
        description="""
       The (theoretical) fill factor of the sample as a solar cell under
       AM1.5G.
       """,
    )


class Photovoltaic(ArchiveSection):
    efficiency = SubSection(section_def=PhotovoltaicEfficiency)
    jsc = SubSection(section_def=PhotovoltaicShortCircuitCurrentDensity)
    voc = SubSection(section_def=PhotovoltaicOpenCircuitVoltage)
    ff = SubSection(section_def=PhotovoltaicFillFactor)


class ThinFilmCombinatorialSample(CombinatorialSample):
    formula = SubSection(section_def=Formula)
    thickness = SubSection(section_def=Thickness)
    conductivity = SubSection(section_def=Conductivity)
    carrier_lifetime = SubSection(section_def=CarrierLifetime)
    band_gap = SubSection(section_def=BandGap)
    synthesis = SubSection(section_def=Synthesis)
    photoluminescence = SubSection(section_def=Photoluminescence)
    xray_diffraction = SubSection(section_def=XRayDiffraction)
    complex_refractive_index = SubSection(section_def=ComplexRefractiveIndex)
    photovoltaic = SubSection(section_def=Photovoltaic)


m_package.__init_metainfo__()
