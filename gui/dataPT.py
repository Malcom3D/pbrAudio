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

class PBRAUDIO_PT_data_panel(Panel):
    """Panel for pbrAudio sound I/O settings"""
    bl_label = 'Sound I/O'
    bl_idname = 'PBRAUDIO_PT_data_panel'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO' and context.object.type == 'EMPTY' or context.object.type == 'CAMERA'

    def draw(self, context):
        layout = self.layout
        object = context.object
        snode = object.pbraudio

        layout.prop(object.pbraudio, "output")

        if not object.pbraudio.output and object.type == 'EMPTY':
            # Object is a Sound Source
            layout.prop(object.pbraudio, "source_type")
            layout.template_ID(snode, "source", new="sound.open_mono")
            # use gizmo shape - text editor -> templates -> gizmo_custom_geometry
            if object.pbraudio.source and object.pbraudio.source_type == 'SPHERE':
                object.empty_display_type = 'SPHERE'
                object.empty_display_size = 0.25
            elif object.pbraudio.source and object.pbraudio.source_type == 'PLANE':
                object.empty_display_type = 'CUBE'
                object.empty_display_size = 0.25
        else:
            # Object is a Sound Output
            layout.prop(object.pbraudio, "output_type")
            if object.pbraudio.output_type == 'AMBI':
                layout.prop(object.pbraudio, "ambisonic_order")

classes.append(PBRAUDIO_PT_data_panel)
