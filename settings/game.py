import os
from pathlib import Path
import bpy


class GameProps(bpy.types.PropertyGroup):
    """Properties for a game"""
    bl_idname = "SOURCEOPS_PG_GameProps"

    def verify(self):
        path = bpy.path.abspath(self.gameinfo)
        gameinfo = Path(path).resolve()
        mod = gameinfo.parent
        game = mod.parent
        studiomdl = game / "bin/studiomdl.exe"
        hlmv = game / "bin/hlmv.exe"
        name = game.name

        self["gameinfo"] = str(gameinfo)
        self["mod"] = str(mod)
        self["studiomdl"] = str(studiomdl)
        self["hlmv"] = str(hlmv)

        if gameinfo.is_file() and studiomdl.is_file():
            self["name"] = str(name)
            return True
        else:
            self["name"] = "Invalid Game"
            return False

    def update(self, context):
        self.verify()

    gameinfo: bpy.props.StringProperty(
        name="Mod Path",
        description="Path to your gameinfo.txt",
        default="gameinfo.txt",
        subtype='FILE_PATH',
        update=update,
    )

    mod: bpy.props.StringProperty(
        name="Mod Path",
        description="Path to your mod folder, eg cstrike for CS:S",
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
