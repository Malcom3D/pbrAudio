import bpy
import aud
from bpy.types import Node, NodeSocket, Operator
from bpy.props import PointerProperty, StringProperty, FloatProperty
from bpy.utils import register_class, unregister_class

classes = []

class audTreeNodeSocket:
    def get_tree(self):
        return self.id_data

    def get_index(self):
        # TODO: store index in property?
        return int(self.path_from_id().split('[')[-1][:-1])

class audSocketSound(NodeSocket, audTreeNodeSocket):
    """Custom NodeSocket for streaming audio between audaspace 3DHandle and 3DDevice nodes."""

    bl_idname = 'audSocketSound'
    bl_label = 'Sound Socket'

    def update_value(self, context):
       self.node.send_value_update(self.get_index(), self.value_prop)

    value_prop: bpy.props.FloatProperty(update=update_value)

    def init(self, context):
        self.display_shape = 'CIRCLE'

    def draw(self, context, layout, node, text):
        layout.label(text=text if text else "Sound")

    def draw_color(self, context, node):
        return (0.8, 0.2, 0.6, 1.0)  # Pinkish color for sound sockets

classes.append(audSocketSound)

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
        self.outputs.new('audSocketSound', "Audio Output")
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "filepath")
        layout.prop(self, "volume")
        op = layout.operator("audaspace.playsound", text="Play")
        op.filepath = self.filepath
        op.volume = self.volume
    
    def update(self):
        pass

classes.append(audPlayBack)

class aud3DOutput(Node):
    """A custom node that outputs audio with 3D spatialization based on an object's transform."""
    bl_idname = 'audaspace.3doutput'
    bl_label = 'Spatialized Output'
    bl_icon = 'SOUND'

    # Property to store the selected object
    target_object: PointerProperty(
        name="Target Object",
        type=bpy.types.Object,
        description="The object whose position and orientation will be used for spatialization"
    )

    def init(self, context):
        """Initialize the node with an input socket."""
        self.inputs.new('audSocketSound', "Input")

    def update(self):
        """Update the node's output based on the input and object transform."""
        if not self.inputs[0].is_linked:
            return

        input_sound = self.inputs[0].links[0].from_socket.default_value
        if not input_sound:
            return

        if not self.target_object:
            return

        # Get the object's location and rotation
        location = self.target_object.location
        rotation = self.target_object.rotation_euler

        # Create a 3D handle for spatialization
        handle = aud.I3DHandle(input_sound)
        handle.position = location
        handle.orientation = rotation

        # Play the sound (or pass it to the next node if needed)
        # In a real implementation, you might want to return the handle or play it directly
        # For now, we just store it in the node
        self.sound_handle = handle

    def free(self):
        """Clean up when the node is removed."""
        if hasattr(self, 'sound_handle'):
            self.sound_handle.stop()
            del self.sound_handle

    def draw_buttons(self, context, layout):
        """Draw the UI elements for the node."""
        layout.prop(self, "target_object")

classes.append(aud3DOutput)

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

class AUD_OT_add_spatialization_node(bpy.types.Operator):
    """Add a spatialization audio node"""
    bl_idname = "aud.add_spatialization_node"
    bl_label = "Add Spatialization Node"
   
    def execute(self, context):
        if not context.space_data.edit_tree:
            return {'CANCELLED'}

        tree = context.space_data.edit_tree
        node = tree.nodes.new('SpatializationNode')
        return {'FINISHED'}

classes.append(AUD_OT_add_spatialization_node)

class SpatializationNode(bpy.types.Node):
    """Audio spatialization node based on 3D object position"""
    bl_idname = 'audaspace.SpatializationNode'
    bl_label = 'Spatialization'
    bl_icon = 'SOUND'
   
    # Properties
    object_ref: PointerProperty(
        name="Object",
        type=bpy.types.Object,
        description="Object to track for spatialization"
    )
   
    distance_max: FloatProperty(
        name="Max Distance",
        default=25.0,
        min=0.1,
        max=1000.0,
        description="Maximum distance for audio attenuation"
    )
   
    distance_reference: FloatProperty(
        name="Reference Distance",
        default=1.0,
        min=0.1,
        max=100.0,
        description="Distance where volume is not attenuated"
    )
   
    rolloff_factor: FloatProperty(
        name="Rolloff Factor",
        default=1.0,
        min=0.1,
        max=10.0,
        description="How quickly sound attenuates with distance"
    )

    def init(self, context):
        """Initialize the node"""
        self.inputs.new('audSocketSound', "Sound")
        self.outputs.new('audSocketSound', "Sound")

    def draw_buttons(self, context, layout):
        """Draw node properties"""
        layout.prop(self, "object_ref")
        layout.prop(self, "distance_max")
        layout.prop(self, "distance_reference")
        layout.prop(self, "rolloff_factor")

    def draw_buttons_ext(self, context, layout):
        """Draw additional node properties"""
        self.draw_buttons(context, layout)

    def get_settings(self):
        """Get spatialization settings"""
        return {
            'distance_max': self.distance_max,
            'distance_reference': self.distance_reference,
            'rolloff_factor': self.rolloff_factor,
            'object': self.object_ref
        }

    def create_spatializer(self, i3ddevice, factory, settings):
        """Create the spatialization effect"""
        if not settings['object']:
            return factory

        # Get object location and orientation
        loc = settings['object'].location
        rot = settings['object'].rotation_euler

        # Create 3D sound effect
        effect = aud.Sound3D(
            factory,
            aud.Vector3(loc.x, loc.z, loc.y),  # Note: Blender's Z is up, audaspace's Y is up
            aud.Vector3(0, 0, 0),  # Velocity (not used here)
            aud.Vector3(math.sin(rot.z), 0, math.cos(rot.z)),  # Orientation (simplified)
            settings['distance_max'],
            settings['distance_reference'],
            settings['rolloff_factor']
        )

        return effect

    def evaluate(self):
        """Evaluate the node's output"""
        if not self.inputs[0].is_linked:
            return None

        input_node = self.inputs[0].links[0].from_node
        sound = input_node.evaluate()

        if sound is None:
            return None

        settings = self.get_settings()
        device = aud.Device()

        # Create spatialized sound
        spatial_sound = self.create_spatializer(device, sound, settings)

        return spatial_sound

classes.append(SpatializationNode)
