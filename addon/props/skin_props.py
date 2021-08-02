import bpy


class SOURCEOPS_SkinProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name='Materials',
        description='Space separated list of VMT names, supports quotes',
        default='example',
    )
