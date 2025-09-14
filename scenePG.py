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
from bpy.props import EnumProperty, IntProperty, BoolProperty

classes = []

class PBRAudioSceneProperties(PropertyGroup):
    """Scene properties for pbrAudio"""
    audio_quality: EnumProperty(
        name="Audio Quality",
        items=[
            ('LOW', "Low", "Low quality, fast rendering"),
            ('MEDIUM', "Medium", "Balanced quality and speed"),
            ('HIGH', "High", "High quality, slow rendering"),
            ('ULTRA', "Ultra", "Ultra quality, very slow rendering"),
        ],
        default='MEDIUM'
    )

    sample_rate: IntProperty(
        name="Sample Rate",
        description="Audio sample rate in Hz",
        default=44100,
        min=8000,
        max=192000
    )

    enable_realtime_audio: BoolProperty(
        name="Realtime Audio",
        description="Enable realtime audio processing",
        default=False
    )

classes.append(PBRAudioSceneProperties)
