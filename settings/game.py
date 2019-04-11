# <import>
import os, subprocess, math
import bpy, bmesh, mathutils
from .. import common
# </import>

# <functions>
def update_path(self, context):
    self["path"] = os.path.realpath(bpy.path.abspath(self["path"]))
    self["name"] = os.path.basename(os.path.realpath(self["path"] + common.dir_up))
    if not os.path.isdir(self["path"]): self.report({'WARNING'}, "Invalid game path")
# </functions>

# <props>
class BASE_PG_GameProps(bpy.types.PropertyGroup):
    """Properties for a game"""
    name: bpy.props.StringProperty(
        name = "Game Name",
        description = "Name of the game you're exporting for",
        default = "Game Name",
    )

    path: bpy.props.StringProperty(
        name = "Game Path",
        description = "Path to your game folder, eg cstrike for CS:S",
        default = "",
        subtype = 'FILE_PATH',
        update = update_path,
    )
# </props>

# <list>
class BASE_UL_GameList(bpy.types.UIList):
    """List of games"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text = item.name)

class BASE_OT_AddGame(bpy.types.Operator):
    """Add a game"""
    bl_idname = "base.add_game"
    bl_label = "Add Game"

    def execute(self, context):
        settings = context.scene.BASE.settings
        settings.games.add()
        settings.game_index = len(settings.games) - 1
        return {'FINISHED'}

class BASE_OT_RemoveGame(bpy.types.Operator):
    """Remove the selected game from the list"""
    bl_idname = "base.remove_game"
    bl_label = "Remove Game"

    @classmethod
    def poll(cls, context):
        settings = context.scene.BASE.settings
        return len(settings.games) > 0

    def execute(self, context):
        settings = context.scene.BASE.settings
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

    direction: bpy.props.EnumProperty(items = (
        ('UP', "Up", "Move the item up"),
        ('DOWN', "Down", "Move the item down"),
    ))

    @classmethod
    def poll(cls, context):
        settings = context.scene.BASE.settings
        return len(settings.games) > 1

    def execute(self, context):
        settings = context.scene.BASE.settings
        neighbor = settings.game_index + (-1 if self.direction == 'UP' else 1)
        settings.games.move(neighbor, settings.game_index)
        list_length = len(settings.games) - 1
        settings.game_index = max(0, min(neighbor, list_length))
        return {'FINISHED'}
# </list>