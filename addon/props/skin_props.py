import bpy


class SOURCEOPS_SkinProps(bpy.types.PropertyGroup):
    display: bpy.props.StringProperty(
        name='Display Name',
        description='The name this material has in the list',
        default='Material Name',
    )

    name: bpy.props.StringProperty(
        name='VMT Name',
        description='Name of this material in the texture group',
        default='example',
    )
