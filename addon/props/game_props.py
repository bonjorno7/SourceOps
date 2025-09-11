import bpy
from .. import utils


class SOURCEOPS_GameProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name='Name',
        description='The name this game has in the list, just for display',
        default='Example',
    )

    game: bpy.props.StringProperty(
        name='Game',
        description='Path to your game folder, gameinfo.txt is here',
        subtype='DIR_PATH',
        update=utils.game.update_game,
    )

    bin: bpy.props.StringProperty(
        name='Bin',
        description='Path to your bin folder, StudioMDL and HLMV are here',
        subtype='DIR_PATH',
        update=utils.game.update_bin,
    )

    studiomdl: bpy.props.StringProperty(
        name='StudioMDL',
        description='Path to your StudioMDL executable, used for compiling models',
        subtype='FILE_PATH',
        update=utils.game.update_studiomdl,
    )

    hlmv: bpy.props.StringProperty(
        name='HLMV',
        description='Path to your HLMV executable, used for previewing models',
        subtype='FILE_PATH',
        update=utils.game.update_hlmv,
    )

    modelsrc: bpy.props.StringProperty(
        name='ModelSrc',
        description='Path to your modelsrc folder, exported QC/SMD/FBX files go here',
        subtype='DIR_PATH',
        update=utils.game.update_modelsrc,
    )

    models: bpy.props.StringProperty(
        name='Models',
        description='Path to your models folder, compiled MDL files go here',
        subtype='DIR_PATH',
        update=utils.game.update_models,
    )

    mapsrc: bpy.props.StringProperty(
        name='Mapsrc',
        description='Path to your mapsrc folder, exported VMF files go here',
        subtype='DIR_PATH',
        update=utils.game.update_mapsrc,
    )

    mesh_type: bpy.props.EnumProperty(
        name='Mesh Type',
        description='File type for mesh export',
        items=[
            ('SMD', 'SMD', 'Export meshes as SMD'),
            ('FBX', 'FBX', 'Export meshes as FBX (only on CS:GO branch)'),
        ],
        default='SMD',
    )
