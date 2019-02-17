# <import>
import bpy
from . import common
# </import>

# </types>
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

class Settings(bpy.types.PropertyGroup):
    games = bpy.props.CollectionProperty(type = Game)
    game_index = bpy.props.IntProperty(name = "", default = 0)

    scale = bpy.props.FloatProperty(
        name = "",
        description = "Factor to scale your models by for export",
        default = 1.0,
    )
# </types>

# <game list>
class GameList(bpy.types.UIList):
    """List of games"""
    bl_idname = "base.game_list"
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", emboss = False, translate = False)

class GameAdd(bpy.types.Operator):
    """Add a game"""
    bl_idname = "base.game_add"
    bl_label = ""

    def execute(self, context):
        settings = context.scene.BASE.settings
        settings.games.add()
        return {'FINISHED'}

class GameRemove(bpy.types.Operator):
    """Remove the selected game from the list"""
    bl_idname = "base.game_remove"
    bl_label = ""

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
# </game list>

# <panel>
class SettingsPanel(bpy.types.Panel):
    bl_idname = "base.settings_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Settings"

    def draw(self, context):
        settings = context.scene.BASE.settings
        box = self.layout.box()
        box.label(text = "Options", icon = 'PREFERENCES')
        common.add_prop(box, "Model Scale", settings, "scale")

        box = self.layout.box()
        box.label(text = "Games", icon = 'TOOL_SETTINGS')
        row = box.row()
        row.template_list("base.game_list", "", settings, "games", settings, "game_index", rows = 3)
        col = row.column(align = True)
        col.operator("base.game_add", icon = 'ADD')
        col.operator("base.game_remove", icon = 'REMOVE')

        games = settings.games
        game_index = settings.game_index

        if games and game_index >= 0:
            game = games[game_index]
            common.add_prop(box, "Game Path", game, "path")
# </panel>