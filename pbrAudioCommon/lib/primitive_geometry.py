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
import trimesh
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from scipy.spatial import ConvexHull
from scipy.spatial.distance import pdist

from ..lib.shape_properties import ShapeType, ShapeProperties

@dataclass
class PrimitiveGeometry:
    """
    Classify mesh geometry into primitive shapes and extract properties
    for approximate modal model generation.
    """
    
    def classify(self, vertices: np.ndarray, faces: np.ndarray) -> ShapeProperties:
        """
        Classify a mesh into a primitive shape type.
        
        Parameters:
        -----------
        vertices : np.ndarray
            Vertex positions (N, 3)
        faces : np.ndarray
            Face indices (M, 3)
            
        Returns:
        --------
        ShapeProperties
            Classified shape properties
        """
        # Create trimesh object for analysis
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        
        # Basic properties
        volume = mesh.volume
        surface_area = mesh.area
        centroid = mesh.centroid
        bounds = mesh.bounds
        extents = mesh.extents  # Size in each dimension
        
        # Bounding box
        bbox = mesh.bounding_box.vertices
        
        # Aspect ratios
        sorted_extents = np.sort(extents)
        aspect_ratio_1 = sorted_extents[2] / sorted_extents[0] if sorted_extents[0] > 0 else 1.0
        aspect_ratio_2 = sorted_extents[2] / sorted_extents[1] if sorted_extents[1] > 0 else 1.0
        
        # Compactness (sphere = 1.0, less compact = smaller)
        compactness = self._compute_compactness(volume, surface_area)
        
        # Sphericity
        sphericity = self._compute_sphericity(vertices, centroid)
        
        # Principal axes and moments of inertia
        inertia_tensor = mesh.moment_inertia
        principal_moments = np.linalg.eigvalsh(inertia_tensor)
        sorted_moments = np.sort(principal_moments)
        
        # Moment ratios
        moment_ratio_1 = sorted_moments[2] / sorted_moments[0] if sorted_moments[0] > 0 else 1.0
        moment_ratio_2 = sorted_moments[2] / sorted_moments[1] if sorted_moments[1] > 0 else 1.0
        
        # Classify based on features
        shape_type, confidence, dimensions = self._classify_shape(extents=extents, sorted_extents=sorted_extents, aspect_ratio_1=aspect_ratio_1, aspect_ratio_2=aspect_ratio_2, compactness=compactness, sphericity=sphericity, moment_ratio_1=moment_ratio_1, moment_ratio_2=moment_ratio_2, volume=volume, surface_area=surface_area, vertices=vertices, centroid=centroid)
        
        return ShapeProperties(shape_type=shape_type, dimensions=dimensions, volume=volume, surface_area=surface_area, aspect_ratio=aspect_ratio_1, compactness=compactness, confidence=confidence, bounding_box=bbox, centroid=centroid)
    
    def _compute_compactness(self, volume: float, surface_area: float) -> float:
        """
        Compute compactness (isoperimetric quotient).
        Sphere has compactness = 1.0
        
        Compactness = 36π * V² / S³
        """
        if surface_area <=  0 or volume <= 0:
            return 0.0
        
        compactness = (36 * np.pi * volume**2) / (surface_area**3)
        return float(np.clip(compactness, 0.0, 1.0))
    
    def _compute_sphericity(self, vertices: np.ndarray, centroid: np.ndarray) -> float:
        """
        Compute sphericity based on radial distance distribution.
        """
        distances = np.linalg.norm(vertices - centroid, axis=1)
        
        if len(distances) < 3 or np.std(distances) == 0:
            return 0.0
        
        # Coefficient of variation of radial distances
        cv = np.std(distances) / np.mean(distances)
        
        # Sphericity = 1 - cv (normalized)
        sphericity = 1.0 - cv
        return float(np.clip(sphericity, 0.0, 1.0))
    
    def _classify_shape(self, extents: np.ndarray, sorted_extents: np.ndarray, aspect_ratio_1: float, aspect_ratio_2: float, compactness: float, sphericity: float, moment_ratio_1: float, moment_ratio_2: float, volume: float, surface_area: float, vertices: np.ndarray, centroid: np.ndarray) -> Tuple[ShapeType, float, Dict[str, float]]:
        """
        Classify shape based on geometric features.
        
        Returns:
            (shape_type, confidence, dimensions)
        """
        dimensions = {}
        
        # Check for sphere-like objects
        if compactness > 0.8 and sphericity > 0.85:
            radius = (3 * volume / (4 * np.pi)) ** (1/3)
            dimensions = {'radius': radius}
            return ShapeType.SPHERE, min(compactness, sphericity), dimensions
        
        # Check for cube-like objects
        if (abs(aspect_ratio_1 - 1.0) < 0.3 and 
            abs(aspect_ratio_2 - 1.0) < 0.3 and
            compactness > 0.5):
            side = extents[0]  # Approximate side length
            dimensions = {'side': side}
            return ShapeType.CUBE, 0.8, dimensions
        
        # Check for plate-like objects (thin in one dimension)
        if aspect_ratio_1 > 3.0 and compactness < 0.5:
            thickness = sorted_extents[0]
            width = sorted_extents[1]
            length = sorted_extents[2]
            dimensions = {
                'length': length,
                'width': width,
                'thickness': thickness
            }
            return ShapeType.PLATE, 0.7, dimensions
        
        # Check for beam-like objects (long in one dimension)
        if aspect_ratio_1 > 2.0 and aspect_ratio_2 > 1.5:
            # Check if it's a cylinder (circular cross-section)
            cross_section_aspect = sorted_extents[1] / sorted_extents[0] if sorted_extents[0] > 0 else 1.0
            
            if cross_section_aspect < 1.3:  # Near-circular cross-section
                radius = sorted_extents[00] / 2
                height = sorted_extents[2]
                dimensions = {
                    'radius': radius,
                    'height': height
                }
                return ShapeType.CYLINDER, 0.75, dimensions
            else:
                width = sorted_extents[0]
                depth = sorted_extents[1]
                length = sorted_extents[2]
                dimensions = {
                    'length': length,
                    'width': width,
                    'depth': depth
                }
                return ShapeType.BEAM, 0.7, dimensions
        
        # Check for cone-like objects
        # (Pyramidal shape with circular base approximation)
        if self._is_cone_like(vertices, centroid):
            height = extents[2] - extents[0]
            base_radius = np.max(np.linalg.norm(vertices[vertices[:, 2] < centroid[2]] - centroid, axis=1))
            dimensions = {
                'height': height,
                'base_radius': base_radius
            }
            return ShapeType.CONE, 0.6, dimensions
        
        # Check for pyramid-like objects
        if self._is_pyramid_like(vertices, centroid):
            height = extents[2] - extents[0]
            base_width = extents[1] - extents[0]
            base_length = extents[2] - extents[0]
            dimensions = {
                'height': height,
                'base_width': base_width,
                'base_length': base_length
            }
            return ShapeType.PYRAMID, 0.5, dimensions
        
        # Default: irregular shape
        dimensions = {
            'extent_x': extents[0],
            'extent_y': extents[1],
            'extent_z': extents[2]
        }
        return ShapeType.IRREGULAR, 0.3, dimensions
    
    def _is_cone_like(self, vertices: np.ndarray, centroid: np.ndarray) -> bool:
        """Check if mesh is cone-like."""
        # Check if vertices converge to a point
        # Simple heuristic: check if there's a significant reduction in cross-section
        # along one axis
        z_values = vertices[:, 2]
        z_min, z_max = np.min(z_values), np.max(z_values)
        
        if z_max - z_min < 0.01:
            return False
        
        # Sample cross-sections at different heights
        n_sections = 5
        section_areas = []
        
        for i in range(n_sections):
            z_level = z_min + (z_max - z_min) * i / (n_sections - 1)
            mask = np.abs(z_values - z_level) < (z_max - z_min) / (n_sections * 2)
            
            if np.sum(mask) >= 3:
                section_vertices = vertices[mask]
                # Approximate area using convex hull
                try:
                    hull = ConvexHull(section_vertices[:, :2])
                    section_areas.append(hull.volume)
                except:
                    section_areas.append(0)
            else:
                section_areas.append(0)
        
        if len(section_areas) < 2 or max(section_areas) == 0:
            return False
        
        # Check for monotonic decrease in area (cone-like)
        normalized_areas = np.array(section_areas) / max(section_areas)
        decreasing = all(normalized_areas[i] >= normalized_areas[i+1] for i in range(len(normalized_areas)-1))
        
        return decreasing
    
    def _is_pyramid_like(self, vertices: np.ndarray, centroid: np.ndarray) -> bool:
        """Check if mesh is pyramid-like."""
        # Similar to cone but with rectangular cross-section
        # Check for planar base and converging sides
        # This is a simplified check
        hull = ConvexHull(vertices)
        
        # Count vertices in hull
        n_hull_vertices = len(hull.vertices)
        
        # Pyramid typically has 5 vertices (square base + apex)
        # or 4 vertices (triangular base + apex)
        return 4 <= n_hull_vertices <= 6
    
    def get_effective_radius(self, shape_properties: ShapeProperties) -> float:
        """
        Get effective radius for modal analysis.
        
        For irregular shapes, returns equivalent sphere radius.
        """
        if 'radius' in shape_properties.dimensions:
            return shape_properties.dimensions['radius']
        elif 'side' in shape_properties.dimensions:
            return shape_properties.dimensions['side'] / 2
        elif 'height' in shape_properties.dimensions and 'radius' in shape_properties.dimensions:
            # For cylinder/cone, use equivalent radius
            return (3 * shape_properties.volume / (4 * np.pi)) ** (1/3)
        else:
            # Equivalent sphere radius from volume
            return (3 * shape_properties.volume / (4 * np.pi)) ** (1/3)
    
    def get_characteristic_dimension(self, shape_properties: ShapeProperties) -> float:
        """
        Get characteristic dimension for frequency scaling.
        """
        if shape_properties.shape_type == ShapeType.SPHERE:
            return shape_properties.dimensions.get('radius', 0.1)
        elif shape_properties.shape_type == ShapeType.CUBE:
            return shape_properties.dimensions.get('side', 0.1)
        elif shape_properties.shape_type == ShapeType.CYLINDER:
            return max(shape_properties.dimensions.get('radius', 0.05), 
                      shape_properties.dimensions.get('height', 0.1))
        elif shape_properties.shape_type == ShapeType.PLATE:
            return shape_properties.dimensions.get('thickness', 0.01)
        elif shape_properties.shape_type == ShapeType.BEAM:
            return shape_properties.dimensions.get('length', 0.1)
        else:
            return (3 * shape_properties.volume / (4 * np.pi)) ** (1/3)

