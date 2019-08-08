import bpy
from .. import common


class AddGame(bpy.types.Operator):
    """Add a game"""
    bl_idname = "sourceops.add_game"
    bl_label = "Add Game"

    def execute(self, context):
        settings = common.get_settings(context)
        settings.games.add()
        settings.game_index = len(settings.games) - 1
        return {'FINISHED'}


class RemoveGame(bpy.types.Operator):
    """Remove the selected game from the list"""
    bl_idname = "sourceops.remove_game"
    bl_label = "Remove Game"

    @classmethod
    def poll(cls, context):
        settings = common.get_settings(context)
        return len(settings.games) > 0

    def execute(self, context):
        settings = common.get_settings(context)
        settings.games.remove(settings.game_index)
        settings.game_index = min(
            max(0, settings.game_index - 1),
            len(settings.games) - 1
        )
        return {'FINISHED'}


class MoveGame(bpy.types.Operator):
    """Move the selected game up or down in the list"""
    bl_idname = "sourceops.move_game"
    bl_label = "Move Game"

    direction: bpy.props.EnumProperty(items=(
        ('UP', "Up", "Move the item up"),
        ('DOWN', "Down", "Move the item down"),
    ))

    @classmethod
    def poll(cls, context):
        settings = common.get_settings(context)
        return len(settings.games) > 1

    def execute(self, context):
        settings = common.get_settings(context)
        neighbor = settings.game_index + (-1 if self.direction == 'UP' else 1)
        settings.games.move(neighbor, settings.game_index)
        list_length = len(settings.games) - 1
        settings.game_index = max(0, min(neighbor, list_length))
        return {'FINISHED'}
