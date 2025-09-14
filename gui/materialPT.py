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

class PBRAUDIO_PT_material_panel(Panel):
    """Panel for pbrAudio material settings"""
    bl_label = "pbrAudio Material"
    bl_idname = "PBRAUDIO_PT_material_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO' and context.material

    def draw(self, context):
        layout = self.layout
        mat = context.material

        if not mat.pbraudio:
            layout.operator("material.pbraudio_init", text="Initialize pbrAudio Material")
        else:
            layout.prop(mat.pbraudio, "acoustic_properties")
            layout.prop(mat.pbraudio, "sound_absorption")

classes.append(PBRAUDIO_PT_material_panel)
