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
from .config import pbrAudioConfigInit

classes =  []

class PBRAudioRenderEngine(RenderEngine):
    """pbrAudio render engine implementation"""
    bl_idname = 'PBRAUDIO'
    bl_label = "pbrAudio"
    bl_use_preview = True
    bl_use_shading_nodes_custom = False

    # Init is called whenever a new render engine instance is created. Multiple
    # instances may exist at the same time, for example for a viewport and final
    # render.
    # Note the generic arguments signature, and the call to the parent class
    # `__init__` methods, which are required for Blender to create the underlying
    # `RenderEngine` data.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_data = None
        self.draw_data = None

    # When the render engine instance is destroy, this is called. Clean up any
    # render engine data here, for example stopping running render threads.
#    def __del__(self):
        # Own delete code...
#        super().__del__()

    # Render methods
    def update(self, data, depsgraph):
        """Update render data"""
        self.report({'INFO'}, "pbrAudio rendering updated...")

    def render(self, depsgraph):
        """Main render method"""
        self.report({'INFO'}, "pbrAudio rendering in progress...")
        scene = depsgraph.scene
        pbraudio_init = pbrAudioConfigInit()

        # check cache tree
        if not pbraudio_init.scene.pbraudio.cache_status:
            pbraudio_init.create_cache()

        pbraudio_init.domain_config()
        pbraudio_init.source_config()
        pbraudio_init.output_config()
        #pbraudio.init.object_config()
        pbraudio_init.create_config()

        if not pbraudio_init.scene.pbraudio.cache_status:
            pbraudio_init.initZarr()
            pbraudio_init.scene.pbraudio.cache_status = True

        self.report({'INFO'}, "pbrAudio rendering end...")

        # For viewport renders, this method gets called once at the start and
        # whenever the scene or 3D viewport changes. This method is where data
        # should be read from Blender in the same thread. Typically a render
        # thread will be started to do the work while keeping Blender responsive.
        def view_update(self, context, depsgraph):
            """Update viewport"""
            pass

        # For viewport renders, this method is called whenever Blender redraws
        # the 3D viewport. The renderer is expected to quickly draw the render
        # with OpenGL, and not perform other expensive work.
        # Blender will draw overlays for selection and editing on top of the
        # rendered image automatically.
        def view_draw(self, context, depsgraph):
            """Draw viewport"""
            pass

classes.append(PBRAudioRenderEngine)
