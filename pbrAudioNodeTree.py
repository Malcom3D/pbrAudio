import bpy
import time
import nodeitems_utils
from bpy.types import NodeTree, Node, NodeSocket, NodeSocketFloat
from nodeitems_utils import NodeCategory

# classes for common node tree space
from .audionodes import ffi

classes = []

class pbrAudioNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'pbrAudioTreeType'

#classes.append(pbrAudioNodeCategory)

class pbrAudioTree(NodeTree):

    '''Node tree for audio mixer'''

    bl_idname = 'pbrAudioTreeType'
    bl_label = 'pbrAudio Node Editor'
    bl_icon = 'PLAY_SOUND'

    def init(self):
        pass

    def update(self):
        ######## from Audionodes
        # Blender likes to call this method when loading isn't yet finished,
        # don't do anything in that case
        if ffi.flag_loading_file:
            return
        ffi.begin_tree_update()
        for link in self.links:
            if link.to_node.bl_idname == "NodeReroute":
                continue
            from_node, from_socket = link.from_node, link.from_socket
            to_node, to_socket = link.to_node, link.to_socket
            connected = True
            while from_node.bl_idname == "NodeReroute":
                if not from_node.inputs[0].is_linked:
                    connected = False
                    break
                # TODO: socket.links is slow
                new_link = from_node.inputs[0].links[0]
                from_node, from_socket = new_link.from_node, new_link.from_socket
            if not connected:
                continue
            from_node.check_revive()
            to_node.check_revive()
            ffi.add_tree_update_link(from_node.get_uid(), to_node.get_uid(), from_socket.get_index(), to_socket.get_index())
        ffi.finish_tree_update()

    def post_load_handler(self):
        # Clear unique_ids first in case something goes wrong while initiailizing nodes
        for node in self.nodes:
            if isinstance(node, pbrAudioTreeNode):
                node["unique_id"] = -1
        for node in self.nodes:
            if isinstance(node, pbrAudioTreeNode):
                node.reinit()
        self.update()

    def refresh_all_uid_cache(self):
        for i, node in enumerate(self.nodes):
            if isinstance(node, pbrAudioTreeNode):
                node.refresh_uid_cache(i)

classes.append(pbrAudioTree)
