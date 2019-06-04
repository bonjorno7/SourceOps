import os
import subprocess
import math
import bpy
import bmesh
import mathutils
from .. import common
from . game import GameProps


class SettingsProps(bpy.types.PropertyGroup):
    """Properties for the Settings panel"""
    bl_idname: "BASE_PG_SettingsProps"

    games: bpy.props.CollectionProperty(type=GameProps)
    game_index: bpy.props.IntProperty(default=0)

    def game(self):
        if self.games:
            return self.games[self.game_index]
        return None

    scale: bpy.props.FloatProperty(
        name="Model Scale",
        description="Factor to scale your models by for export",
        default=1.0,
    )
