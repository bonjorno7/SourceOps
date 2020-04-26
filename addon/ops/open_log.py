import bpy
from .. utils import common
from .. types . model_export . model import Model


class SOURCEOPS_OT_OpenLog(bpy.types.Operator):
    bl_idname = 'sourceops.open_log'
    bl_options = {'REGISTER'}
    bl_label = 'Open Log'
    bl_description = 'Open this model\'s compile log in blender\'s text editor'

    @classmethod
    def poll(cls, context):
        sourceops = common.get_globals(context)
        game = common.get_game(sourceops)
        model = common.get_model(sourceops)
        return sourceops and game and model

    def invoke(self, context, event):
        sourceops = common.get_globals(context)
        game = common.get_game(sourceops)
        model = common.get_model(sourceops)

        if not common.verify_game(game):
            self.report({'ERROR'}, 'Game is invalid')
            return {'CANCELLED'}

        source_model = Model(game, model)

        if not source_model.open_log():
            self.report({'ERROR'}, 'Failed to open log')
            return {'CANCELLED'}

        self.report({'INFO'}, 'Opened log')
        return {'FINISHED'}
