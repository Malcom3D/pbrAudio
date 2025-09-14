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
from bpy.props import PointerProperty
from bpy.utils import register_class, unregister_class

classes = []

from . import enginePT, materialPG, materialPT, scenePG, worldPG, worldPT

for mod in (enginePT, materialPG, materialPT, scenePG, worldPG, worldPT):
    classes += mod.classes

def register():
    for cls in classes:
        register_class(cls)

    # Register property groups
    bpy.types.Scene.pbraudio = PointerProperty(type=scenePG.PBRAudioSceneProperties)
    bpy.types.Material.pbraudio = PointerProperty(type=materialPG.PBRAudioMaterialProperties)
    bpy.types.World.pbraudio = PointerProperty(type=worldPG.PBRAudioWorldProperties)

def unregister():
    for cls in reversed(classes):
        unregister_class(cls)

    """Unregister all classes and properties"""
    # Remove property groups
    del bpy.types.Scene.pbraudio
    del bpy.types.Material.pbraudio
    del bpy.types.World.pbraudio
