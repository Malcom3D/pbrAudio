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
from bpy.app.handlers import persistent
from bpy.utils import register_class, unregister_class

classes = []

from . import playback

for mod in (playback, ):
    classes += mod.classes

def register():
    for cls in classes:
        register_class(cls)

    # Add handler for playback events
    if not hasattr(bpy.types.Screen, '_play_handler'):
        @persistent
        def play_handler(scene):
            # Update all playback status nodes when playback state change to play
            for node_tree in bpy.data.node_groups:
                if 'pbrAudio' in node_tree.name:
                    if node_tree.nodes.values():
                        for node in node_tree.nodes:
                            if hasattr(node, 'playback_update'):
                                node.playback_update(True)

    if not hasattr(bpy.types.Screen, '_stop_handler'):
        @persistent
        def stop_handler(scene):
            # Update all playback status nodes when playback state change to stop
            for node_tree in bpy.data.node_groups:
                if 'pbrAudio' in node_tree.name:
                    if node_tree.nodes.values():
                        for node in node_tree.nodes:
                            if hasattr(node, 'playback_update'):
                                node.playback_update(False)

        bpy.types.Screen._play_handler = play_handler
        bpy.types.Screen._stop_handler = stop_handler
        bpy.app.handlers.animation_playback_post.append(stop_handler)
        bpy.app.handlers.animation_playback_pre.append(play_handler)


    @persistent
    def item_activate_handler(context):
        object = bpy.context.active_object
        treeType = None
        nodeTreeName = None

        if object.type == 'EMPTY' or object.type == 'CAMERA':
            return

        for world in bpy.data.worlds:
            if hasattr(world.pbraudio, 'acoustic_domain'):
                AcousticDomain = world.pbraudio.acoustic_domain

        if object == AcousticDomain:
            treeType = 'AudioWorldNodeTree'
            if hasattr(world.pbraudio.nodetree, 'name'):
                nodeTreeName = world.pbraudio.nodetree.name
        else:
            treeType = 'AudioMaterialNodeTree'
            if hasattr(object.pbraudio.nodetree, 'name'):
                nodeTreeName = object.pbraudio.nodetree.name

        if treeType is not None:
            for area in bpy.context.screen.areas:
                if area.type == "NODE_EDITOR":
                    for space in area.spaces:
                        if space.type == "NODE_EDITOR" and not space.pin:
                            if 'Audio' in space.tree_type:
                                space.tree_type = treeType
                                if nodeTreeName is not None:
                                    space.node_tree = bpy.data.node_groups[nodeTreeName]

    bpy.app.handlers.depsgraph_update_post.append(item_activate_handler)

def unregister():
    for cls in reversed(classes):
        unregister_class(cls)

    # Remove handler
    bpy.app.handlers.depsgraph_update_post.remove(item_activate_handler)

    if hasattr(bpy.types.Screen, '_playback_handler'):
        if bpy.types.Screen._play_handler in bpy.app.handlers.animation_playback_pre:
            bpy.app.handlers.animation_playback_pre.remove(bpy.types.Screen._play_handler)
        if bpy.types.Screen._stop_handler in bpy.app.handlers.animation_playback_post:
            bpy.app.handlers.animation_playback_post.remove(bpy.types.Screen._stop_handler)
        delattr(bpy.types.Screen, '_play_handler')
        delattr(bpy.types.Screen, '_stop_handler')
