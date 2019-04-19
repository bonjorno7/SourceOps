# <pep8 compliant>


# <import>
import os, subprocess, math
from pathlib import Path

import bpy, bmesh, mathutils
from .. import common


# </import>

# <functions>
def update_path(self, context):
    mod_path = Path(self["path"]).absolute()
    game_path = mod_path.parent
    studiomdl_exe = game_path / r"bin/studiomdl.exe"
    hlmv_exe = game_path / r"bin/hlmv.exe"
    self["path"] = str(mod_path)
    self["game"] = str(game_path)
    self["name"] = str(mod_path.name)
    self["studiomdl"] = str(studiomdl_exe)
    self["hlmv"] = str(hlmv_exe)

    if not studiomdl_exe.is_file():
        self["name"] = "Invalid Game"


# </functions>

# <props>
class BASE_PG_GameProps(bpy.types.PropertyGroup):
    """Properties for a game"""
    path: bpy.props.StringProperty(
        name="Mod Path",
        description="Path to your game mod folder, eg cstrike for CS:S",
        default="",
        subtype='FILE_PATH',
        update=update_path,
    )
    game: bpy.props.StringProperty(
        name="Game Path",
        description="Path to your game folder, eg cstrike for CS:S",
        default="",
        subtype='FILE_PATH',
        update=update_path,
    )

    name: bpy.props.StringProperty(
        name="Game Name",
        description="Name of the game you're exporting for",
        default="Game Name",
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


# </props>

# <list>
class BASE_UL_GameList(bpy.types.UIList):
    """List of games"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.name)


class BASE_OT_AddGame(bpy.types.Operator):
    """Add a game"""
    bl_idname = "base.add_game"
    bl_label = "Add Game"

    def execute(self, context):
        base = context.scene.BASE
        settings = base.settings
        settings.games.add()
        settings.game_index = len(settings.games) - 1
        return {'FINISHED'}


class BASE_OT_RemoveGame(bpy.types.Operator):
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


class BASE_OT_MoveGame(bpy.types.Operator):
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
# </list>
