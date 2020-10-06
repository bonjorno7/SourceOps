import bpy


class SOURCEOPS_EventProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name='Name',
        description='The name this event has in the list',
        default='Example',
    )

    event: bpy.props.StringProperty(
        name='Event Type',
        description='The type of the event',
        default='AE_CL_PLAYSOUND',
    )

    frame: bpy.props.IntProperty(
        name='Start Frame',
        description='The frame of the sequence at which the event should start',
        default=0,
    )

    value: bpy.props.StringProperty(
        name='Event Value',
        description='The value for the event',
        default='Weapon_Shotgun.Single',
    )
