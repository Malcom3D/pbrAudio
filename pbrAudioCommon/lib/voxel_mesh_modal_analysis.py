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

import json
import numpy as np
import trimesh
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.linalg import eigsh
from typing import Dict, List, Tuple, Optional, Any

from ..lib.shape_properties import ShapeType, ShapeProperties

class VoxelMeshModalAnalysis:
    def __init__(self, voxel_grid, voxel_size, material_properties):
        """
        Initialize voxel mesh modal analysis
        
        Parameters:
        -----------
        voxel_grid : 3D numpy array (boolean or int)
            Binary array where True/1 indicates solid material
        voxel_size : float or tuple
            Size of each voxel (can be uniform or anisotropic)
        material_properties : dict
            Dictionary containing material properties
        """
        self.voxel_grid = np.array(voxel_grid, dtype=bool)
        self.nx, self.ny, self.nz = self.voxel_grid.shape
        
        # Handle voxel size (uniform or anisotropic)
        if isinstance(voxel_size, (int, float)):
            self.dx = self.dy = self.dz = float(voxel_size)
        else:
            self.dx, self.dy, self.dz = voxel_size

        # Material properties
        self.E = material_properties['young_modulus']
        self.nu = material_properties['poisson_ratio']
        self.rho = material_properties['density']
        self.alpha = material_properties.get('rayleigh_alpha', 0.0)
        self.beta = material_properties.get('rayleigh_beta', 0.0)
        
        # Compute Lamé parameters
        self.lambda_ = self.E * self.nu / ((1 + self.nu) * (1 - 2 * self.nu))
        self.mu = self.E / (2 * (1 + self.nu))
        
        # Initialize system matrices
        self.K = None  # Stiffness matrix
        self.M = None  # Mass matrix
        self.C = None  # Damping matrix

        # For interpolation: node index grid and origin
        self.node_index_grid = None
        self.origin = None
        
    def build_system_matrices(self):
        """
        Build stiffness and mass matrices using voxel-based FEM
        Uses trilinear hexahedral elements (8-node bricks)
        """
        # Get active voxels
        active_voxels = np.argwhere(self.voxel_grid)
        n_voxels = len(active_voxels)
        
        if n_voxels == 0:
            raise ValueError("No active voxels found in the grid")

        # Determine bounding box for node indexing
        min_idx = active_voxels.min(axis=0)
        max_idx = active_voxels.max(axis=0)
        self.origin = min_idx * np.array([self.dx, self.dy, self.dz])
        
        # Map voxel indices to global DOF indices
        self.voxel_to_dof = {}
        self.dof_to_voxel = {}
        n_nodes = 0

        # Initialize node_index_grid with -1
        self.node_index_grid = -np.ones((self.nx+1, self.ny+1, self.nz+1), dtype=int)
        
        # Each voxel has 8 corner nodes, each with 3 DOFs
        for voxel_idx, (i, j, k) in enumerate(active_voxels):
            for di in [0, 1]:
                for dj in [0, 1]:
                    for dk in [0, 1]:
                        node = (i + di, j + dj, k + dk)
                        if node not in self.voxel_to_dof:
                            self.voxel_to_dof[node] = n_nodes
                            self.dof_to_voxel[n_nodes] = node
                            # Fill node_index_grid
                            ni, nj, nk = node
                            self.node_index_grid[ni, nj, nk] = n_nodes
                            n_nodes += 1
        
        n_dofs = n_nodes * 3
        
        # Initialize sparse matrices
        rows_K, cols_K, data_K = [], [], []
        rows_M, cols_M, data_M = [], [], []
        
        # Element stiffness and mass matrices for 8-node brick
        Ke, Me = self._get_element_matrices()
        
        # Assemble global matrices
        for voxel_idx, (i, j, k) in enumerate(active_voxels):
            # Get global node indices for this voxel's corners
            element_dofs = []
            for di in [0, 1]:
                for dj in [0, 1]:
                    for dk in [0, 1]:
                        node = (i + di, j + dj, k + dk)
                        node_idx = self.voxel_to_dof[node]
                        for dof in range(3):
                            element_dofs.append(node_idx * 3 + dof)
            
            # Add to global matrices
            for a in range(24):  # 8 nodes * 3 DOFs
                for b in range(24):
                    if abs(Ke[a, b]) > 1e-15:
                        rows_K.append(element_dofs[a])
                        cols_K.append(element_dofs[b])
                        data_K.append(Ke[a, b])
                    
                    if abs(Me[a, b]) > 1e-15:
                        rows_M.append(element_dofs[a])
                        cols_M.append(element_dofs[b])
                        data_M.append(Me[a, b])
        
        # Build sparse matrices
        self.K = csr_matrix((data_K, (rows_K, cols_K)), shape=(n_dofs, n_dofs))
        self.M = csr_matrix((data_M, (rows_M, cols_M)), shape=(n_dofs, n_dofs))
        
        # Build damping matrix if needed
        if self.alpha > 0 or self.beta > 0:
            self.C = self.alpha * self.M + self.beta * self.K
        
        return n_dofs
    
    def _get_element_matrices(self):
        """
        Get element stiffness and mass matrices for 8-node hexahedral element
        Using standard trilinear shape functions
        """
        # Gauss quadrature points (2x2x2)
        gp = [-1/np.sqrt(3), 1/np.sqrt(3)]
        
        # Material matrix
        D = self._get_constitutive_matrix()
        
        # Initialize element matrices
        Ke = np.zeros((24, 24))
        Me = np.zeros((24, 24))
        
        # Integration loop
        for xi in gp:
            for eta in gp:
                for zeta in gp:
                    # Shape function derivatives at Gauss point
                    dN_dxi = 0.125 * np.array([
                        -(1-eta)*(1-zeta), (1-eta)*(1-zeta),
                        (1+eta)*(1-zeta), -(1+eta)*(1-zeta),
                        -(1-eta)*(1+zeta), (1-eta)*(1+zeta),
                        (1+eta)*(1+zeta), -(1+eta)*(1+zeta)
                    ])
                    dN_deta = 0.125 * np.array([
                        -(1-xi)*(1-zeta), -(1+xi)*(1-zeta),
                        (1+xi)*(1-zeta), (1-xi)*(1-zeta),
                        -(1-xi)*(1+zeta), -(1+xi)*(1+zeta),
                        (1+xi)*(1+zeta), (1-xi)*(1+zeta)
                    ])
                    dN_dzeta = 0.125 * np.array([
                        -(1-xi)*(1-eta), -(1+xi)*(1-eta),
                        -(1+xi)*(1+eta), -(1-xi)*(1+eta),
                        (1-xi)*(1-eta), (1+xi)*(1-eta),
                        (1+xi)*(1+eta), (1-xi)*(1+eta)
                    ])
                    
                    # Jacobian determinant
                    detJ = self.dx * self.dy * self.dz / 8
                    
                    # Build B matrix (strain-displacement)
                    B = np.zeros((6, 24))
                    for i in range(8):
                        B[0, 3*i] = dN_dxi[i] * 2/self.dx
                        B[1, 3*i+1] = dN_deta[i] * 2/self.dy
                        B[2, 3*i+2] = dN_dzeta[i] * 2/self.dz
                        B[3, 3*i] = dN_deta[i] * 2/self.dy
                        B[3, 3*i+1] = dN_dxi[i] * 2/self.dx
                        B[4, 3*i+1] = dN_dzeta[i] * 2/self.dz
                        B[4, 3*i+2] = dN_deta[i] * 2/self.dy
                        B[5, 3*i] = dN_dzeta[i] * 2/self.dz
                        B[5, 3*i+2] = dN_dxi[i] * 2/self.dx
                    
                    # Add to element matrices
                    Ke += B.T @ D @ B * detJ
                    
                    # Mass matrix (consistent)
                    N = 0.125 * np.array([
                        (1-xi)*(1-eta)*(1-zeta), (1+xi)*(1-eta)*(1-zeta),
                        (1+xi)*(1+eta)*(1-zeta), (1-xi)*(1+eta)*(1-zeta),
                        (1-xi)*(1-eta)*(1+zeta), (1+xi)*(1-eta)*(1+zeta),
                        (1+xi)*(1+eta)*(1+zeta), (1-xi)*(1+eta)*(1+zeta)
                    ])
                    
                    for a in range(8):
                        for b in range(8):
                            for dof in range(3):
                                Me[3*a+dof, 3*b+dof] += self.rho * N[a] * N[b] * detJ
        
        return Ke, Me
    
    def _get_constitutive_matrix(self):
        """
        Get constitutive matrix for isotropic material
        """
        D = np.zeros((6, 6))
        c = self.lambda_ + 2 * self.mu
        
        D[0, 0] = D[1, 1] = D[2, 2] = c
        D[0, 1] = D[1, 0] = D[0, 2] = D[2, 0] = D[1, 2] = D[2, 1] = self.lambda_
        D[3, 3] = D[4, 4] = D[5, 5] = self.mu
        
        return D
    
    def compute_modes(self, n_modes=10, min_freq=0, max_freq=None, system_min_freq=None, system_max_freq=None):
        """
        Compute modal modes (eigenvalues and eigenvectors) with adaptive k.

        Parameters:
        -----------
        n_modes : int
            Desired number of modes to return.
        min_freq, max_freq : float
            Frequency range to filter modes (Hz). If max_freq is None, no upper bound.
        system_min_freq, system_max_freq : float or None
            Fallback frequency range if not enough modes are found in [min_freq, max_freq].
            If provided, and insufficient modes are found, we will return modes within this
            wider range instead.

        Returns:
        --------
        frequencies : np.ndarray
            Sorted frequencies (Hz) of the selected modes (at most n_modes).
        eigenvectors : np.ndarray 
            Corresponding mode shape matrix (n_dofs x n_modes).
        """
        if self.K is None or self.M is None:
            self.build_system_matrices()
        
        n_dofs = self.K.shape[0]
        if n_dofs <= 1:
            return np.array([]), np.array([])

        # Compute eigenvalues and eigenvectors
        sigma = (2 * np.pi * min_freq) ** 2

        # Maximum number of eigenvalues we are willing to compute (avoid excessive cost)
        max_k = min(n_dofs - 1, 1000)  # cap to avoid memory/time issues

        # Start with a base number: at least n_modes + 20, but not more than max_k
        k = min(max(n_modes + 20, 50), max_k)
        
        # Loop to increase k until we have enough modes in the desired range
        while True:
            # Compute k eigenvalues (lowest frequencies) 
            try:
                eigenvalues, eigenvectors = eigsh(
                    self.K,
                    k=k,
                    M=self.M,
                    sigma=sigma,
                    which='LM',
                    mode='cayley'
                )
            except Exception as e:
                # If eigsh fails (e.g., not enough degrees of freedom), reduce k
                if k > 10:
                    k = max(k // 2, 2)
                    continue
                else:
                    return np.array([]), np.array([])

            # Sort by eigenvalue (ascending, since we want lowest frequencies)
            idx = np.argsort(eigenvalues)
            eigenvalues = eigenvalues[idx]
            eigenvectors = eigenvectors[:, idx]
        
            # Convert to frequencies (Hz)
            freqs = np.sqrt(np.abs(eigenvalues)) / (2 * np.pi)
        
            # Filter by requested frequency range
            mask = (freqs >= min_freq)
            if max_freq is not None:
                mask &= (freqs <= max_freq)

            filtered_freqs = freqs[mask]
            filtered_vectors = eigenvectors[:, mask]

            # If we have enough modes in the requested range, take first n_modes
            if len(filtered_freqs) >= n_modes:
                return filtered_freqs[:n_modes], filtered_vectors[:, :n_modes]

            # If we have exhausted the maximum k, break to fallback
            if k >= max_k:
                break

            # Increase k to get more modes
            k = min(k + 20, max_k)

        # Fallback: not enough modes in requested range: use system-wide fallback range
        if system_min_freq is not None and system_max_freq is not None:
            mask_fallback = (freqs >= system_min_freq) & (freqs <= system_max_freq)
            fallback_freqs = freqs[mask_fallback]
            fallback_vectors = eigenvectors[:, mask_fallback]

            if len(fallback_freqs) >= n_modes:
                return fallback_freqs[:n_modes], fallback_vectors[:, :n_modes]
            else:
                # Still not enough; return what we have in fallback range
                return fallback_freqs, fallback_vectors

        # No fallback or still insufficient: return whatever we have in requested range
        return filtered_freqs, filtered_vectors

    def interpolate_mode_shapes_to_points(self, points: np.ndarray, mode_shapes: np.ndarray, shape_properties: ShapeProperties) -> np.ndarray:
        """
        Interpolate modal displacement magnitudes to arbitrary points (e.g., original mesh vertices).

        Parameters:
        -----------
        points : np.ndarray, shape (N, 3)
            Coordinates of points where to evaluate mode shapes.
        mode_shapes : np.ndarray, shape (n_dofs, n_modes)
            Mode shape matrix (each column is a mode, each row is a DOF).
        shape_properties : ShapeProperties, optional
            Pre‑computed shape properties (avoids recomputation).

        Returns:
        --------
        gains : np.ndarray, shape (N, n_modes)
            Magnitude of displacement at each point for each mode.
        """
        if self.node_index_grid is None:
            raise RuntimeError("Must call build_system_matrices first.")

        N = points.shape[0]
        n_modes = mode_shapes.shape[1]
        gains = np.zeros((N, n_modes), dtype=np.float64)

        for p_idx, pt in enumerate(points):
            # Compute voxel cell indices (clamp to grid)
            # origin is the minimum corner of the grid
            i = (pt[0] - self.origin[0]) / self.dx
            j = (pt[1] - self.origin[1]) / self.dy
            k = (pt[2] - self.origin[2]) / self.dz

            # Clamp to valid range for interpolation
            i = np.clip(i, 0, self.nx - 1)
            j = np.clip(j, 0, self.ny - 1)
            k = np.clip(k, 0, self.nz - 1)

            # Get surrounding node indices
            i0, i1 = int(np.floor(i)), int(np.ceil(i))
            j0, j1 = int(np.floor(j)), int(np.ceil(j))
            k0, k1 = int(np.floor(k)), int(np.ceil(k))

            # Clamp to valid indices (ensuring we stay within grid)
            i0 = max(0, min(i0, self.nx))
            i1 = max(0, min(i1, self.nx))
            j0 = max(0, min(j0, self.ny))
            j1 = max(0, min(j1, self.ny))
            k0 = max(0, min(k0, self.nz))
            k1 = max(0, min(k1, self.nz))

            # Gather node indices for the 8 corners
            corners = [
                (i0, j0, k0), (i1, j0, k0),
                (i0, j1, k0), (i1, j1, k0),
                (i0, j0, k1), (i1, j0, k1),
                (i0, j1, k1), (i1, j1, k1)
            ]
            node_indices = []
            for (ci, cj, ck) in corners:
                nidx = self.node_index_grid[ci, cj, ck]
                if nidx == -1:
                    found = False
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            for dk in [-1, 0, 1]:
                                ni2 = ci + di
                                nj2 = cj + dj
                                nk2 = ck + dk
                                if 0 <= ni2 <= self.nx and 0 <= nj2 <= self.ny and 0 <= nk2 <= self.nz:
                                    alt_idx = self.node_index_grid[ni2, nj2, nk2]
                                    if alt_idx != -1:
                                        node_indices.append(alt_idx)
                                        found = True
                                        break
                            if found:
                                break
                        if found:
                            break
                    if not found:
                        # Point is outside valid domain.
                        break  # will leave gain as 0
                else:
                    node_indices.append(nidx)

            if len(node_indices) != 8:
                # If we couldn't get 8 nodes, set gains to 0 for this point
                continue

            # Compute interpolation weights for trilinear interpolation
            di = i - i0
            dj = j - j0
            dk = k - k0

            # Compute the displacement at the point for each mode.
            for mode_idx in range(n_modes):
                # Gather displacement vectors for the 8 corner nodes
                disp_vectors = []
                for nidx in node_indices:
                    # Each node has 3 DOFs: nidx*3, nidx*3+1, nidx*3+2
                    dx = mode_shapes[nidx*3, mode_idx]
                    dy = mode_shapes[nidx*3+1, mode_idx]
                    dz = mode_shapes[nidx*3+2, mode_idx]
                    disp_vectors.append(np.array([dx, dy, dz]))

                # Trilinear interpolation on each component
                # c000, c100, c010, c110, c001, c101, c011, c111
                c000, c100, c010, c110, c001, c101, c011, c111 = disp_vectors

                # Interpolate x component
                x00 = c000[0] * (1 - di) + c100[0] * di
                x01 = c001[0] * (1 - di) + c101[0] * di
                x10 = c010[0] * (1 - di) + c110[0] * di
                x11 = c011[0] * (1 - di) + c111[0] * di
                x0 = x00 * (1 - dj) + x10 * dj
                x1 = x01 * (1 - dj) + x11 * dj
                x = x0 * (1 - dk) + x1 * dk

                # y component
                y00 = c000[1] * (1 - di) + c100[1] * di
                y01 = c001[1] * (1 - di) + c101[1] * di
                y10 = c010[1] * (1 - di) + c110[1] * di
                y11 = c011[1] * (1 - di) + c111[1] * di
                y0 = y00 * (1 - dj) + y10 * dj
                y1 = y01 * (1 - dj) + y11 * dj
                y = y0 * (1 - dk) + y1 * dk

                # z component
                z00 = c000[2] * (1 - di) + c100[2] * di
                z01 = c001[2] * (1 - di) + c101[2] * di
                z10 = c010[2] * (1 - di) + c110[2] * di
                z11 = c011[2] * (1 - di) + c111[2] * di
                z0 = z00 * (1 - dj) + z10 * dj
                z1 = z01 * (1 - dj) + z11 * dj
                z = z0 * (1 - dk) + z1 * dk

                # Magnitude (Euclidean norm)
                gains[p_idx, mode_idx] = np.sqrt(x*x + y*y + z*z)

        # Shape‑aware stochastic fuzzy logic
        shape_type = shape_properties.shape_type
        confidence = shape_properties.confidence
        centroid = shape_properties.centroid
        bbox = shape_properties.bounding_box
        # Compute vertex features
        # Normalized position in bounding box (range 0..1)
        bbox_min = bbox.min(axis=0)
        bbox_max = bbox.max(axis=0)
        range_ = bbox_max - bbox_min
        range_[range_ == 0] = 1.0  # avoid division by zero
        norm_pos = (points - bbox_min) / range_   # shape (N, 3)

        # Distance from centroid (normalized by max distance)
        dist_from_centroid = np.linalg.norm(points - centroid, axis=1)
        max_dist = np.max(dist_from_centroid) if np.max(dist_from_centroid) > 0 else 1.0
        norm_dist = dist_from_centroid / max_dist  # 0..1

        # Shape‑specific gain adjustment factors
        # Determine shape‑specific function
        if shape_type == ShapeType.SPHERE:
            # Uniform gains
            shape_scale = np.ones(N)
        elif shape_type == ShapeType.PLATE:
            # Use normalized position (0..1), edge if near 0 or 1 in any dimension
            edge_factor = np.minimum(norm_pos, 1 - norm_pos).min(axis=1)  # 0 at edge, 0.5 at center
            # scale = 1 + 0.5 * (1 - edge_factor)  -> higher at edges
            shape_scale = 1.0 + 0.5 * (1.0 - 2.0 * edge_factor)  # range 0.5..1.5
        elif shape_type == ShapeType.BEAM:
            # Use normalized position along the longest dimension
            # Determine which axis is longest
            extents = bbox_max - bbox_min
            longest_axis = np.argmax(extents)
            # position along that axis normalized 0..1
            axis_pos = norm_pos[:, longest_axis]
            # scale: higher at ends (like a simply supported beam)
            shape_scale = 1.0 + 0.4 * np.sin(np.pi * axis_pos)  # 0.6..1.4
        elif shape_type == ShapeType.CUBE:
            # Some variation with distance from center
            shape_scale = 1.0 + 0.2 * (1.0 - norm_dist)
        elif shape_type == ShapeType.CYLINDER:
            # Use distance from centroid in the two radial axes
            # For simplicity, use norm_dist but with a sine wave
            shape_scale = 1.0 + 0.3 * np.sin(2 * np.pi * norm_dist)
        elif shape_type == ShapeType.CONE:
            # Apex vs base
            # Use normalized height (z axis)
            # Assuming cone axis along z, use norm_pos[:,2]
            shape_scale = 1.0 + 0.3 * (norm_pos[:, 2] - 0.5)  # base higher
        else:
            # Irregular: use distance from centroid with random variation
            shape_scale = 1.0 + 0.2 * (1.0 - norm_dist)

        # fixed seed for reproducibility
        rng = np.random.default_rng(seed=42)

        # Confidence‑based stochastic amplitude: low confidence -> more noise
        noise_amplitude = 1.0 - confidence

        for mode_idx in range(n_modes):
            # Mode‑specific variation: add a random phase to the shape scale
            mode_phase = rng.uniform(0, 2 * np.pi)
            # Combine shape_scale with a mode‑dependent sinusoidal factor
            mode_factor = 1.0 + 0.2 * np.sin(2 * np.pi * norm_dist + mode_phase)
            # Apply to gains
            gains[:, mode_idx] *= shape_scale * mode_factor

            # Add stochastic noise
            # Noise proportional to the gain magnitude and shape_scale
            noise = rng.normal(0, noise_amplitude * np.abs(gains[:, mode_idx]))
            gains[:, mode_idx] += noise

        # Ensure gains are non‑negative
        gains = np.maximum(gains, 0.0)

        return gains

    def compute_stochastic_variation_factors(self, n_modes: int, min_freq: float, max_freq: float) -> Dict[str, np.ndarray]:
        """
        Compute stochastic variation factors for modal parameters.

        Parameters
        ----------
        n_modes : int
            Number of modes to generate factors for.

        Returns
        -------
        dict
            Dictionary with keys:
            - 'freq_scale' : np.ndarray, shape (n_modes,)
                Scaling factor for each mode's frequency.
            - 'gain_scale' : np.ndarray, shape (n_modes,)
                Scaling factor for each mode's gain (amplitude).
            - 't60_scale' : np.ndarray, shape (n_modes,)
                Scaling factor for each mode's T60 (decay time).
        """
        # Default uncertainty fractions (relative standard deviation)
        uncertainty_fractions = {
            'E': 0.10,
            'nu': 0.05,
            'rho': 0.05,
            'alpha': 0.20,
            'beta': 0.20
        }

        # Set random generator
        rng = np.random.default_rng()

        # Sample material properties with uncertainty
        # Use lognormal to keep values positive
        def sample_prop(nominal: float, frac: float, low_clip: float = 1e-12) -> float:
            sigma = np.sqrt(np.log(1 + frac**2))
            mu = np.log(nominal) - 0.5 * sigma**2
            return rng.lognormal(mu, sigma)

        E_sampled = sample_prop(self.E, uncertainty_fractions['E'])
        nu_sampled = sample_prop(self.nu, uncertainty_fractions['nu'])
        rho_sampled = sample_prop(self.rho, uncertainty_fractions['rho'])
        alpha_sampled = sample_prop(self.alpha, uncertainty_fractions['alpha'])
        beta_sampled = sample_prop(self.beta, uncertainty_fractions['beta'])

        # Compute frequency scaling: freq ∝ sqrt(E / rho)
        freq_scale = np.sqrt(E_sampled / rho_sampled) / np.sqrt(self.E / self.rho)

        # Compute T60 scaling: T60 ∝ 1 / (damping_ratio * omega)
        nominal_freqs = np.logspace(np.log10(min_freq), np.log10(max_freq), n_modes)
        omega = 2 * np.pi * nominal_freqs

        # Nominal damping ratio
        xi_nom = self.alpha / (2 * omega) + self.beta * omega / 2
        # Sampled damping ratio
        xi_sampled = alpha_sampled / (2 * omega) + beta_sampled * omega / 2

        # T60 scaling: T60 = 6.9078 / (xi * omega)  (since T60 = ln(1000)/(xi*omega))
        # So T60_scale = (xi_nom * omega) / (xi_sampled * omega) = xi_nom / xi_sampled
        t60_scale = xi_nom / xi_sampled

        # Gain scaling: mild random factor (e.g., 1 ± 5‑10%) to account for mode‑shape variations
        # This is not directly derived from material properties, but we add a small stochastic component.
        gain_scale = rng.normal(1.0, 0.05, n_modes)
        gain_scale = np.clip(gain_scale, 0.7, 1.3)

        return {
            'freq_scale': freq_scale * np.ones(n_modes),  # same for all modes (material scaling)
            'gain_scale': gain_scale,
            't60_scale': t60_scale
        }
