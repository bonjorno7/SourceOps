import bpy


class SOURCEOPS_AttachmentProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name='Name',
        description='The name of this attachment',
        default='Attachment',
    )

    armature: bpy.props.StringProperty(
        name='Armature',
        description='The armature to choose the bone from',
        default='',
    )

    bone: bpy.props.StringProperty(
        name='Bone',
        description='The bone that this attachment should attach to',
        default='',
    )

    offset: bpy.props.FloatVectorProperty(
        name='Offset',
        subtype='XYZ',
        description='The local X, Y, and Z position of the attachment (relative to the bone position)',
        default=(0.0, 0.0, 0.0),
        step=10,
        precision=3,
    )

    rotation: bpy.props.FloatVectorProperty(
        name='Rotation',
        subtype='XYZ',
        description='Rotates the attachment, in degrees, relative to its parent bone / the origin. Formatted as [pitch, yaw, roll]',
        default=(0.0, 0.0, 0.0),
        step=100,
        precision=3,
    )

    absolute: bpy.props.BoolProperty(
        name='Absolute',
        description='Parented to the model\'s origin. The offset is still relative to the given parent bone, however',
        default=False,
    )

    rigid: bpy.props.BoolProperty(
        name='Rigid',
        description='Declares that the bone this attachment is parented to will not move, allowing StudioMDL to optimise it out. Used to convert bones created in a modelling package into attachments',
        default=False,
    )
