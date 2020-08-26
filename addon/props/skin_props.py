import bpy


class SOURCEOPS_SkinProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name='Name',
        description='Name of this VMT in the texture group',
        default='example',
    )
