import os
import subprocess
import math
from pathlib import Path
import bpy
import bmesh
import mathutils
from .. import common


def update_path(self, context):
    path = bpy.path.abspath(self["gameinfo"])
    gameinfo = Path(path).resolve()
    mod = gameinfo.parent
    game = mod.parent
    studiomdl = game / r"bin/studiomdl.exe"
    hlmv = game / r"bin/hlmv.exe"
    name = game.name

    self["gameinfo"] = str(gameinfo)
    self["mod"] = str(mod)
    self["game"] = str(game)
    self["studiomdl"] = str(studiomdl)
    self["hlmv"] = str(hlmv)

    if studiomdl.is_file():
        self["name"] = str(name)
    else:
        self["name"] = "Invalid Game"


class GameProps(bpy.types.PropertyGroup):
    """Properties for a game"""
    bl_idname = "BASE_PG_GameProps"

    gameinfo: bpy.props.StringProperty(
        name="Mod Path",
        description="Path to your gameinfo.txt",
        default="",
        subtype='FILE_PATH',
        update=update_path,
    )

    mod: bpy.props.StringProperty(
        name="Mod Path",
        description="Path to your mod folder, eg cstrike for CS:S",
        default="",
    )

    game: bpy.props.StringProperty(
        name="Game Path",
        description="Path to your game folder, eg Counter-Strike Source for CS:S",
        default="",
    )

    studiomdl: bpy.props.StringProperty(
        name="StudioMDL",
        description="Path to studiomdl.exe",
        default="",
    )

    hlmv: bpy.props.StringProperty(
        name="HLMV",
        description="Path to hlmv.exe",
        default="",
    )

    name: bpy.props.StringProperty(
        name="Game Name",
        description="Name of the game you're exporting for",
        default="Game Name",
    )


class GameList(bpy.types.UIList):
    """List of games"""
    bl_idname = "BASE_UL_GameList"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.name)


class AddGame(bpy.types.Operator):
    """Add a game"""
    bl_idname = "base.add_game"
    bl_label = "Add Game"

    def execute(self, context):
        base = context.scene.BASE
        settings = base.settings
        settings.games.add()
        settings.game_index = len(settings.games) - 1
        return {'FINISHED'}


class RemoveGame(bpy.types.Operator):
    """Remove the selected game from the list"""
    bl_idname = "base.remove_game"
    bl_label = "Remove Game"

    @classmethod
    def poll(cls, context):
        base = context.scene.BASE
        settings = base.settings
        return len(settings.games) > 0

    def execute(self, context):
        base = context.scene.BASE
        settings = base.settings
        settings.games.remove(settings.game_index)
        settings.game_index = min(
            max(0, settings.game_index - 1),
            len(settings.games) - 1
        )
        return {'FINISHED'}


class MoveGame(bpy.types.Operator):
    """Move the selected game up or down in the list"""
    bl_idname = "base.move_game"
    bl_label = "Move Game"

    direction: bpy.props.EnumProperty(items=(
        ('UP', "Up", "Move the item up"),
        ('DOWN', "Down", "Move the item down"),
    ))

    @classmethod
    def poll(cls, context):
        base = context.scene.BASE
        settings = base.settings
        return len(settings.games) > 1

    def execute(self, context):
        base = context.scene.BASE
        settings = base.settings
        neighbor = settings.game_index + (-1 if self.direction == 'UP' else 1)
        settings.games.move(neighbor, settings.game_index)
        list_length = len(settings.games) - 1
        settings.game_index = max(0, min(neighbor, list_length))
        return {'FINISHED'}
