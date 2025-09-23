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
from bpy.types import NodeSocket
from bpy.props import IntProperty, FloatProperty, PointerProperty

from ..properties import worldPG

classes = []

class pbrAudioSoundSpeedNodeSocket(NodeSocket):
    bl_idname = 'pbrAudioSoundSpeedNodeSocket'
    bl_label = "pbrAudio Sound Speed Socket"

    def draw(self, context, layout, node, text):
        for world in bpy.data.worlds.values():
            if hasattr(world, 'pbraudio'):
                pbraudio = world.pbraudio
        layout.prop(pbraudio, "sound_speed", text='Sound Speed')

    def draw_color(self, context, node):
        return (0.65, 0.65, 0.65, 1.0) # Light Gray for Float

classes.append(pbrAudioSoundSpeedNodeSocket)

class pbrAudioImpedenceNodeSocket(NodeSocket):
    bl_idname = 'pbrAudioImpedenceNodeSocket'
    bl_label = "pbrAudio Impedence Socket"

    def draw(self, context, layout, node, text):
        for world in bpy.data.worlds.values():
            if hasattr(world, 'pbraudio'):
                pbraudio = world.pbraudio
        layout.prop(pbraudio, "impedence", text='Impedence', slider=True)

    def draw_color(self, context, node):
        return (0.65, 0.65, 0.65, 1.0) # Light Gray for Float

classes.append(pbrAudioImpedenceNodeSocket)

class pbrAudioDensityNodeSocket(NodeSocket):
    bl_idname = 'pbrAudioDensityNodeSocket'
    bl_label = "pbrAudio Temperature Socket"

    def draw(self, context, layout, node, text):
        for world in bpy.data.worlds.values():
            if hasattr(world, 'pbraudio'):
                pbraudio = world.pbraudio
        layout.prop(pbraudio, "density", text='Density', slider=True)

    def draw_color(self, context, node):
        return (0.65, 0.65, 0.65, 1.0) # Light Gray for Float

classes.append(pbrAudioDensityNodeSocket)

class pbrAudioTemperatureNodeSocket(NodeSocket):
    bl_idname = 'pbrAudioTemperatureNodeSocket'
    bl_label = "pbrAudio Temperature Socket"

    def draw(self, context, layout, node, text):
        for world in bpy.data.worlds.values():
            if hasattr(world, 'pbraudio'):
                pbraudio = world.pbraudio
        layout.prop(pbraudio, "temperature", text='Temperature', slider=True)

    def draw_color(self, context, node):
        return (0.65, 0.65, 0.65, 1.0) # Light Gray for Float

classes.append(pbrAudioTemperatureNodeSocket)

#class pbrAudioWorldEnvironmentNodeSocket(NodeSocket):
#    bl_idname = 'pbrAudioWorldEnvironmentNodeSocket'
#    bl_label = "pbrAudio World Environment Socket"

#    # Collection property for the socket
#    items: PointerProperty(
#       name="Environment Collection",
#       type=worldPG.PBRAudioWorldEnvironmentProperties
#    )
#    
#    # Active index for the collection
#    active_index: IntProperty(
#       name="Environment Collection Index",
#       default=0
#    )
#
#    def draw(self, context, layout, node, text):
#       if self.is_output:
#          # Display collection items
#          #template_list("UI_UL_list", "collection_items", self, "items", self, "active_index", rows=3)
#          template_list("UI_UL_list", "collection_items", self, "items", self, "active_index")
#
#          col = layout.column()
#          row = col.row(align=True)
#          row.operator("world.pbraudioenv_add", text="Add", icon='ADD')
#          row.operator("world.pbraudioenv_remove", text="Remove", icon='REMOVE')
#       else:
#          layout.label(text='Input')
#
#    def draw_color(self, context, node):
#        return (1.0, 1.0, 1.0, 1.0) # white for collection data
#
#classes.append(pbrAudioWorldEnvironmentNodeSocket)
