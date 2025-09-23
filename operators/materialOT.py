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

class PBRAUDIO_OT_material_add(Operator):
    bl_idname = "material.pbraudio_add"
    bl_label = "New pbrAudio material"
    bl_description = "Create a add audio material node tree"
    bl_options = {'REGISTER', 'UNDO'}

    name: StringProperty(
        name="Name",
        description="Name of the pbrAudio node tree",
        default="AudioMaterial"
    )

    def execute(self, context):
        # Create new pbrAudio node tree
        nodetree = bpy.data.node_groups.new(self.name, 'AudioMaterialNodeTree')
        
        # Link to active object if available
        if context.active_object and context.active_object.pbraudio:
            context.active_object.pbraudio.nodetree = nodetree
        
        self.report({'INFO'}, f"Created pbrAudio node tree: {nodetree.name}")
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_material_add)
