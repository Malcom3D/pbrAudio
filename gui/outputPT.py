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
from bpy.types import Panel
from bpy.types import RENDER_MT_framerate_presets

classes = []

class PBRAUDIO_PT_format_panel(Panel):
    """Panel for pbrAudio Format settings"""
    bl_label = "Format"
    bl_idname = "PBRAUDIO_PT_format_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        layout.prop(scene.pbraudio, "audio_quality")
        col = layout.column(align=True)
        col.prop(scene.pbraudio, "sample_rate", text="Sample Rate")
        layout.prop(scene.pbraudio, "bit_depth")

classes.append(PBRAUDIO_PT_format_panel)

class PBRAUDIO_PT_output_panel(Panel):
    """Panel for pbrAudio Format settings"""
    bl_label = "Output"
    bl_idname = "PBRAUDIO_PT_output_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        layout.prop(scene.pbraudio, "output_path")
        layout.prop(scene.pbraudio, "file_format")

classes.append(PBRAUDIO_PT_output_panel)

class PBRAUDIO_PT_frame_range_panel(Panel):
    """Panel for pbrAudio Frame Range settings"""
    bl_label = "Frame Range"
    bl_idname = "PBRAUDIO_PT_frame_range_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        col = layout.column(align=True)
        col.enabled = False
        col.prop(scene, "frame_start", text="Frame Start")
        col.prop(scene, "frame_end", text="End")
        col.prop(scene, "fps", text="FPS")
        col.prop(scene, "fps_base", text="FPS BASE")

classes.append(PBRAUDIO_PT_frame_range_panel)

class PBRAUDIO_PT_metadata_panel(Panel):
    """Panel for pbrAudio Frame Range settings"""
    bl_label = "Metadata"
    bl_idname = "PBRAUDIO_PT_metadata_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        layout.label(text="Metadata Text")

classes.append(PBRAUDIO_PT_metadata_panel)
