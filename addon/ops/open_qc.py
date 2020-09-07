import bpy
from .. import utils
from .. types . model_export . model import Model


class SOURCEOPS_OT_OpenQC(bpy.types.Operator):
    bl_idname = 'sourceops.open_qc'
    bl_options = {'REGISTER'}
    bl_label = 'Open QC'
    bl_description = 'Open this model\'s QC file in blender\'s text editor'

    @classmethod
    def poll(cls, context):
        prefs = utils.common.get_prefs(context)
        game = utils.common.get_game(prefs)
        sourceops = utils.common.get_globals(context)
        model = utils.common.get_model(sourceops)
        return prefs and game and sourceops and model

    def invoke(self, context, event):
        prefs = utils.common.get_prefs(context)
        game = utils.common.get_game(prefs)
        sourceops = utils.common.get_globals(context)
        model = utils.common.get_model(sourceops)

        if not utils.game.verify(game):
            self.report({'ERROR'}, 'Game is invalid')
            return {'CANCELLED'}

        source_model = Model(game, model)

        if not source_model.open_qc():
            self.report({'ERROR'}, 'Failed to open QC')
            return {'CANCELLED'}

        self.report({'INFO'}, 'Opened QC')
        return {'FINISHED'}
