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
from bpy.utils import register_class, unregister_class
from nodeitems_utils import NodeCategory, NodeItem, register_node_categories, unregister_node_categories

classes = []

from . import materialsND, worldND

for mod in (materialsND, worldND):
    classes += mod.classes

class WorldNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'AudioWorldNodeTree'

world_node_categories = [
    WorldNodeCategory("WORLD_NODES", "World", items=[
        NodeItem("AudioEnvironmentNode"),
        NodeItem("AudioWorldOutputNode"),
    ]),
]

class MaterialNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'AudioMaterialNodeTree'

material_node_categories = [
    MaterialNodeCategory("MATERIAL_NODES", "Material", items=[
        NodeItem("AudioInputNode"),
        NodeItem("AudioMaterialOutputNode"),
    ]),
]

def register():
    for cls in classes:
        register_class(cls)
    register_node_categories("WORLD", world_node_categories)
    register_node_categories("MATERIAL", material_node_categories)

def unregister():
    unregister_node_categories("WORLD_NODE")
    unregister_node_categories("MATERIAL_NODE")
    for cls in reversed(classes):
        unregister_class(cls)
