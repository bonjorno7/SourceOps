# <import>
import os
import bpy
from . import common
# </import>

# </type>
class Game(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(
        name = "",
        description = "Name of the game you're exporting for",
        default = "Game Name",
    )

    path = bpy.props.StringProperty(
        name = "",
        description = "Path to your game's gameinfo.txt",
        default = "",
        subtype = 'FILE_PATH',
    )

    scale = bpy.props.FloatProperty(
        name = "",
        description = "Factor to scale your models by for export",
        default = 1.0,
    )
# </type>

# <ui>
class List(bpy.types.UIList):
    """List of games"""
    bl_idname = "base.game_list"
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", emboss = False, translate = False)

class Add(bpy.types.Operator):
    """Add a game"""
    bl_idname = "base.game_add"
    bl_label = ""

    def execute(self, context):
        context.scene.BASE.games.add()
        return {'FINISHED'}

class Remove(bpy.types.Operator):
    """Remove the selected game from the list"""
    bl_idname = "base.game_remove"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return len(context.scene.BASE.games) > 0

    def execute(self, context):
        context.scene.BASE.games.remove(context.scene.BASE.game_index)
        context.scene.BASE.game_index = min(
            max(0, context.scene.BASE.game_index - 1),
            len(context.scene.BASE.games) - 1
        )
        return {'FINISHED'}

class Move(bpy.types.Operator):
    """Move the selected game up or down in the list"""
    bl_idname = "base.game_move"
    bl_label = ""

    direction = bpy.props.EnumProperty(items = (
        ('UP', "Up", ""),
        ('DOWN', "Down", ""),
    ))

    @classmethod
    def poll(cls, context):
        return len(context.scene.BASE.games) > 1

    def execute(self, context):
        neighbor = context.scene.BASE.game_index + (-1 if self.direction == 'UP' else 1)
        context.scene.BASE.games.move(neighbor, context.scene.BASE.game_index)
        list_length = len(context.scene.BASE.games) - 1
        context.scene.BASE.game_index = max(0, min(neighbor, list_length))
        return {'FINISHED'}

class Panel(bpy.types.Panel):
    bl_idname = "base.game_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE Model Export"
    bl_label = "Games"

    def draw(self, context):
        row = self.layout.row()
        row.template_list("base.game_list", "", context.scene.BASE, "games", context.scene.BASE, "game_index", rows = 4)
        col = row.column(align = True)
        col.operator("base.game_add", icon = 'ADD')
        col.operator("base.game_remove", icon = 'REMOVE')
        col.separator()
        col.operator("base.game_move", icon = 'TRIA_UP').direction = 'UP'
        col.operator("base.game_move", icon = 'TRIA_DOWN').direction = 'DOWN'

        games = context.scene.BASE.games
        game_index = context.scene.BASE.game_index

        if games and game_index >= 0:
            game = games[game_index]
            common.add_prop(self.layout, "Game Path", game, "path")
            common.add_prop(self.layout, "Model Scale", game, "scale")
# </ui>