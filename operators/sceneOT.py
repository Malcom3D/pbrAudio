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
#from bpy.props import StringProperty
from bpy.types import Operator

classes = []

class PBRAUDIO_OT_bake(Operator):
    bl_idname = "scene.pbraudio_bake"
    bl_label = "pbrAudio bake"
    bl_description = "Bake prebaked sound with dynamics and animation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if hasattr(scene.pbraudio, 'prebake'):
            if scene.pbraudio.prebake and not scene.bake:
                scene.pbraudio.bake = True
        self.report({'INFO'}, f"pbrAudio PreBaked sound Baked")
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_bake)

class PBRAUDIO_OT_prebake(Operator):
    bl_idname = "scene.pbraudio_prebake"
    bl_label = "Prebake sound from objects physics"
    bl_description = "Prebake sound"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if hasattr(scene.pbraudio, 'prebake'):
            if not scene.pbraudio.prebake:
                scene.pbraudio.prebake = True
        self.report({'INFO'}, f"pbrAudio sound from object physic PreBaked")
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_prebake)
