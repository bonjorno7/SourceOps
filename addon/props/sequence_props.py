import bpy
from . event_props import SOURCEOPS_EventProps


class SOURCEOPS_SequenceProps(bpy.types.PropertyGroup):
    event_items: bpy.props.CollectionProperty(type=SOURCEOPS_EventProps)
    event_index: bpy.props.IntProperty(default=0, name='Ctrl click to rename')

    name: bpy.props.StringProperty(
        name='Name',
        description='The name this sequence will have in game',
        default='idle',
    )

    action: bpy.props.PointerProperty(
        name='Action',
        description='The action to use for this sequence',
        type=bpy.types.Action,
    )

    use_framerate: bpy.props.BoolProperty(
        name='Custom Framerate',
        description='Whether to use the custom framerate instead of the scene framerate',
        default=False,
    )

    framerate: bpy.props.IntProperty(
        name='Framerate',
        description='If override is enabled, use this framerate instead of the scene framerate',
        default=30,
    )

    use_range: bpy.props.BoolProperty(
        name='Custom Range',
        description='Whether to use custom start and end frames instead of the whole action',
        default=False,
    )

    start: bpy.props.IntProperty(
        name='Start Frame',
        description='First frame of the sequence',
        default=1,
    )

    end: bpy.props.IntProperty(
        name='End Frame',
        description='Last frame of the sequence',
        default=30,
    )

    activity: bpy.props.StringProperty(
        name='Activity',
        description='The the activity that triggers this sequence to play',
        default='ACT_VM_IDLE',
    )

    weight: bpy.props.IntProperty(
        name='Weight',
        description='Determines the chance this sequence will play compared to other sequences with this activity',
        default=1,
    )

    snap: bpy.props.BoolProperty(
        name='Snap',
        description='Snap to and from this sequence instead of interpolating',
        default=False,
    )

    loop: bpy.props.BoolProperty(
        name='Loop',
        description='Whether the sequence will be looped.\nStart frame must be identical to end frame',
        default=False,
    )
