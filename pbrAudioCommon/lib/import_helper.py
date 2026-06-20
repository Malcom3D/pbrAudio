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

"""
Helper module to manage numpy imports from alternative packages path
"""
import sys
import os
import importlib

# Path to the custom numpy installation
ALT_PKGS_PATH = '../alt_pkgs'

def import_pbr_audio_numpy():
    """
    Import numpy from the alternative packages path.
    Returns the numpy module with the correct version.
    """
    # Remove any previously imported numpy to force reload
    if 'numpy' in sys.modules:
        del sys.modules['numpy']
        del np

    if ALT_PKGS_PATH not in sys.path:
        sys.path.insert(0, ALT_PKGS_PATH)
    
    import numpy as np
    return np

# Global numpy instance for the pbrAudio suite
np = import_pbr_audio_numpy()
