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

__version__ = "0.2.36"
__author__ = "Malcom3D"
__description__ = "Common core classes and library"

import os, sys
import numpy as np

decimals = 18
np.set_printoptions(precision=decimals, floatmode='fixed', threshold=np.inf)

from .core.entity_manager import EntityManager
from .lib.functions import *

__all__ = [
    'EntityManager',
    '_mesh_to_obj',
    '_acoustic_domain_mesh',
    '_load_mesh',
    '_load_pose',
    '_generate_band_frequencies',
    '_euler_to_rotation_matrix',
    '_parse_lib',
    '_update_status',
    '_cartesian_to_spherical',
    '_trilinear_interpolate',
    '_degrees_to_radians',
    '_compute_rayleigh_damping',
    '_mono_to_bands'
]
