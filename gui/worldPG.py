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
from bpy.props import FloatProperty

classes = []

class PBRAudioWorldProperties(PropertyGroup):
    """World properties for pbrAudio"""
    ambient_sound_level: FloatProperty(
        name="Ambient Sound Level",
        description="Base level of ambient sound",
        default=0.3,
        min=0.0,
        max=1.0
    )

    reverb_time: FloatProperty(
        name="Reverb Time",
        description="Reverberation time in seconds",
        default=1.5,
        min=0.1,
        max=10.0
    )

    air_absorption: FloatProperty(
        name="Air Absorption",
        description="How much air absorbs sound",
        default=0.1,
        min=0.0,
        max=1.0
    )

classes.append(PBRAudioWorldProperties)
