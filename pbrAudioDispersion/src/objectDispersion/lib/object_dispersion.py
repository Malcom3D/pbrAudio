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
from scipy.spatial import ConvexHull

from physicsSolver import EntityManager
from physicsSolver.lib.functions import _parse_lib, _load_mesh
from physicsSolver.lib.trajectory_data import TrajectoryData
from physicsSolver.lib.force_data import ContactType

from .dispersion_data import ObjectDispersionPattern, ModalRadiator

@dataclass
class ObjectDispersion:
    """
    Main class for computing object dispersion patterns.
    Bridges modal synthesis with acoustic propagation.
    """
    entity_manager: EntityManager
    
    def __post_init__(self):
        self.config = self.entity_manager.get('config')
        self.cache_path = f"{self.config.system.cache_path}/dispersion"
        os.makedirs(self.cache_path, exist_ok=True)
        
        # Initialize spherical harmonics for radiation pattern decomposition
        self._init_spherical_harmonics()
    
    def _init_spherical_harmonics(self, max_order: int = 4):
        """Initialize spherical harmonics basis functions."""
        self.sh_max_order = max_order
        self.n_harmonics = (max_order + 1) ** 2
        
        # Generate sampling directions on sphere
        n_samples = 1000
        phi = np.pi * (3. - np.sqrt(5.))  # Golden angle
        theta = phi * np.arange(n_samples)
        z = np.linspace(1 - 1/n_samples, 1/n_samples - 1, n_samples)
        radius = np.sqrt(1 - z * z)
        
        self.sample_azimuths = np.arctan2(radius * np.sin(theta), radius * np.cos(theta))
        self.sample_elevations = np.arcsin(z)
    
    def compute(self, obj_idx: int) -> ObjectDispersionPattern:
        """
        Compute dispersion pattern for a a given object.
        
        Args:
            obj_idx: Object index
            
        Returns:
            ObjectDispersionPattern containing all dispersion information
        """
        config = self.config
        
        # Find object config
        config_obj = None
        for obj in config.objects:
            if obj.idx == obj_idx:
                config_obj = obj
                break
        
        if not config_obj:
            raise ValueError(f"Object {obj_idx} not found")
        
        # Get modal model parameters
        modal_data = self._load_modal_data(config_obj)
        
        # Get object geometry
        vertices, normals, faces = _load_mesh(config_obj, 0)
        
        # Get trajectory information
        trajectories = self.entity_manager.get('trajectories')
        trajectory = None
        for t_idx, traj in trajectories.items():
            if hasattr(traj, 'obj_idx') and traj.obj_idx == obj_idx:
                trajectory = traj
                break
        
        # Compute dispersion pattern
        dispersion_pattern = self._compute_dispersion(
            config_obj=config_obj,
            modal_data=modal_data,
            vertices=vertices,
            normals=normals,
            faces=faces,
            trajectory=trajectory
        )
        
        # Save to cache
        self._save_dispersion(dispersion_pattern, config_obj.name)
        
        return dispersion_pattern
    
    def _load_modal_data(self, config_obj: Any) -> Dict[str, Any]:
        """Load modal model data from .lib file."""
        cache_path = self.config.system.cache_path
        obj_name = config_obj.name
        
        if config_obj.proxy_type is not False:
            obj_name = f"{config_obj.name}_proxy_{config_obj.proxy_type}"
        
        lib_file = f"{cache_path}/dspsp/{obj_name}.lib"
        
        if not os.path.exists(lib_file):
            print(f"Warning: Modal model not found for {obj_name}, using fallback")
            return self._create_fallback_modal_data(config_obj)
        
        return _parse_lib(lib_file)
    
    def _create_fallback_modal_data(self, config_obj: Any) -> Dict[str, Any]:
        """Create fallback modal data when .lib file is not available."""
        n_modes = self.config.system.modal_modes
        
        # Generate reasonable modal frequencies
        frequencies = np.logspace(
            np.log10(config_obj.acoustic_shader.low_frequency or 20),
            np.log10(config_obj.acoustic_shader.high_frequency or 20000),
            n_modes
        )
        
        # Generate T60 values
        damping = config_obj.acoustic_shader.damping or 0.02
        t60s = 3 * np.log(10) / (np.pi * damping * frequencies)
        t60s = np.clip(t60s, 0.001, 10.0)
        
        # Generate placeholder gains
        n_vertices = 100  # Estimated
        gains = np.random.randn(n_modes, n_vertices) * 0.1
        
        return {
            'frequencies': frequencies,
            't60s': t60s,
            'gains': gains,
            'nModes': n_modes
        }
    
    def _compute_dispersion(
        self,
        config_obj: Any,
        modal_data: Dict[str, Any],
        vertices: np.ndarray,
        normals: np.ndarray,
        faces: np.ndarray,
        trajectory: Optional[Any]
    ) -> ObjectDispersionPattern:
        """
        Compute the complete dispersion pattern for an object.
        
        This is the core algorithm that bridges modal synthesis with propagation.
        """
        n_modes = modal_data['nModes']
        n_vertices = len(vertices)
        
        # 1. Compute mode shapes and radiation patterns
        radiators = []
        mode_energies = []
        
        for mode_idx in range(n_modes):
            frequency = modal_data['frequencies'][mode_idx]
            t60 = modal_data['t60s'][mode_idx]
            gains = modal_data['gains'][mode_idx] if mode_idx < len(modal_data['gains']) else np.ones(n_vertices) * 0.1
            
            # Compute mode shape from gains
            mode_shape = self._compute_mode_shape(gains, vertices, normals)
            
            # Compute radiation pattern for this mode
            radiation_pattern, radiation_strength = self._compute_mode_radiation(
                mode_shape=mode_shape,
                frequency=frequency,
                vertices=vertices,
                normals=normals,
                faces=faces
            )
            
            # Estimate mode order from frequency
            mode_order = self._estimate_mode_order(mode_idx, frequency)
            
            # Create radiator
            radiator = ModalRadiator(
                mode_idx=mode_idx,
                frequency=frequency,
                t60=t60,
                gain=np.mean(np.abs(gains)),
                radiation_pattern=radiation_pattern,
                radiation_strength=radiation_strength,
                mode_order=mode_order,
                nodal_lines=[],  # Can be computed from mode shape
                directivity_center=frequency
            )
            
            radiators.append(radiator)
            mode_energies.append(np.sum(gains ** 2))
        
        # 2. Compute overall radiation characteristics
        center_of_radiation = np.mean(vertices, axis=0)
        
        # Compute effective radiation radius
        hull = ConvexHull(vertices)
        radiation_radius = np.mean([
            np.linalg.norm(v - center_of_radiation) 
            for v in vertices[hull.vertices]
        ])
        
        # 3. Compute frequency response
        freq_bins = np.logspace(
            np.log10(config_obj.acoustic_shader.low_frequency or 20),
            np.log10(config_obj.acoustic_shader.high_frequency or 20000),
            100
        )
        
        frequency_response = self._compute_frequency_response(
            radiators=radiators,
            freq_bins=freq_bins
        )
        
        # 4. Compute spatial harmonics decomposition
        spatial_harmonics = self._compute_spatial_harmonics(
            radiators=radiators,
            freq_bins=freq_bins
        )
        
        # 5. Normalize energies
        mode_energies = np.array(mode_energies)
        total_energy = np.sum(mode_energies)
        if total_energy > 0:
            mode__energies /= total_energy
        
        # Create dispersion pattern
        dispersion_pattern = ObjectDispersionPattern(
            obj_idx=config_obj.idx,
            obj_name=config_obj.name,
            n_modes=n_modes,
            n_vertices=n_vertices,
            radiators=radiators,
            center_of_radiation=center_of_radiation,
            radiation_radius=radiation_radius,
            frequency_response=frequency_response,
            frequency_bins=freq_bins,
            spatial_harmonics=spatial_harmonics,
            energy_per_mode=mode_energies,
            total_radiated_energy=total_energy
        )
        
        return dispersion_pattern
    
    def _compute_mode_shape(
        self,
        gains: np.ndarray,
        vertices: np.ndarray,
        normals: np.ndarray
    ) -> np.ndarray:
        """
        Compute mode shape (displacement pattern) from modal gains.
        
        The mode shape describes how the object deforms in this mode.
        """
        n_vertices = len(vertices)
        mode_shape = np.zeros((n_vertices, 3))
        
        # Gains represent displacement amplitude at each vertex
        # The direction is along the vertex normal (for bending modes)
        # or radial (for breathing modes)
        for i in range(n_vertices):
            # Displacement is proportional to gain along normal direction
            mode_shape[i] = gains[i] * normals[i]
        
        return mode_shape
    
    def _compute_mode_radiation(
        self,
        mode_shape: np.ndarray,
        frequency: float,
        vertices: np.ndarray,
        normals: np.ndarray,
        faces: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute radiation pattern for a single mode.
        
        Uses the mode shape to determine how sound radiates from the object.
        
        Returns:
            Tuple of (directions, strengths) for radiation pattern
        """
        # Generate sampling directions on sphere
        n_directions = 100
        phi = np.pi * (3. - np.sqrt(5.))
        theta = phi * np.arange(n_directions)
        z = np.linspace(1 - 1/n_directions, 1/n_directions - 1, n_directions)
        radius = np.sqrt(1 - z * z)
        
        directions = np.zeros((n_directions, 2))
        directions[:, 0] = np.arctan2(radius * np.sin(theta), radius * np.cos(theta))
        directions[:, 1] = np.arcsin(z)
        
        # Compute radiation strength for each direction
        strengths = np.zeros(n_directions)
        
        # For each vertex, compute its contribution to each direction
        # Based on the Rayleigh integral approximation
        center = np.mean(vertices, axis=0)
        k = 2 * np.pi * frequency / 343.0  # Wavenumber
        
        for i, (az, el) in enumerate(directions):
            # Direction vector
            dir_vec = np.array([
                np.cos(el) * np.cos(az),
                np.cos(el) * np.sin(az),
                np.sin(el)
            ])
            
            # Sum contributions from all vertices
            for j in range(len(vertices)):
                # Position relative to center
                r = vertices[j] - center
                
                # Phase factor
                phase = k * np.dot(r, dir_vec)
                
                # Amplitude from mode shape projected onto normal
                amplitude = np.dot(mode_shape[j], normals[j])
                
                # Add contribution with phase
                strengths[i] += amplitude * np.cos(phase)
        
        # Normalize
        max_strength = np.max(np.abs(strengths))
        if max_strength > 0:
            strengths /= max_strength
        
        return directions, strengths
    
    def _estimate_mode_order(
        self,
        mode_idx: int,
        frequency: float
    ) -> Tuple[int, int, int]:
        """
        Estimate the mode order (l, m, n) from frequency and index.
        
        For simple geometries, this can be derived analytically.
        For complex geometries, we use heuristic based on frequency.
        """
        # Simple heuristic: higher modes have higher orders
        # This can be refined with actual mode shape analysis
        l = (mode_idx // 4) + 1
        m = ((mode_idx % 4) // 2) + 1
        n = (mode_idx % 2) + 1
        
        return (l, m, n)
    
    def _compute_frequency_response(
        self,
        radiators: List[ModalRadiator],
        freq_bins: np.ndarray
    ) -> np.ndarray:
        """
        Compute overall frequency response by combining all modal radiators.
        """
        frequency_response = np.zeros(len(freq_bins))
        
        for radiator in radiators:
            # Each mode contributes a resonant peak
            f0 = radiator.frequency
            Q = 2 * np.pi * f0 * radiator.t60 / (3 * np.log(10))
            
            # Lorentzian resonance curve
            contribution = 1.0 / (1.0 + ((freq_bins - f0) / (f0 / (2 * Q))) ** 2)
            
            # Weight by mode gain
            frequency_response += radiator.gain * contribution
        
        # Normalize
        max_response = np.max(frequency_response)
        if max_response > 0:
            frequency_response /= max_response
        
        return frequency_response
    
    def _compute_spatial_harmonics(
        self,
        radiators: List[ModalRadiator],
        freq_bins: np.ndarray
    ) -> np.ndarray:
        """
        Decompose radiation patterns into spherical harmonics.
        
        This provides a compact representation of the dispersion pattern
        that can be efficiently used in the ray tracer.
        """
        n_harmonics = self.n_harmonics
        n_freq_bins = len(freq_bins)
        
        spatial_harmonics = np.zeros((n_harmonics, n_freq_bins))
        
        # For each frequency bin, decompose the combined radiation pattern
        for freq_idx in range(n_freq_bins):
            frequency = freq_bins[freq_idx]
            
            # Get combined radiation pattern at this frequency
            directions, strengths = self._get_combined_radiation(
                radiators=radiators,
                frequency=frequency
            )
            
            # Decompose into spherical harmonics
            harmonics = self._spherical_harmonic_decomposition(
                directions=directions,
                strengths=strengths,
                max_order=self.sh_max_order
            )
            
            spatial_harmonics[:, freq_idx] = harmonics
        
        return spatial_harmonics
    
    def _get_combined_radiation(
        self,
        radiators: List[ModalRadiator],
        frequency: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get combined radiation pattern from all radiators at a given frequency.
        """
        # Use a dense sampling of directions
        n_samples = 500
        phi = np.pi * (3. - np.sqrt(5.))
        theta = phi * np.arange(n_samples)
        z = np.linspace(1 - 1/n_samples, 1/n_samples - 1, n_samples)
        radius = np.sqrt(1 - z * z)
        
        directions = np.zeros((n_samples, 2))
        directions[:, 0] = np.arctan2(radius * np.sin(theta), radius * np.cos(theta))
        directions[:, 1] = np.arcsin(z)
        
        strengths = np.zeros(n_samples)
        
        # Sum contributions from all radiators
        for radiator in radiators:
            # Frequency-dependent weighting
            f0 = radiator.frequency
            Q = 2 * np.pi * f0 * radiator.t60 / (3 * np.log(10))
            
            # Lorentzian weight
            weight = 1.0 / (1.0 + ((frequency - f0) / (f0 / (2 * Q))) ** 2)
            
            # Interpolate radiator's pattern at our sampling directions
            for i, (az, el) in enumerate(directions):
                pattern_strength = radiator.get_radiation_at_direction(az, el)
                strengths[i] += weight * radiator.gain * pattern_strength
        
        # Normalize
        max_strength = np.max(np.abs(strengths))
        if max_strength > 0:
            strengths /= max_strength
        
        return directions, strengths
    
    def _spherical_harmonic_decomposition(
        self,
        directions: np.ndarray,
        strengths: np.ndarray,
        max_order: int = 4
    ) -> np.ndarray:
        """
        Decompose a radiation pattern into spherical harmonics coefficients.
        
        Uses the real spherical harmonics basis.
        """
        from scipy.special import sph_harm
        
        n_harmonics = (max_order + 1) ** 2
        coefficients = np.zeros(n_harmonics)
        
        # Convert directions to spherical coordinates
        azimuths = directions[:, 0]
        elevations = directions[:, 1]
        
        # Compute spherical harmonics for each direction
        for l in range(max_order + 1):
            for m in range(-l, l + 1):
                idx = l * (l + 1) + m
                
                # Compute spherical harmonic values
                Y_lm = sph_harm(m, l, azimuths, np.pi/2 - elevations)
                
                # Project strength onto this harmonic
                coefficients[idx] = np.real(np.sum(strengths * np.conj(Y_lm)))
        
        # Normalize coefficients
        norm = np.sqrt(np.sum(coefficients ** 2))
        if norm > 0:
            coefficients /= norm
        
        return coefficients
    
    def _save_dispersion(self, dispersion: ObjectDispersionPattern, name: str):
        """Save dispersion pattern to cache."""
        import pickle
        
        filepath = f"{self.cache_path}/{name}_dispersion.pkl"
        with open(filepath, 'wb') as f:
            pickle.dump(dispersion, f)
        
        print(f"Saved dispersion pattern for {name} to {filepath}")
    
    def load_dispersion(self, obj_name: str) -> Optional[ObjectDispersionPattern]:
        """Load dispersion pattern from cache."""
        import pickle
        
        filepath = f"{self.cache_path}/{obj_name}_dispersion.pkl"
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        
        return None
    
    def get_radiation_for_ray_tracer(
        self,
        dispersion: ObjectDispersionPattern,
        frequency: float,
        direction: np.ndarray
    ) -> float:
        """
        Get radiation strength for use in the ray tracer.
        
        This is the key bridge function - it tells the ray tracer
        how much energy is radiated in a specific direction at a specific frequency.
        
        Args:
            dispersion: The object's dispersion pattern
            frequency: Frequency of interest (Hz)
            direction: Direction vector (3,) from object to listener
            
        Returns:
            Radiation strength (0-1) for for this direction/frequency
        """
        # Convert direction to spherical coordinates
        azimuth = np.arctan2(direction[1], direction[0])
        elevation = np.arcsin(direction[2] / np.linalg.norm(direction))
        
        # Get radiation pattern at this frequency
        directions, strengths = dispersion.get_radiation_pattern(frequency)
        
        # Interpolate at the requested direction
        from scipy.interpolate import griddata
        
        result = griddata(
            directions, strengths,
            np.array([[azimuth, elevation]]),
            method='linear',
            fill_value=0.0
        )
        
        return float(result[0]) if not np.isnan(result[0]) else 0.0
    
    def get_source_position_for_ray(
        self,
        dispersion: ObjectDispersionPattern,
        sample_idx: float,
        trajectory: TrajectoryData
    ) -> np.ndarray:
        """
        Get the effective source position for ray tracing.
        
        For complex objects, the effective source position may be
        different from the geometric center, depending on which
        modes are excited.
        """
        # Get object position at this sample
        position = trajectory.get_position(sample_idx)
        
        # The effective source is the center of radiation
        # This can be offset from the geometric center based on mode shapes
        effective_position = position + dispersion.center_of_radiation
        
        return effective_position
    
    def get_modal_excitation(
        self,
        dispersion: ObjectDispersionPattern,
        force_data: ForceDataSequence,
        sample_idx: float
    ) -> np.ndarray:
        """
        Compute how much each mode is excited by the current forces.
        
        This bridges the force synthesis with the dispersion pattern.
        
        Returns:
            Array of excitation levels for each mode (n_modes,)
        """
        n_modes = dispersion.n_modes
        excitation = np.zeros(n_modes)
        
        # Get force at this sample
        normal_force = force_data.get_normal_force(sample_idx)
        tangential_force = force_data.get_tangential_force(sample_idx)
        contact_type = force_data.get_contact_type(sample_idx)
        
        # Different contact types excite different modes
        if contact_type == ContactType.IMPACT:
            # Impact excites all modes, weighted by frequency response
            for i, radiator in enumerate(dispersion.radiators):
                # Lower modes are more excited by impacts
                freq_weight = 1.0 / (1.0 + (radiator.frequency / 1000.0) ** 2)
                excitation[i] = np.linalg.norm(normal_force) * freq_weight
                
        elif contact_type in [ContactType.SLIDING, ContactType.SCRAPING]:
            # Sliding/scraping excites higher modes more
            for i, radiator in enumerate(dispersion.radiators):
                freq_weight = (radiator.frequency / 1000.0) / (1.0 + (radiator.frequency / 1000.0) ** 2)
                excitation[i] = np.linalg.norm(tangential_force) * freq_weight
                
        elif contact_type == ContactType.ROLLING:
            # Rolling excites modes related to rotational frequency
            for i, radiator in enumerate(dispersion.radiators):
                # Only modes near the rolling frequency
                freq_diff = np.abs(radiator.frequency - np.linalg.norm(force_data.get_tangential_velocity(sample_idx)) / (2 * np.pi))
                excitation[i] = np.exp(-freq_diff / 100.0)
        
        # Normalize
        total_excitation = np.sum(excitation)
        if total_excitation > 0:
            excitation /= total_excitation
        
        return excitation
