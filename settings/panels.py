# <import>
import os, subprocess, math
import bpy, bmesh, mathutils
from .. import common
# </import>

# <panels>
class BASE_PT_SettingsPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Settings"

    def draw_header(self, context):
        self.layout.label(icon = 'PREFERENCES')

    def draw(self, context):
        pass

class BASE_PT_OptionsPanel(bpy.types.Panel):
    bl_parent_id = "BASE_PT_SettingsPanel"
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

class BASE_PT_GamesPanel(bpy.types.Panel):
    bl_parent_id = "BASE_PT_SettingsPanel"
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
        row.template_list("BASE_UL_GameList", "", settings, "games", settings, "game_index", rows = 4)
        col = row.column(align = True)
        col.operator("base.add_game", text = "", icon = 'ADD')
        col.operator("base.remove_game", text = "", icon = 'REMOVE')
        col.separator()
        col.operator("base.move_game", text = "", icon = 'TRIA_UP').direction = 'UP'
        col.operator("base.move_game", text = "", icon = 'TRIA_DOWN').direction = 'DOWN'

        games = settings.games
        game_index = settings.game_index

        if games and game_index >= 0:
            game = games[game_index]
            self.layout.row().prop(game, "path", text = "")
# </panels>