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
import math
from bpy.types import PropertyGroup
from bpy.props import IntProperty, FloatProperty, StringProperty, EnumProperty, PointerProperty

from ..nodetrees.worldNT import AudioWorldNodeTree

classes = []

class PBRAudioWorldProperties(PropertyGroup):
    def domain_selected(self, context):
        if self.old_domain:
            self.old_domain.display.show_shadows = True
            self.old_domain.display_type = 'TEXTURED'
            self.old_domain.show_bounds = False

        self.old_domain = self.acoustic_domain
        if self.acoustic_domain:
            self.acoustic_domain.display.show_shadows = False
            self.acoustic_domain.display_type = 'WIRE'
            self.acoustic_domain.show_bounds = True

    def compute_speed_imp(self, context):
       self.compute_speed(self, context)
       self.compute_impedence(self, context)

    def compute_speed(self, context):
       if self.type == 'GAS':
          self.sound_speed = sqrt((self.C_p/self.C_v)*(self.R_0/self.M)*(self.temperature+273.15))
       elif self.type == 'LIQUID':
          self.sound_speed = sqrt(self.K/self.density)
       elif self.type == 'SOLID':
          self.sound_speed = sqrt(self.E/self.density)

       if self.outputs['Sound Speed'].is_linked:
          self.outputs['Sound Speed'].sound_speed = self.sound_speed

    def compute_impedence(self, context):
        self.impedence = self.density*self.sound_speed

    """World properties for pbrAudio"""
    acoustic_domain: PointerProperty(
        name="Domain",
        type=bpy.types.Object,
        description="Select the target object",
        update=domain_selected
    )

    old_domain: PointerProperty(
        name="Old Domain Target Object",
        type=bpy.types.Object,
        description="Old selected target object",
    )

    """World Material properties for pbrAudio"""
    nodetree: PointerProperty(
        name="NodeTree",
        type=AudioWorldNodeTree
    )

    type: EnumProperty(
        name="Medium Type",
        items=[
            ('GAS', "Gas", "Spheric wave sound source"),
            ('LIQUID', "Liquid", "Plane wave sound source"),
            ('SOLID', "Solid", "Plane wave sound source"),
        ],
        default='GAS'
    )

    C_p: FloatProperty(
        name="Specific heat at constant pressure",
        default=7.0,
        update=compute_speed
    )

    C_v: FloatProperty(
        name="Specific heat at constant volume",
        default=5.0,
        update=compute_speed
    )

    R_0: FloatProperty(
        name="Gas constant",
        default=8.31446261815324,
        update=compute_speed
    )

    M: FloatProperty(
        name="Molar mass",
        default=0.0289645,
        update=compute_speed
    )

    K: FloatProperty(
        name="Bulk modulus",
        default=0.0,
        update=compute_speed
    )

    E: FloatProperty(
        name="Young modulus",
        default=0.0,
        update=compute_speed
    )

    sound_speed: FloatProperty(
        name="Specific heat at constant pressure",
        default=0.0,
        update=compute_impedence
    )

    impedence: FloatProperty(
        name="Medium impedence",
        default=0.0
    )

    density: FloatProperty(
        name="Medium Density",
        default=1.2041,
        min=0.1,
        max=5.0,
        update=compute_speed_imp
    )

    temperature: FloatProperty(
        name="Temperature in Celsius degree",
        default=20,
        min=-273.15,
        update=compute_speed_imp
    )

classes.append(PBRAudioWorldProperties)

#class PBRAudioWorldEnvironmentProperties(PropertyGroup):
#    name: StringProperty(
#        name="Environment Name Property",
#        default="Unknown"
#    )
#
#    ambisonic_file: StringProperty(
#        name="Audio File",
#        description="Path to ambisonic file",
#        subtype='FILE_PATH'
#    )
#
#    sphere_radius: FloatProperty(
#        name="Radius of field sphere",
#        default=1.0
#    )
#
#    ch_num: IntProperty(
#        name="Channel number",
#        default=6,
#    )
#
#classes.append(PBRAudioWorldEnvironmentProperties)
