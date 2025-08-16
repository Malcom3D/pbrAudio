import bpy
import nodeitems_utils
from bpy.types import Node, Operator
from bpy.utils import register_class, unregister_class
from bpy.props import PointerProperty, StringProperty, FloatProperty
from nodeitems_utils import NodeCategory, NodeItem, register_node_categories, unregister_node_categories
from ..pbrAudioNodeTree import pbrAudioNodeCategory

node_categories = [
    pbrAudioNodeCategory("AUD_NODES", "AudaSpace", items=[
        NodeItem("audaspace.playback"),
        NodeItem("audaspace.3dplayback"),
        NodeItem("audaspace.3doutput"),
        NodeItem("audaspace.SpatializationNode"),
    ]),
]

classes = []

from . import nodes
classes = nodes.classes
#for mod in (nodes):
#    classes += mod.classes


def register():
    for cls in classes:
        register_class(cls)
    register_node_categories("AUDASPACE", node_categories)

def unregister():
    unregister_node_categories("AUDASPACE")
    for cls in reversed(classes):
        unregister_class(cls)
