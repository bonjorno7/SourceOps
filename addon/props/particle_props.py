import bpy

SOURCEOPS_ParticleAttachProps = [
    ('start_at_origin', 'start_at_origin', ''),
    ('start_at_attachment', 'start_at_attachment', ''),
    ('follow_origin', 'follow_origin', ''),
    ('follow_attachment', 'follow_attachment', ''),
]

class SOURCEOPS_ParticleProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name='Name',
        description='The name of a particle system. NOT the name of a .pcf file!',
        default='Particle',
    )

    attachment_type: bpy.props.EnumProperty(
        name='Attachment Type',
        description='The method of attaching the particle to the prop',
        items=SOURCEOPS_ParticleAttachProps,
        default='start_at_origin',
    )

    attachment_point: bpy.props.StringProperty(
        name='Attachment Point',
        description='The attachment point at which the particle system should spawn, if applicable',
        default='',
    )
