import bpy
from .. import common


class GameList(bpy.types.UIList):
    """List of games"""
    bl_idname = "BASE_UL_GameList"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.name)


class SettingsPanel(bpy.types.Panel):
    bl_idname = "BASE_PT_SettingsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Settings"

    def draw_header(self, context):
        self.layout.label(icon='PREFERENCES')

    def draw(self, context):
        pass


class OptionsPanel(bpy.types.Panel):
    bl_idname = "BASE_PT_OptionsPanel"
    bl_parent_id = "BASE_PT_SettingsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Options"

    def draw_header(self, context):
        self.layout.label(icon='SETTINGS')

    def draw(self, context):
        settings = context.scene.BASE.settings
        common.add_prop(self.layout, "Model Scale", settings, "scale")


class GamesPanel(bpy.types.Panel):
    bl_idname = "BASE_PT_GamesPanel"
    bl_parent_id = "BASE_PT_SettingsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Games"

    def draw_header(self, context):
        self.layout.label(icon='TOOL_SETTINGS')

    def draw(self, context):
        settings = context.scene.BASE.settings

        row = self.layout.row()
        row.template_list("BASE_UL_GameList", "", settings,
                          "games", settings, "game_index", rows=4)
        col = row.column(align=True)
        col.operator("base.add_game", text="", icon='ADD')
        col.operator("base.remove_game", text="", icon='REMOVE')
        col.separator()
        col.operator("base.move_game", text="",
                     icon='TRIA_UP').direction = 'UP'
        col.operator("base.move_game", text="",
                     icon='TRIA_DOWN').direction = 'DOWN'

        games = settings.games
        game_index = settings.game_index

        if games and game_index >= 0:
            game = games[game_index]
            self.layout.row().prop(game, "gameinfo", text="")
