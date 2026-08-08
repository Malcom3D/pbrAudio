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
from typing import Union, Optional, Any
from typing import List, Tuple
import numpy as np
import numba as nb

from ..lib.interpolator import FrequencyInterpolator

@dataclass
class AcousticCoefficients:
    """Represents frequency-dependent coefficients using numpy arrays."""
    frequencies: np.ndarray  # Frequency values array
    coefficients: np.ndarray  # Corresponding coefficient values array
    phases: np.ndarray = None # Corresponding phases values array

    def __post_init__(self):
        # Create interpolator
        self.coeffs_interpolator = FrequencyInterpolator(self.frequencies, self.coefficients, method='cubic')
        if not self.phases == None:
            self.phases_interpolator = FrequencyInterpolator(self.frequencies, self.phases, method='cubic')

    def get_coeffs(self, low_freq: Optional[float] = None, high_freq: Optional[float] = None, num_points: Optional[int] = 0) -> np.ndarray:
        low_freq = low_freq if low_freq else self.frequencies[0]
        high_freq = high_freq if high_freq else self.frequencies[-1]
        num_points = num_points if not num_points == 0 else len(self.frequencies)
        frequencies, coeffs = self.coeffs_interpolator.interpolate_band(low_freq, high_freq, num_points)
        phases = np.array([], dtype=np.float32)
        if not self.phases == None:
            frequencies, phases = self.phases_interpolator.interpolate_band(low_freq, high_freq, num_points)
        return frequencies, coeffs, phases

    def get_avg_coeffs(self, low_freq: Optional[float] = None, high_freq: Optional[float] = None) -> np.ndarray:
        low_freq = low_freq if low_freq else self.frequencies[0]
        high_freq = high_freq if high_freq else self.frequencies[-1]
        coeff = self.coeffs_interpolator.get_band_average(low_freq, high_freq)
        phase = None
        if not self.phases == None:
            phase = self.phases_interpolator.get_band_average(low_freq, high_freq)
        return coeff, phase

    def get_bands_avg(self, freq_bands: List[Tuple[float, float]], num_points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Numba-accelerated SIMD computation of band averages with phases.
        """
        n_bands = len(freq_bands)
        avg_coeffs = np.zeros((1,n_bands), dtype=np.float32)
        avg_phases = np.zeros((1,n_bands), dtype=np.float32)

        coeff_interp_func = self.coeffs_interpolator.interp_func
        phase_interp_func = None
        if not self.phases == None:
            phase_interp_func = self.phases_interpolator.interp_func
 
        # Process all bands in parallel
        return _compute_band_averages(freq_bands, n_bands, num_points, coeff_interp_func, phase_interp_func, avg_coeffs, avg_phases)

    @staticmethod
    @nb.njit(parallel=True, fastmath=True, cache=True)
    def _compute_band_averages(freq_bands: np.ndarray, n_bands: int, num_points: int, coeff_interp_func, phase_interp_func, avg_coeffs: np.ndarray, avg_phases: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        for i in nb.prange(n_bands):
            low_freq, high_freq = freq_bands[i]

            # Compute averages using Simpson's rule for better accuracy
            coeff_sum = 0.0
            phase_sum = 0.0
            
            for j in range(num_points):
                t = j / (num_points - 1) if num_points > 1 else 0
                freq = low_freq + t * (high_freq - low_freq)
                
                coeff_sum += coeff_interp_func(freq) if coeff_interp_func(freq) >= 0 else 0
                if not phase_interp_func == None:
                    phase_sum += phase_interp_func(freq)
            
            avg_coeffs[0][i] = coeff_sum / num_points
            if not phase_interp_func == None:
                avg_phases[0][i] = phase_sum / num_points
        
        return avg_coeffs, avg_phases

@dataclass
class AcousticProperties:
    """Container for acoustic properties."""
    absorption: Union[float, Optional[AcousticCoefficients]] = None
    transmission: Union[float, Optional[AcousticCoefficients]] = None
    reflection: Union[float, Optional[AcousticCoefficients]] = None
    scattering: Union[float, Optional[AcousticCoefficients]] = None

@dataclass
class AcousticShader:
    sound_speed: float = 343.0  # m/s
    young_modulus: float = None
    poisson_ratio: float = None
    density: float = None
    damping: float = None
    friction: float = None
    roughness: float = None
    impedence: float = None
    temperature: float = None
    failure_stress": float = None
    low_frequency: float = 1.0
    high_frequency: float = 24000.0
    acoustic_properties: Optional[AcousticProperties] = field(default_factory=AcousticProperties)

    def get_data(self, properties: Union[List[str], str]) -> AcousticCoefficients:
        """Retrieve data for one or more acoustic properties."""
        for property in properties:
            if property in self.acoustic_properties:
                return self.acoustic_properties[property]
        return None
