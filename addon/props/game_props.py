import bpy


class SOURCEOPS_GameProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name='Name',
        description='The name this game has in the list',
        default='Example',
    )

    gameinfo: bpy.props.StringProperty(
        name='Gameinfo Path',
        description='Path to your gameinfo.txt',
        default='gameinfo.txt',
        subtype='FILE_PATH',
    )

    additional: bpy.props.StringProperty(
        name='Additional Path',
        description='Compiled models will be copied to this path',
        default='',
        subtype='FILE_PATH',
    )

    maps: bpy.props.StringProperty(
        name='Maps Path',
        description='Maps will be exported to this folder',
        default='',
        subtype='FILE_PATH',
    )
