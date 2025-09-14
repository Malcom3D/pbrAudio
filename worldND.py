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
from bpy.types import Node
from bpy.props import FloatProperty

classes = []

class AudioWorldNode(Node):
    """Base class for all audio world nodes"""
    bl_idname = 'AudioWorldNode'
    bl_label = "Audio World Node"
    bl_icon = 'WORLD'

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'AudioWorldNodeTree'

classes.append(AudioWorldNode)

# Example node types
class AudioEnvironmentNode(AudioWorldNode):
    """Audio environment properties node"""
    bl_idname = 'AudioEnvironmentNode'
    bl_label = "Environment"

    air_density: FloatProperty(
        name="Air Density",
        default=1.2,
        min=0.1,
        max=5.0
    )

    temperature: FloatProperty(
        name="Temperature",
        default=20.0,
        min=-50.0,
        max=50.0
    )

    def init(self, context):
        self.outputs.new('AudioWorldNodeSocket', "Environment Properties")

classes.append(AudioEnvironmentNode)

class AudioWorldOutputNode(AudioWorldNode):
    """Audio world output node"""
    bl_idname = 'AudioWorldOutputNode'
    bl_label = "World Output"

    def init(self, context):
        self.inputs.new('AudioWorldNodeSocket', "Global Acoustics")
        self.inputs.new('AudioWorldNodeSocket', "Reverb Properties")
        self.inputs.new('AudioWorldNodeSocket', "Ambient Sound")

classes.append(AudioWorldOutputNode)
