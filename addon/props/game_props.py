import bpy


class SOURCEOPS_GameProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name='Name',
        description='The name this game has in the list',
        default='Example',
    )

    bin: bpy.props.StringProperty(
        name='Bin',
        description='Path to your bin folder',
        subtype='DIR_PATH',
    )

    modelsrc: bpy.props.StringProperty(
        name='ModelSrc',
        description='Path to your modelsrc folder',
        subtype='DIR_PATH',
    )

    models: bpy.props.StringProperty(
        name='Models',
        description='Path to your models folder',
        subtype='DIR_PATH',
    )

    maps: bpy.props.StringProperty(
        name='Maps',
        description='Path to your maps folder',
        subtype='DIR_PATH',
    )
