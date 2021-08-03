import bpy
from .. import utils
from .. types . model_export . model import Model


class SOURCEOPS_OT_CompileQC(bpy.types.Operator):
    bl_idname = 'sourceops.compile_qc'
    bl_options = {'REGISTER'}
    bl_label = 'Compile QC'
    bl_description = 'Compile this model\'s QC file'

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
        error = source_model.compile_qc()

        if error:
            self.report({'ERROR'}, error)
            return {'CANCELLED'}

        self.report({'INFO'}, 'Compiled QC')
        return {'FINISHED'}
