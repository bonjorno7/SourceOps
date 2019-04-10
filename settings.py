# <import>
import os, bpy
from . import common
# </import>

# <functions>
def update_path(self, context):
    self["path"] = os.path.realpath(bpy.path.abspath(self["path"]))
    self["name"] = os.path.basename(os.path.realpath(self["path"] + common.dir_up))
    #if not os.path.isdir(self["path"]): self.report({'WARNING'}, "Invalid game path")
# </functions>

# </types>
class BASE_PG_Game(bpy.types.PropertyGroup):
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

class BASE_PG_Settings(bpy.types.PropertyGroup):
    """Properties for the Settings panel"""
    games: bpy.props.CollectionProperty(type = BASE_PG_Game)
    game_index: bpy.props.IntProperty(default = 0)

    scale: bpy.props.FloatProperty(
        name = "Model Scale",
        description = "Factor to scale your models by for export",
        default = 1.0,
    )
# </types>

# <game list>
class BASE_UL_Game(bpy.types.UIList):
    """List of games"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text = item.name)

class BASE_OT_GameAdd(bpy.types.Operator):
    """Add a game"""
    bl_idname = "base.game_add"
    bl_label = "Add Game"

    def execute(self, context):
        settings = context.scene.BASE.settings
        settings.games.add()
        settings.game_index = len(settings.games) - 1
        return {'FINISHED'}

class BASE_OT_GameRemove(bpy.types.Operator):
    """Remove the selected game from the list"""
    bl_idname = "base.game_remove"
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

class BASE_OT_GameMove(bpy.types.Operator):
    """Move the selected game up or down in the list"""
    bl_idname = "base.game_move"
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
# </game list>

# <panels>
class BASE_PT_Settings(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Settings"

    def draw_header(self, context):
        self.layout.label(icon = 'PREFERENCES')

    def draw(self, context):
        pass

class BASE_PT_Options(bpy.types.Panel):
    bl_parent_id = "BASE_PT_Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Options"

    def draw_header(self, context):
        self.layout.label(icon = 'SETTINGS')

    def draw(self, context):
        settings = context.scene.BASE.settings
        common.add_prop(self.layout, "Model Scale", settings, "scale")

class BASE_PT_Games(bpy.types.Panel):
    bl_parent_id = "BASE_PT_Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Games"

    def draw_header(self, context):
        self.layout.label(icon = 'TOOL_SETTINGS')

    def draw(self, context):
        settings = context.scene.BASE.settings

        row = self.layout.row()
        row.template_list("BASE_UL_Game", "", settings, "games", settings, "game_index", rows = 4)
        col = row.column(align = True)
        col.operator("base.game_add", text = "", icon = 'ADD')
        col.operator("base.game_remove", text = "", icon = 'REMOVE')
        col.separator()
        col.operator("base.game_move", text = "", icon = 'TRIA_UP').direction = 'UP'
        col.operator("base.game_move", text = "", icon = 'TRIA_DOWN').direction = 'DOWN'

        games = settings.games
        game_index = settings.game_index

        if games and game_index >= 0:
            game = games[game_index]
            common.add_prop(self.layout, "Path", game, "path")
# </panels>