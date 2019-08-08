import os
from pathlib import Path
import bpy


class GameProps(bpy.types.PropertyGroup):
    """Properties for a game"""
    bl_idname = "SOURCEOPS_PG_GameProps"

    def is_valid(self):
        return self.name != "Invalid Game"

    def verify(self, context):
        if not os.path.isfile(self.studiomdl):
            self["name"] = "Invalid Game"
            return False
        return True

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
