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
from bpy.types import RenderEngine

classes =  []

class PBRAudioRenderEngine(RenderEngine):
    """pbrAudio render engine implementation"""
    bl_idname = 'PBRAUDIO'
    bl_label = "pbrAudio"
    bl_use_preview = True
    bl_use_shading_nodes_custom = False

    # Render methods
    def update(self, data, depsgraph):
        """Update render data"""
        pass

    def render(self, depsgraph):
        """Main render method"""
        scene = depsgraph.scene
        self.report({'INFO'}, "pbrAudio rendering in progress...")

    def view_update(self, context, depsgraph):
        """Update viewport"""
        pass

    def view_draw(self, context, depsgraph):
        """Draw viewport"""
        pass

classes.append(PBRAudioRenderEngine)
