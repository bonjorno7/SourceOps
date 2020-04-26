import bpy
from .. utils import common
from .. types . model_export . model import Model


class SOURCEOPS_OT_ViewModel(bpy.types.Operator):
    bl_idname = 'sourceops.view_model'
    bl_options = {'REGISTER'}
    bl_label = 'View Model'
    bl_description = 'View this model in HLMV'

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

        if not source_model.view_model():
            self.report({'ERROR'}, 'Failed to open model in HLMV')
            return {'CANCELLED'}

        self.report({'INFO'}, 'Viewing model in HLMV')
        return {'FINISHED'}
