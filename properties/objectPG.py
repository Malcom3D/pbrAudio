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

import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, PointerProperty, EnumProperty

from ..nodetrees import materialsNT

classes = []

class PBRAudioObjectProperties(PropertyGroup):

    """Material properties for pbrAudio"""
    nodetree: PointerProperty(
        name="NodeTree",
        type=materialsNT.AudioMaterialNodeTree
    )

    """Source properties for pbrAudio"""
    source: PointerProperty(
        name="SoundSource",
        type=bpy.types.Sound,
        description="Select the sound for the source"
    )

    source_type: EnumProperty(
        name="Type",
        items=[
            ('SPHERE', "Spheric", "Spheric wave sound source"),
            ('PLANE', "Plane", "Plane wave sound source"),
        ],
        default='SPHERE'
    )

    """Output properties for pbrAudio"""
    output: BoolProperty(
        name="SoundOutput",
        description="Select the sound for the source",
        default=False
    )

    output_type: EnumProperty(
        name="Type",
        items=[
            ('MONO', "Mono", "Mono sound output"),
            ('AMBI', "Ambisonic", "Ambisonic sound output"),
        ],
        default='MONO'
    )

    ambisonic_order: EnumProperty(
        name="Order",
        items=[
            ('1', "First", "First order"),
            ('2', "Second", "Second order"),
            ('3', "Third", "Third order"),
        ],
        default='1'
    )

classes.append(PBRAudioObjectProperties)
