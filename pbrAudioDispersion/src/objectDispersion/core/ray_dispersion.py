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

import os
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

from physicsSolver import EntityManager

from ..lib.object_dispersion import ObjectDispersion
from ..lib.dispersion_data import ObjectDispersionPattern

# Integration with the ray tracer
@dataclass
class DispersionAwareRayTracer:
    """
    Extension of the ray tracer that uses dispersion patterns
    for more accurate source modeling.
    """
    entity_manager: EntityManager
    
    def __post_init__(self):
        self.dispersion_calculator = ObjectDispersion(self.entity_manager)
        self.dispersion_cache: Dict[int, ObjectDispersionPattern] = {}
    
    def get_source_radiation(
        self,
        obj_idx: int,
        frequency: float,
        direction: np.ndarray,
        sample_idx: float
    ) -> float:
        """
        Get radiation from an object in a specific direction.
        
        This is called by the ray tracer when initializing rays.
        """
        # Get or compute dispersion pattern
        if obj_idx not in self.dispersion_cache:
            dispersion = self.dispersion_calculator.compute(obj_idx)
            self.dispersion_cache[obj_idx] = dispersion
        else:
            dispersion = = self.dispersion_cache[obj_idx]
        
        # Get radiation strength
        radiation = self.dispersion_calculator.get_radiation_for_ray_tracer(
            dispersion=dispersion,
            frequency=frequency,
            direction=direction
        )
        
        return radiation
    
    def get_initial_ray_distribution(
        self,
        obj_idx: int,
        sample_idx: float,
        n_rays: int = 64
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get optimal ray distribution for an object based on its dispersion pattern.
        
        Returns:
            Tuple of (directions, intensities) for initial rays
        """
        # Get dispersion pattern
        if obj_idx not in self.dispersion_cache:
            dispersion = self.dispersion_calculator.compute(obj_idx)
            self.dispersion_cache[obj_idx] = dispersion
        else:
            dispersion = self.dispersion_cache[obj_idx]
        
        # Get modal excitation from forces
        forces = self.entity_manager.get('forces')
        force_data = None
        for f_idx, f in forces.items():
            if f.obj_idx == obj_idx:
                force_data = f
                break
        
        if force_data:
            excitation = self.dispersion_calculator.get_modal_excitation(
                dispersion=dispersion,
                force_data=force_data,
                sample_idx=sample_idx
            )
        else:
            excitation = np.ones(dispersion.n_modes) / dispersion.n_modes
        
        # Generate rays weighted by excitation and radiation pattern
        directions = np.zeros((n_rays, 3))
        intensities = np.zeros(n_rays)
        
        # Use importance importance sampling based on radiation pattern
        for i in range(n_rays):
            # Random direction
            theta = np.random.uniform(0, 2 * np.pi)
            phi = np.arccos(2 * np.random.random() - 1)
            
            direction = np.array([
                np.sin(phi) * np.cos(theta),
                np.sin(phi) * np.sin(theta),
                np.cos(phi)
            ])
            
            # Get radiation in this direction
            # Average over all modes weighted by excitation
            radiation = 0.0
            for mode_idx, radiator in enumerate(dispersion.radiators):
                mode_radiation = dispersion.get_radiation_pattern(radiator.frequency)
                # Simplified: use the mode's radiation pattern
                pattern_strength = radiator.get_radiation_at_direction(theta, phi - np.pi/2)
                radiation += excitation[mode_idx] * pattern_strength
            
            directions[i] = direction
            intensities[i] = max(radiation, 0.0)
        
        # Normalize intensities
        total_intensity = np.sum(intensities)
        if total_intensity > 0:
            intensities /= total_intensity

        return directions, intensities
