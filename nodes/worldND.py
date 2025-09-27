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
from numpy import sqrt
from bpy.types import Node
from bpy.props import FloatProperty

classes = []

class pbrAudioWorldOutputNode(Node):
    """Audio world output node"""
    bl_idname = 'pbrAudioWorldOutputNode'
    bl_label = "Acoustic World Output"

    def init(self, context):
        self.inputs.new('pbrAudioSoundSpeedNodeSocket', "Sound Speed")
        self.inputs.new('pbrAudioImpedenceNodeSocket', "Impedence")
#        self.inputs.new('pbrAudioWorldEnvironmentNodeSocket', "Environment")

classes.append(pbrAudioWorldOutputNode)

class pbrAudioSoundSpeedNode(Node):
    """Acoustic sound speed properties node"""
    bl_idname = 'pbrAudioSoundSpeedNode'
    bl_label = "Sound speed Parameters"

#    def compute_speed(self, context):
#       for world in bpy.data.worlds.values():
#          if hasattr(world, 'pbraudio'):
#             pbraudio = world.pbraudio
#
#       if pbraudio.type == 'GAS':
#          pbraudio.sound_speed = sqrt((self.C_p/self.C_v)*(self.R_0/self.M)*(pbraudio.temperature+273.15))
#       elif pbraudio.type == 'LIQUID':
#          pbraudio.sound_speed = sqrt(self.K/pbraudio.density)
#       elif pbraudio.type == 'SOLID':
#          pbraudio.sound_speed = sqrt(self.E/pbraudio.density)
#
#       if self.outputs['Sound Speed'].is_linked:
#          self.outputs['Sound Speed'].sound_speed = pbraudio.sound_speed
#
#    C_p: FloatProperty(
#        name="Specific heat at constant pressure",
#        default=7.0,
#        update=compute_speed
#    )
#
#    C_v: FloatProperty(
#        name="Specific heat at constant volume",
#        default=5.0,
#        update=compute_speed
#    )
#
#    R_0: FloatProperty(
#        name="Gas constant",
#        default=8.31446261815324,
#        update=compute_speed
#    )
#
#    M: FloatProperty(
#        name="Molar mass",
#        default=0.0289645,
#        update=compute_speed
#    )
#
#    K: FloatProperty(
#        name="Bulk modulus",
#        default=0.0,
#        update=compute_speed
#    )
#
#    E: FloatProperty(
#        name="Young modulus",
#        default=0.0,
#        update=compute_speed
#    )
#
    def init(self, context):
        self.outputs.new('pbrAudioSoundSpeedNodeSocket', "Sound Speed")
        self.inputs.new('pbrAudioTemperatureNodeSocket', "Temperature in Celsius degree")
        self.inputs.new('pbrAudioDensityNodeSocket', "Density")

    def draw_buttons(self, context, layout):
        for world in bpy.data.worlds.values():
            if hasattr(world, 'pbraudio'):
                pbraudio = world.pbraudio

        layout.prop(pbraudio, "type", text='Type')

        if pbraudio.type == 'GAS':
            layout.prop(pbraudio, "C_p", text='Cp: Specific heat at constant pressure', slider=True)
            layout.prop(pbraudio, "C_v", text='Cv: Specific heat at constant volume', slider=True)
            layout.prop(pbraudio, "R_0", text='Ro: Gas constant', slider=True)
            layout.prop(pbraudio, "M", text='M: Molar Mass', slider=True)
        if pbraudio.type == 'LIQUID':
            layout.prop(pbraudio, "K", text='K: Bulk modulus', slider=True)
        if pbraudio.type == 'SOLID':
            layout.prop(pbraudio, "E", text='E: Young\'s modulus', slider=True)

#        if pbraudio.type == 'GAS':
#            layout.prop(self, "C_p", text='Cp: Specific heat at constant pressure', slider=True)
#            layout.prop(self, "C_v", text='Cv: Specific heat at constant volume', slider=True)
#            layout.prop(self, "R_0", text='Ro: Gas constant', slider=True)
#            layout.prop(self, "M", text='M: Molar Mass', slider=True)
#        if pbraudio.type == 'LIQUID':
#            layout.prop(self, "K", text='K: Bulk modulus', slider=True)
#        if pbraudio.type == 'SOLID':
#            layout.prop(self, "E", text='E: Young\'s modulus', slider=True)

    def draw_label(self):
        return "Acoustic Medium"

    def update(self):
        pass

    def free(self):
        pass

classes.append(pbrAudioSoundSpeedNode)

class pbrAudioImpedenceNode(Node):
    """Acoustic impedence properties node"""
    bl_idname = 'pbrAudioImpedenceNode'
    bl_label = "Acoustic Impedence Parameters"

    def init(self, context):
        self.outputs.new('pbrAudioImpedenceNodeSocket', "Impedence")
        self.inputs.new('pbrAudioSoundSpeedNodeSocket', "Sound Speed")
        self.inputs.new('pbrAudioDensityNodeSocket', "Density")

    def draw_buttons(self, context, layout):
        pass

    def draw_label(self):
        return "Acoustic Impedence"

    def update(self):
        pass

    def free(self):
        pass

classes.append(pbrAudioImpedenceNode)

class pbrAudioDensityNode(Node):
    """Acoustic density properties node"""
    bl_idname = 'pbrAudioDensityNode'
    bl_label = "Acoustic Density Parameters"

    def init(self, context):
        self.outputs.new('pbrAudioDensityNodeSocket', "Density")

    def draw_buttons(self, context, layout):
        pass

    def draw_label(self):
        return "Density"

    def update(self):
        pass

    def free(self):
        pass

classes.append(pbrAudioDensityNode)

class pbrAudioTemperatureNode(Node):
    """Acoustic temperature properties node"""
    bl_idname = 'pbrAudioTemperatureNode'
    bl_label = "Acoustic Temperature Parameters"

    def init(self, context):
        self.outputs.new('pbrAudioTemperatureNodeSocket', "Temperature in Celsius degree")

    def draw_buttons(self, context, layout):
        pass

    def draw_label(self):
        return "Temperature"

    def update(self):
        pass

    def free(self):
        pass

classes.append(pbrAudioTemperatureNode)

#class pbrAudioEnvironmentNode(Node):
#    """pbrAudio environment node"""
#    bl_idname = 'pbrAudioEnvironmentNode'
#    bl_label = "Environment"
#
#    def init(self, context):
#        self.outputs.new('pbrAudioWorldEnvironmentNodeSocket', text='Environment')
#
#    def draw_buttons(self, context, layout):
#        for world in bpy.data.worlds.values():
#            if hasattr(world, 'pbraudioEnv'):
#                environment = world.pbraudioEnv
#        layout.prop(environment, "ambisonic_file")
#        layout.prop(environment, "cwsphere_radius")
#        layout.prop(environment, "ch_num")
#
#    def draw_label(self):
#        return "Acoustic Environment"
#
#    def update(self):
#        pass
#
#    def free(self):
#        pass
#
#classes.append(pbrAudioEnvironmentNode)
