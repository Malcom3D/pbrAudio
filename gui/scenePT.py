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

classes = []

class PBRAUDIO_PT_prebake_panel(Panel):
    """Panel for pbrAudio prebake settings"""
    bl_label = "PbrAudio PreBake"
    bl_idname = "PBRAUDIO_PT_prebake_preview_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        # operator button
        layout.operator('scene.pbraudio_prebake')

classes.append(PBRAUDIO_PT_prebake_panel)

class PBRAUDIO_PT_bake_panel(Panel):
    """Panel for pbrAudio bake settings"""
    bl_label = "PbrAudio Bake"
    bl_idname = "PBRAUDIO_PT_bake_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'
        
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        
        scene = context.scene
        
        # operator button
        layout.operator('scene.pbraudio_bake')

classes.append(PBRAUDIO_PT_bake_panel)

class PBRAUDIO_PT_cache_panel(Panel):
    """Panel for pbrAudio cache path and settings"""
    bl_label = "PbrAudio Cache"
    bl_idname = "PBRAUDIO_PT_cache_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        layout.enabled = not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "cache_path")

classes.append(PBRAUDIO_PT_cache_panel)
