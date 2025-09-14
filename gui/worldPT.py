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

class PBRAUDIO_PT_world_panel(Panel):
    """Panel for pbrAudio world settings"""
    bl_label = "pbrAudio World"
    bl_idname = "PBRAUDIO_PT_world_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO' and context.world

    def draw(self, context):
        layout = self.layout
        world = context.world

        if not world.pbraudio:
            layout.operator("world.pbraudio_init", text="Initialize pbrAudio World")
        else:
            layout.prop(world.pbraudio, "ambient_sound_level")
            layout.prop(world.pbraudio, "reverb_time")

classes.append(PBRAUDIO_PT_world_panel)
