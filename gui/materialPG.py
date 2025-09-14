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
from bpy.props import FloatVectorProperty, FloatProperty

classes = []

class PBRAudioMaterialProperties(PropertyGroup):
    """Material properties for pbrAudio"""
    acoustic_properties: FloatVectorProperty(
        name="Acoustic Properties",
        description="Material acoustic characteristics",
        size=3,
        default=(0.5, 0.5, 0.5),
        min=0.0,
        max=1.0
    )

    sound_absorption: FloatProperty(
        name="Sound Absorption",
        description="How much sound the material absorbs",
        default=0.5,
        min=0.0,
        max=1.0
    )

    reflection_strength: FloatProperty(
        name="Reflection Strength",
        description="Strength of sound reflections",
        default=0.7,
        min=0.0,
        max=1.0
    )

classes.append(PBRAudioMaterialProperties)
