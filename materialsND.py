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
from bpy.props import StringProperty

classes = []

class AudioMaterialNode(Node):
    """Base class for all audio material nodes"""
    bl_idname = 'AudioMaterialNode'
    bl_label = "Audio Material Node"
    bl_icon = 'SOUND'

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'AudioMaterialNodeTree'

classes.append(AudioMaterialNode)

# Example node types
class AudioInputNode(AudioMaterialNode):
    """Audio input node"""
    bl_idname = 'AudioInputNode'
    bl_label = "Audio Input"

    audio_file: StringProperty(
        name="Audio File",
        description="Path to audio file",
        subtype='FILE_PATH'
    )

    def init(self, context):
        self.outputs.new('AudioMaterialNodeSocket', "Audio Signal")

classes.append(AudioInputNode)

class AudioMaterialOutputNode(AudioMaterialNode):
    """Audio material output node"""
    bl_idname = 'AudioMaterialOutputNode'
    bl_label = "Material Output"

    def init(self, context):
        self.inputs.new('AudioMaterialNodeSocket', "Acoustic Properties")
        self.inputs.new('AudioMaterialNodeSocket', "Reflectivity")
        self.inputs.new('AudioMaterialNodeSocket', "Absorption")

classes.append(AudioMaterialOutputNode)
