# <pep8 compliant>


# <import>
import os, subprocess, math
import bpy, bmesh, mathutils
from .. import common

from . game import BASE_PG_GameProps
# </import>

# <props>
class BASE_PG_SettingsProps(bpy.types.PropertyGroup):
    """Properties for the Settings panel"""
    games: bpy.props.CollectionProperty(type = BASE_PG_GameProps)
    game_index: bpy.props.IntProperty(default = 0)

    scale: bpy.props.FloatProperty(
        name = "Model Scale",
        description = "Factor to scale your models by for export",
        default = 1.0,
    )
# </props>