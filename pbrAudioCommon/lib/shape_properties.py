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
from enum import Enum

class ShapeType(Enum):
    """Enum for primitive shape classification."""
    SPHERE = "sphere"
    CUBE = "cube"
    CYLINDER = "cylinder"
    PLATE = "plate"
    BEAM = "beam"
    TORUS = "torus"
    CONE = "cone"
    PYRAMID = "pyramid"
    IRREGULAR = "irregular"

@dataclass
class ShapeProperties:
    """Properties of a classified shape."""
    shape_type: ShapeType
    dimensions: Dict[str, float]  # e.g., {'radius': 0.1, 'height': 0.2}
    volume: float
    surface_area: float
    aspect_ratio: float
    compactness: float
    confidence: float  # 0-1 confidence in classification
    bounding_box: np.ndarray  # 8x3 bounding box vertices
    centroid: np.ndarray  # 3D centroid
