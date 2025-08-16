import bpy
import aud
from bpy.types import Node
from bpy.props import StringProperty, FloatProperty

classes = []

class AudaSpacePlaySound(bpy.types.Operator):
    """Play audio file"""
    bl_idname = "audaspace.play_sound"
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

classes.append(AudaSpacePlaySound)

class audPlayBack(Node):
    """A custom node for audio playback"""
    bl_idname = 'audPlayBackNode'
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
        op = layout.operator("audaspace.play_sound", text="Play")
        op.filepath = self.filepath
        op.volume = self.volume
    
    def update(self):
        pass

classes.append(audPlayBack)
