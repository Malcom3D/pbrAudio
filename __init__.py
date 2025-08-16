# Blender addon sorcery

bl_info = {
    "name": "pbrAudio",
    "description": "Physically-based sound synthesis",
    "author": "Malcom3D",
    "version": (0,0,1),
    "blender": (4,5,1),
    "location": "Node Editor > Sound Icon > Add new",
    "warning": "",
    "category": "Node",
    "tracker_url": "https://github.com/Malcom3D/pbrAudio/issues",
    "wiki_url": "https://github.com/Malcom3D/pbrAudio/wiki"
}

import bpy
import time
from bpy.types import NodeTree, Node, NodeSocket, NodeSocketFloat

from struct import pack
from array import array

import threading

import wave
import struct
import tempfile
import platform

from . import nodes
node_tree = nodes.node_tree
ffi = nodes.ffi

def register():
    nodes.register()
    ffi.initialize()

def unregister():
    ffi.cleanup()
    nodes.unregister()

import atexit
def exit_handler():
    ffi.cleanup()
atexit.register(exit_handler)

from bpy.app.handlers import persistent
@persistent
def pre_load_handler(_):
    ffi.flag_loading_file = True
    ffi.cleanup()

@persistent
def post_load_handler(_):
    ffi.initialize()
    ffi.flag_loading_file = False
    for tree in bpy.data.node_groups:
        if type(tree) == node_tree.pbrAudioTree:
            tree.post_load_handler()

bpy.app.handlers.load_pre.append(pre_load_handler)
bpy.app.handlers.load_post.append(post_load_handler)

if __name__ == "__main__":
    register()
