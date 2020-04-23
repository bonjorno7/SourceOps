import bpy


class SOURCEOPS_SkinProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name='VMT Name',
        description='Name of this material in the texture group',
        default='example',
    )
