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
from bpy.props import StringProperty
from bpy.types import Operator

classes = []

class PBRAUDIO_OT_world_material_add(Operator):
    bl_idname = "world.pbraudio_add"
    bl_label = "New pbrAudio world material"
    bl_description = "Create a new world audio material node tree"
    bl_options = {'REGISTER', 'UNDO'}

    name: StringProperty(
        name="Name",
        description="Name of the pbrAudio world node tree",
        default="AcousticWorld"
    )

    def execute(self, context):
        world = context.world
        if world and world.pbraudio:
            # Create new pbrAudio World node tree
            nodetree = bpy.data.node_groups.new(self.name, 'AudioWorldNodeTree')
            # Link to active acoustic domain world if available
            world.pbraudio.nodetree = nodetree
        
        self.report({'INFO'}, f"Created pbrAudio World node tree: {nodetree.name}")
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_world_material_add)

# Operators for managing the world environment collection
class PBRAUDIO_OT_environment_item_add(Operator):
    bl_idname = "world.pbraudioenv_add"
    bl_label = "Add World Environment Collection Item"
    
    @classmethod
    def poll(cls, context):
        return context.space_data.node_tree == 'AudioWorldNodeTree'
    
    def execute(self, context):
        node = context.active_node
        if node and hasattr(node, 'outputs'):
            for socket in node.outputs:
                if hasattr(socket, 'items'):
                    item = socket.items.add()
                    item.name = f"Environment {len(socket.items)}"
                    socket.active_index = len(socket.items) - 1
                    break
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_environment_item_add)

class PBRAUDIO_OT_environment_item_remove(Operator):
    bl_idname = "world.pbraudioenv_remove"
    bl_label = "Remove World Environment Collection Item"
    
    @classmethod
    def poll(cls, context):
        return context.space_data.node_tree == 'AudioWorldNodeTree'
    
    def execute(self, context):
        node = context.active_node
        if node and hasattr(node, 'outputs'):
            for socket in node.outputs:
                if hasattr(socket, 'items') and socket.items:
                    if socket.active_index >= 0 and socket.active_index < len(socket.items):
                        socket.items.remove(socket.active_index)
                        socket.active_index = min(socket.active_index, len(socket.items) - 1)
                    break
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_environment_item_remove)
