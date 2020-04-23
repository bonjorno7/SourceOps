import bpy


class SOURCEOPS_MaterialFolderProps(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(
        name='Folder Path',
        description='$cdmaterials, the folder inside of which to look for materials, relative to your game\'s materials folder',
        default='models/example',
    )
