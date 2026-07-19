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

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

@dataclass
class ModalRadiator:
    """
    Represents a single modal radiator with its dispersion characteristics.
    Each mode radiates sound with a specific directivity pattern based on
    the mode shape and the object's geometry.
    """
    mode_idx: int
    frequency: float  # Hz
    t60: float  # Decay time in seconds
    gain: float  # Mode gain at reference vertex
    radiation_pattern: np.ndarray  # Shape (n_directions, 2) - azimuth, elevation pairs
    radiation_strength: np.ndarray  # Shape (n_directions,) - relative radiation strength
    
    # Modal shape information
    mode_order: Tuple[int, int, int]  # (l, m, n) for rectangular, or (l, m) for spherical
    nodal_lines: List[np.ndarray]  # Lines of zero displacement
    
    # Frequency-dependent directivity
    directivity_center: float  # Hz - frequency of maximum directivity
    
    def get_radiation_at_direction(self, azimuth: float, elevation: float) -> float:
        """
        Get radiation strength for a specific direction using interpolation.
        """
        from scipy.interpolate import griddata
        
        points = self.radiation_pattern
        values = self.radiation_strength
        
        # Interpolate at the requested direction
        result = griddata(points, values, np.array([[azimuth, elevation]]), 
                         method='linear', fill_value=0.0)
        
        return float(result[0])

@dataclass
class ObjectDispersionPattern:
    """
    Complete dispersion pattern for an object, combining all modal radiators.
    """
    obj_idx: int
    obj_name: str
    n_modes: int
    n_vertices: int
    
    # Modal radiators
    radiators: List[ModalRadiator]
    
    # Overall radiation characteristics
    center_of_radiation: np.ndarray  # 3D position (world coordinates)
    radiation_radius: float  # Effective radius for radiation
    
    # Frequency-dependent dispersion
    frequency_response: np.ndarray  # Shape (n_freq_bins,)
    frequency_bins: np.ndarray  # Hz
    
    # Spatial dispersion (spherical harmonics decomposition)
    spatial_harmonics: np.ndarray  # Shape (n_harmonics, n_freq_bins)
    
    # Energy distribution
    energy_per_mode: np.ndarray  # Shape (n_modes,)
    total_radiated_energy: float
    
    def get_radiation_pattern(self, frequency: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get radiation pattern at a specific frequency.
        Returns (directions, strengths)
        """
        # Find nearest frequency bin
        freq_idx = np.argmin(np.abs(self.frequency_bins - frequency))
        
        # Combine spatial harmonics with frequency response
        directions = np.array([r.radiation_pattern for r in self.radiators])
        strengths = np.array([r.radiation_strength for r in self.radiators])
        
        # Weight by frequency response
        freq_weight = self.frequency_response[freq_idx]
        
        return directions, strengths * freq_weight
    
    def get_directivity_index(self, frequency: float) -> float:
        """
        Calculate directivity index (DI) at a given frequency.
        DI = 10 * log10(Q), where Q is the directivity factor.
        """
        directions, strengths = self.get_radiation_pattern(frequency)
        
        # Calculate directivity factor
        mean_strength = np.mean(strengths)
        max_strength = np.max(strengths)
        
        if mean_strength > 0:
            Q = max_strength / mean_strength
            DI = 10 * np.log10(Q)
        else:
            DI = 0.0
        
        return DI
