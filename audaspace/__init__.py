import bpy
import nodeitems_utils
from bpy.utils import register_class, unregister_class
from nodeitems_utils import NodeCategory, NodeItem, register_node_categories, unregister_node_categories
from ..pbrAudioNodeTree import pbrAudioNodeCategory

node_categories = [
    pbrAudioNodeCategory("AUD_NODES", "AudaSpace", items=[NodeItem("audPlayBackNode"),
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
