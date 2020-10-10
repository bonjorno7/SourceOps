import bpy
from .. import utils


class SOURCEOPS_GameProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name='Name',
        description='The name this game has in the list',
        default='Example',
    )

    game: bpy.props.StringProperty(
        name='Game',
        description='Path to your game folder',
        subtype='DIR_PATH',
        update=utils.game.update_game,
    )

    bin: bpy.props.StringProperty(
        name='Bin',
        description='Path to your bin folder',
        subtype='DIR_PATH',
        update=utils.game.update_bin,
    )

    modelsrc: bpy.props.StringProperty(
        name='ModelSrc',
        description='Path to your modelsrc folder',
        subtype='DIR_PATH',
        update=utils.game.update_modelsrc,
    )

    models: bpy.props.StringProperty(
        name='Models',
        description='Path to your models folder',
        subtype='DIR_PATH',
        update=utils.game.update_models,
    )

    mapsrc: bpy.props.StringProperty(
        name='Mapsrc',
        description='Path to your mapsrc folder',
        subtype='DIR_PATH',
        update=utils.game.update_mapsrc,
    )
