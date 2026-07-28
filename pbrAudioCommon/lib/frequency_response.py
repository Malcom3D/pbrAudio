# Copyright (C) 2025 Malcom3D <malcom3d.gpl@gmail.com>
#
# This file is part of pbrAudio.
#
# pbrAudio is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pbrAudio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pbrAudio.  If not, see <https://www.gnu.org/licenses/>.
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
import numpy as np

from ..lib.interpolator import Frequency3DInterpolator
from ..lib.functions import _degrees_to_radians

@dataclass
class SpatialFrequencyResponse:
    """Contains elevation frequency magnitude data for azimuths and elevations."""
    azimuths: List[float] #= field(default_factory=lambda: [0.]) # azimuth angle values array
    elevations: List[float] #= field(default_factory=lambda: [0.]) # elevation angle values array
    frequencies: List[float] #= field(default_factory=lambda: [0.]) # Frequency values array
    magnitude: List[List[List[float]]] #= field(default_factory=lambda: [[[0.]]]) # Corresponding magnitude values array
    phases: List[List[List[float]]] = field(default_factory=lambda: [[[0.]]]) # Corresponding phase values array

    def __post_init__(self):
        # Verify phase is in radians and convert to if need.
        self.phases = _degrees_to_radians(self.phases)

        # Create 3D interpolator
        self.magnitude_interpolator = Frequency3DInterpolator(azimuths=self.azimuths, elevations=self.elevations, frequency_data=self.frequencies, value_data=self.magnitude, freq_method='linear', spatial_method='linear', extrapolate=True)
        self.phases_interpolator = Frequency3DInterpolator(azimuths=self.azimuths, elevations=self.elevations, frequency_data=self.frequencies, value_data=self.phases, freq_method='linear', spatial_method='linear', extrapolate=True)

    def get_magnitude(self, azimuth: Optional[float] = None, elevation: Optional[float] = None, low_freq: Optional[float] = None, high_freq: Optional[float] = None, num_points: Optional[int] = 0) -> np.ndarray:
        """Retrieve data for specific azimuth and elevation."""
        azimuth = azimuth if azimuth else 0.
        elevation = elevation if elevation else 0.
        low_freq = low_freq if low_freq else self.frequencies[0]
        high_freq = high_freq if high_freq else self.frequencies[-1]
        num_points = num_points if not num_points == 0 else len(self.frequencies)
        frequencies, magnitude = self.magnitude_interpolator.interpolate_band_at_point(azimuth, elevation, low_freq, high_freq, num_points)
        return frequencies, magnitude

    def get_phases(self, azimuth: Optional[float] = None, elevation: Optional[float] = None, low_freq: Optional[float] = None, high_freq: Optional[float] = None, num_points: Optional[int] = 0) -> np.ndarray:
        """Retrieve data for specific azimuth and elevation."""
        azimuth = azimuth if azimuth else 0.
        elevation = elevation if elevation else 0.
        low_freq = low_freq if low_freq else self.frequencies[0]
        high_freq = high_freq if high_freq else self.frequencies[-1]
        num_points = num_points if not num_points == 0 else len(self.frequencies)
        frequencies, phases = self.phases_interpolator.interpolate_band_at_point(azimuth, elevation, low_freq, high_freq, num_points)
        return frequencies, phases

    def get_avg_magnitude(self, azimuth: Optional[float] = None, elevation: Optional[float] = None, low_freq: float = None, high_freq: float = None) -> float:
        """Retrieve value for a frequency band for specific azimuth and elevation."""
        azimuth = azimuth if azimuth else 0.
        elevation = elevation if elevation else 0.
        low_freq = low_freq if low_freq else self.frequencies[0]
        high_freq = high_freq if high_freq else self.frequencies[-1]
        return self.magnitude_interpolator.get_band_average_at_point(azimuth, elevation, low_freq, high_freq)

    def get_avg_phase(self, azimuth: Optional[float] = None, elevation: Optional[float] = None, low_freq: float = None, high_freq: float = None) -> float:
        """Retrieve value for a frequency band for specific azimuth and elevation."""
        azimuth = azimuth if azimuth else 0.
        elevation = elevation if elevation else 0.
        low_freq = low_freq if low_freq else self.frequencies[0]
        high_freq = high_freq if high_freq else self.frequencies[-1]
        return self.phases_interpolator.get_band_average_at_point(azimuth, elevation, low_freq, high_freq)
