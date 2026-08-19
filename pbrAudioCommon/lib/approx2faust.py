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

import trimesh
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from ..lib.voxel_mesh_modal_analysis import VoxelMeshModalAnalysis

from ..lib.functions import _compute_rayleigh_damping
from ..lib.primitive_geometry import PrimitiveGeometry

@dataclass
class Approx2Faust:
    """
    Generate modal models from Voxel-based approximation of mesh.
    """
    def __post_init__(self):
        # init primitive geometry classifier
        self.primitive_geometry = PrimitiveGeometry()
    
    def compute(self, vertices: np.ndarray, faces: np.ndarray, young_modulus: float, poisson_ratio: float, density: float, damping: float, min_freq: float, max_freq: float, system_min_freq: float, system_max_freq: float, n_modes: int, voxel_size: float) -> Dict[str, Any]:
        """
        Compute approximate modal parameters for a mesh.
        
        Parameters:
        -----------
        vertices : np.ndarray
            Vertex positions (N, 3)
        faces : np.ndarray
            Face indices (M, 3)
        young_modulus : float
            Young's modulus (Pa)
        poisson_ratio : float
            Poisson's ratio
        density : float
            Density (kg/m³)
        damping : float
            Damping ratio ratio
        min_freq : float
            Minimum frequency (Hz)
        max_freq : float
            Maximum frequency (Hz)
        n_modes : int
            Number of modes to generate
        voxel_size : float
            Voxel size for discretization
            
        Returns:
        --------
        Dict[str, Any]
            Dictionary with keys: 'frequencies', 'gains', 't60s', 'metadata'
        """
        mesh = trimesh.Trimesh(vertices, faces=faces)
        # Voxelize the mesh
        voxel_grid = self._voxelize_mesh(mesh, voxel_size)

        rayleigh_alpha, rayleigh_beta = _compute_rayleigh_damping(min_freq, max_freq, damping)

        material_properties = {
            'young_modulus': young_modulus,
            'poisson_ratio': poisson_ratio,
            'density': density,
            'rayleigh_alpha': rayleigh_alpha,
            'rayleigh_beta': rayleigh_beta
        }

        # Create modal analysis object
        modal_analysis = VoxelMeshModalAnalysis(voxel_grid, voxel_size, material_properties)

        # Compute modes
        frequencies, mode_shapes = modal_analysis.compute_modes(n_modes=n_modes, min_freq=min_freq, max_freq=max_freq, system_min_freq=system_min_freq, system_max_freq=system_max_freq)

        if len(frequencies) == 0:
            # Return empty results
            return {
                'frequencies': np.array([]),
                'gains': np.array([]),
                't60s': np.array([]),
                'metadata': {
                    'voxel_size': voxel_size,
                    'n_voxels': int(np.sum(modal_analysis.voxel_grid)),
                    'material': material_properties,
                    'n_modes': 0
                }
            }

        # Classify the shape
        shape_props = self.primitive_geometry.classify(vertices, faces)

        # Interpolate mode shapes to original vertices to get position-specific gains
        gains = modal_analysis.interpolate_mode_shapes_to_points(vertices, mode_shapes, shape_props)  # shape (N_vertices, n_modes)

        # Compute T60 from damping
        # For each mode, damping ratio = alpha/(2*omega) + beta*omega/2
        omega = 2 * np.pi * frequencies
        damping_ratios = rayleigh_alpha / (2 * omega) + rayleigh_beta * omega / 2
        # T60 = ln(1000) / (damping_ratio * omega) ? Actually T60 = 6.9078 / (damping_ratio * omega)
        # But damping_ratio is already the fraction of critical damping, the decay rate is damping_ratio * omega.
        # So T60 = 6.9078 / (damping_ratio * omega)
        t60s = 6.9078 / (damping_ratios * omega)  # in seconds
        # Clip to reasonable values
        t60s = np.clip(t60s, 0.001, 100.0)

        # Transpose gains to shape (n_modes, n_vertices) for Faust
        gains = gains.T

        # Get modal stochastic variation based on material
        stochastic_factor = modal_analysis.compute_stochastic_variation_factors(n_modes=n_modes, min_freq=min_freq, max_freq=max_freq)

        frequencies *= stochastic_factor['freq_scale']
        t60s *= stochastic_factor['t60_scale']
        gains *= stochastic_factor['gain_scale'][:, None]
        # Normalize gains
        gains /= np.max(abs(gains))

        return {
            'frequencies': frequencies,
            'gains': gains,
            't60s': t60s,
            'metadata': {
                'voxel_size': voxel_size,
                'n_voxels': int(np.sum(modal_analysis.voxel_grid)),
                'n_dofs': mode_shapes.shape[0],
                'material': material_properties,
                'frequency_range': [float(min_freq), float(max_freq)],
                'n_modes': len(frequencies),
                'n_vertices': vertices.shape[0]
            }
        }

    def _voxelize_mesh(self, mesh: trimesh.Trimesh, voxel_size: float) -> np.ndarray:
        """
        Convert mesh to voxel grid

        Parameters:
        -----------
        mesh : trimesh.Trimesh
            Input mesh
        voxel_size : float
            Voxel size

        Returns:
        --------
        np.ndarray
            3D boolean array representing voxelized mesh
        """
        # Get mesh bounds
        bounds = mesh.bounds
        min_bound = bounds[0]
        max_bound = bounds[1]

        # Calculate grid dimensions
        dims = np.ceil((max_bound - min_bound) / voxel_size).astype(int) + 2
        dims = np.maximum(dims, 1)

        # Voxelize using trimesh
        voxelized = mesh.voxelized(voxel_size)

        # Convert to boolean grid
        voxel_grid = np.zeros(dims, dtype=bool)

        # Get voxel indices from trimesh voxelization
        if hasattr(voxelized, 'points'):
            # For trimesh VoxelGrid
            voxel_matrix = voxelized.matrix
            # Pad the matrix to match our dimensions
            voxel_grid[:voxel_matrix.shape[0],
                      :voxel_matrix.shape[1],
                      :voxel_matrix.shape[2]] = voxel_matrix
        else:
            # Fallback: use filled voxelization
            voxel_grid = voxelized.fill().matrix

        return voxel_grid

    def to_faust_lib(self, modal_params: Dict[str, Any], output_name: str, min_freq: float, max_freq: float, t60_scale: float = 1) -> str:
        """
        Generate Faust .lib file content for modal synthesis
        
        Parameters:
        -----------
        modal_params : dict
            Modal analysis results from compute() (must contain 'frequencies', 'gains', 't60s')
        output_name : str
            Name for the Faust output
        min_freq : float
            Minimum frequency for the modal model
        max_freq : float
            Maximum frequency for the modal model
        t60_scale : float, optional
            Scaling factor applied to the T60 values in the Faust expression.
            Default is 1.0 (no scaling).
        
        Returns:
        --------
        str
            Faust .lib file content
        """
        frequencies = modal_params.get('frequencies', [])
        gains = modal_params.get('gains', [])   # shape (n_modes, n_vertices)
        t60s = modal_params.get('t60s', [])
        metadata = modal_params.get('metadata', {})
        
        n_modes = len(frequencies)
        n_vertices = metadata.get('n_vertices', 0) if gains.shape[1] > 0 else 0
        
        if n_modes == 0 or n_vertices == 0:
            return self._generate_empty_lib(output_name, min_freq, max_freq, metadata.get('n_voxels', 0))
        
        # Filter modes by frequency range if specified (already done in compute, but safe)
        valid_idx = np.where((frequencies >= min_freq) & (frequencies <= max_freq))[0]
        if len(valid_idx) < n_modes:
            frequencies = frequencies[valid_idx]
            gains = gains[valid_idx, :]
            t60s = t60s[valid_idx]
            n_modes = len(frequencies)
            if n_modes == 0:
                return self._generate_empty_lib(output_name, min_freq, max_freq, metadata.get('n_voxels', 0))
        
        # Prepare frequency string
        freq_values = [f"{freq:.6f}" for freq in frequencies]
        freq_str = ", ".join(freq_values)
        
        # Prepare T60 strings
        t60_values = [f"{t:.6f}" for t in t60s]
        t60_str = ", ".join(t60_values)
        
        # T60 scale factor (as used in original mesh2faust)
        t60_scale = 1.0 / (6.9078 * max_freq) if max_freq > 0 else 1.0
        t60_scale_str = f"{t60_scale:.10f}"
        
        # Generate gains matrix as waveform
        # Each row corresponds to a mode, each column to a vertex
        gain_lines = []
        for mode_idx in range(n_modes):
            mode_gains = gains[mode_idx, :]
            gain_str = ", ".join([f"{g:.6f}" for g in mode_gains])
            gain_lines.append(f"        {gain_str}")
        gain_waveform = ",\n".join(gain_lines)
        
        # Build the complete Faust lib content
        faust_lib = f"""// ------------------------------------------------------------
// Voxel approximated mesh modal model for {output_name}
// Generated by Approx2Faust fallback mechanism
// Modes: {n_modes}, Vertices: {n_vertices}
// Frequency range: {min_freq:.1f} - {max_freq:.1f} Hz
// ------------------------------------------------------------

declare name        "{output_name}";
declare version     "0.1";
declare author      "Approx2Faust";
declare license     "GPL";

import("stdfaust.lib");

// Modal parameters
nModes = {n_modes};
nExPos = {n_vertices};

// T60 scale factor for damping calculation
t60Scale = {t60_scale_str};

// Mode frequencies (Hz)
modeFreqsUnscaled = ba.take(nModes, ({freq_str}));

// T60 decay times (seconds)
modesT60s = t60Scale : ba.take(nModes, ({t60_str}));

// Mode gains (nModes x nExPos)
modesGains = waveform{{
{gain_waveform}
}};

// Process function
process = no.process;
"""
        return faust_lib

    def _generate_empty_lib(self, output_name: str, min_freq: float, 
                           max_freq: float, n_voxels: int) -> str:
        """
        Generate empty Faust lib when no modes are found
        
        Parameters:
        -----------
        output_name : str
            Name for the Faust output
        min_freq : float
            Minimum frequency
        max_freq : float
            Maximum frequency
        n_voxels : int
            Number of voxels
        
        Returns:
        --------
        str
            Empty Faust .lib file content
        """
        faust_lib = f"""// ------------------------------------------------------------
// Voxel approximated mesh modal model for {output_name}
// Generated by Approx2Faust fallback mechanism
// Modes: 0, Voxels: {n_voxels}
// Frequency range: {min_freq:.1f} - {max_freq:.1f} Hz
// ------------------------------------------------------------

declare name        "{output_name}";
declare version     "0.1";
declare author      "Approx2Faust";
declare license     "GPL";

import("stdfaust.lib");

// Modal parameters
nModes = 0;
nExPos = 0;

// T60 scale factor
t60Scale = 1.0;

// Mode frequencies (Hz)
modeFreqsUnscaled = ba.take(nModes, ());

// T60 decay times (seconds)
modesT60s = t60Scale : ba.take(nModes, ());

// Mode gains (nModes x nExPos)
modesGains = waveform{{}};

// Process function
process = no.process;
"""
        return faust_lib
