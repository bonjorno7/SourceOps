import bpy
from . game_props import SOURCEOPS_GameProps


class SOURCEOPS_AddonPrefs(bpy.types.AddonPreferences):
    bl_idname =  __name__.partition('.')[0]

    game_items: bpy.props.CollectionProperty(type=SOURCEOPS_GameProps)
    game_index: bpy.props.IntProperty(default=0, name='Ctrl click to rename')
