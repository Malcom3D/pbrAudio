import bpy
import aud
from bpy.types import Node, Operator
from bpy.props import PointerProperty, StringProperty, FloatProperty
from bpy.utils import register_class, unregister_class

classes = []

class audPlaySound(bpy.types.Operator):
    """Play audio file"""
    bl_idname = "audaspace.playsound"
    bl_label = "Play Sound"
    
    filepath: StringProperty()
    volume: FloatProperty(default=1.0)
    
    def execute(self, context):
        try:
            # Create a device
            device = aud.Device()
            
            # Load sound file
            sound = aud.Sound(self.filepath)
            
            # Play sound with volume adjustment
            handle = device.play(sound)
            handle.volume = self.volume
            
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

classes.append(audPlaySound)

class audPlayBack(Node):
    """A custom node for audio playback"""
    bl_idname = 'audaspace.playback'
    bl_label = 'Audio Player'
    bl_icon = 'SOUND'
    
    filepath: StringProperty(
        name="File Path",
        description="Path to audio file",
        subtype='FILE_PATH'
    )
    
    volume: FloatProperty(
        name="Volume",
        description="Volume level",
        default=1.0,
        min=0.0,
        max=1.0
    )
    
    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Audio Output")
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "filepath")
        layout.prop(self, "volume")
        op = layout.operator("audaspace.playsound", text="Play")
        op.filepath = self.filepath
        op.volume = self.volume
    
    def update(self):
        pass

classes.append(audPlayBack)

class audPlay3DSound(Operator):
    """Play 3D Audio"""
    bl_idname = "audaspace.play3dsound"
    bl_label = "Play 3D Audio"
    
    filepath: StringProperty(name="File Path", subtype='FILE_PATH')
    
    def execute(self, context):
        node = context.node
        if not node.sound_object:
            self.report({'ERROR'}, "No object selected for sound source")
            return {'CANCELLED'}
        
        if not node.sound_file:
            self.report({'ERROR'}, "No audio file selected")
            return {'CANCELLED'}
        
        # Create audio device
        device = aud.Device()
        
        # Load sound file
        try:
            sound = aud.Sound(node.sound_file)
        except:
            self.report({'ERROR'}, "Could not load audio file")
            return {'CANCELLED'}
        
        # Create handle for playback control
        handle = device.play(sound)
        handle.relative = False
        handle.distance_model = aud.DISTANCE_MODEL_INVERSE_CLAMPED
        
        # Store handle in node for later control
        node.sound_handle = handle
        
        # Update position/orientation immediately
        self.update_sound_position(node)
        
        # Add handler for continuous updates
        if not hasattr(bpy.app.handlers, 'frame_change_pre'):
            bpy.app.handlers.frame_change_pre = []
        
        if self.update_sound_position not in bpy.app.handlers.frame_change_pre:
            bpy.app.handlers.frame_change_pre.append(self.update_sound_position)
        
        return {'FINISHED'}
    
    def update_sound_position(self, node):
        if not hasattr(node, 'sound_handle') or not node.sound_handle:
                       return
        
        obj = node.sound_object
        if not obj:
            return
        
        # Get object location and orientation
        location = obj.location
        orientation = obj.rotation_euler.to_quaternion()
        
        # Update sound position and orientation
        node.sound_handle.location = location
        node.sound_handle.orientation = orientation


classes.append(audPlay3DSound)

class audStop3DSound(Operator):
    """Stop 3D Audio"""
    bl_idname = "audaspace.stop3dsound"
    bl_label = "Stop 3D Audio"
    
    def execute(self, context):
        node = context.node
        if hasattr(node, 'sound_handle') and node.sound_handle:
            node.sound_handle.stop()
            node.sound_handle = None
            
            # Remove handler if no other nodes need it
            if hasattr(bpy.app.handlers, 'frame_change_pre'):
                if audPlay3DSound.update_sound_position in bpy.app.handlers.frame_change_pre:
                    bpy.app.handlers.frame_change_pre.remove(audPlay3DSound.update_sound_position)
        
        return {'FINISHED'}

classes.append(audStop3DSound)

class aud3DplayBackNode(Node):
    """A custom node for 3D audio playback"""
    bl_idname = 'audaspace.3dplayback'
    bl_label = "3D Audio Node"
    bl_icon = 'SOUND'
    
    sound_file: StringProperty(
        name="Sound File",
        description="Path to the audio file",
        subtype='FILE_PATH'
    )
    
    sound_object: PointerProperty(
        name="Sound Source",
        type=bpy.types.Object,
        description="Object to track for 3D audio positioning"
    )
    
    def init(self, context):
        pass
    
    def draw_buttons(self, context, layout):
        row = layout.row()
        row.prop(self, "sound_file")
        
        row = layout.row()
        row.prop(self, "sound_object")
        
        row = layout.row()
        row.operator("audaspace.play3dsound", text="Play")
        row.operator("audaspace.stop3dsound", text="Stop")
    
    def copy(self, node):
        self.sound_file = node.sound_file
        self.sound_object = node.sound_object
    
    def free(self):
        # Stop sound when node is removed
        if hasattr(self, 'sound_handle') and self.sound_handle:
            self.sound_handle.stop()
            self.sound_handle = None

classes.append(aud3DplayBackNode)
