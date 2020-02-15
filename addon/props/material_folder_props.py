import bpy


class SOURCEOPS_MaterialFolderProps(bpy.types.PropertyGroup):
    display: bpy.props.StringProperty(
        name='Display Name',
        description='The name this folder has in the list',
        default='Material Folder Name',
    )

    path: bpy.props.StringProperty(
        name='Folder Path',
        description='$cdmaterials, the folder inside of which to look for materials, relative to your game\'s materials folder',
        default='',
    )
