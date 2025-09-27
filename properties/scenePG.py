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
from bpy.props import EnumProperty, IntProperty, BoolProperty, StringProperty

classes = []

class PBRAudioSceneProperties(PropertyGroup):
    def set_sample_rate(self, context):
        if 'LOW' in self.audio_quality:
            self.sample_rate = 24000
        if 'MEDIUM' in self.audio_quality:
            self.sample_rate = 48000
        if 'HIGH' in self.audio_quality:
            self.sample_rate = 96000
        if 'ULTRA' in self.audio_quality:
            self.sample_rate = 192000

    def set_preview_sample_rate(self, context):
        if 'LOW' in self.preview_audio_quality:
            self.preview_sample_rate = 24000
        if 'MEDIUM' in self.preview_audio_quality:
            self.preview_sample_rate = 48000
        if 'HIGH' in self.preview_audio_quality:
            self.preview_sample_rate = 96000
        if 'ULTRA' in self.preview_audio_quality:
            self.preview_sample_rate = 192000

    """Scene properties for pbrAudio"""
    device: EnumProperty(
        name="Device",
        items=[
            ('CPU', "CPU", "Use CPU device for rendering"),
            ('GPU', "GPU Compute", "Use GPU Compute device for rendering, configured in the system tab in the user preferences"),
        ],
        default='CPU'
    )

    audio_quality: EnumProperty(
        name="Audio Quality",
        items=[
            ('LOW', "Low", "Low quality, fast rendering"),
            ('MEDIUM', "Medium", "Balanced quality and speed"),
            ('HIGH', "High", "High quality, slow rendering"),
            ('ULTRA', "Ultra", "Ultra quality, very slow rendering"),
        ],
        default='MEDIUM',
        update=set_sample_rate
    )

    sample_rate: IntProperty(
        name="Sample Rate",
        description="Audio sample rate in Hz",
        default=48000,
        min=12000,
        max=192000
    )

    output_path: StringProperty(
        name="Output",
        description="Path to save audio files",
        subtype='FILE_PATH',
        default='/tmp/'
    )

    file_format: EnumProperty(
        name="File Format",
        items=[
            ('PCM', "WAV: PCM Waveform Audio File Format", "PCM Waveform Audio File Format"),
            ('BWF', "WAV: Broadcast Wave Format", "Broadcast Wave Format"),
        ],
        default='PCM',
    )

    bit_depth: EnumProperty(
        name="Bit Depth",
        items=[
            ('16BIT', "16 bit", "16-bit Depth per Channel"),
            ('24BIT', "24 bit", "24-bit Depth per Channel"),
            ('32BIT', "32 bit", "32-bit Depth per Channel"),
        ],
        default='24BIT',
    )

    enable_graphical_preview: BoolProperty(
        name="Enable Graphical Preview",
        description="Enable graphical preview",
        default=False
    )

    enable_acoustic_preview: BoolProperty(
        name="Enable Acoustic Preview",
        description="Enable acoustic preview",
        default=False
    )

    preview_sample_rate: IntProperty(
        name="Sample Rate For Acoustic Preview",
        description="Audio sample rate in Hz",
        default=48000,
        min=12000,
        max=192000
    )

    preview_audio_quality: EnumProperty(
        name="Audio Quality",
        items=[
            ('LOW', "Low", "Low quality, fast rendering"),
            ('MEDIUM', "Medium", "Balanced quality and speed"),
            ('HIGH', "High", "High quality, slow rendering"),
            ('ULTRA', "Ultra", "Ultra quality, very slow rendering"),
        ],
        default='MEDIUM',
        update=set_preview_sample_rate
    )

    bake: BoolProperty(
        name="bake",
        description="Baked prebaked sound",
        default=False
    )

    prebake: BoolProperty(
        name="bake",
        description="Prebaked sound",
        default=False
    )

    cache_path: StringProperty(
        name="Cache",
        description="Path to save cache files",
        subtype='FILE_PATH',
    )

    cache_status: BoolProperty(
        name="Cache Status",
        description="True if cache is initialized",
        default=False
    )
classes.append(PBRAudioSceneProperties)
