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
        sourceops = utils.common.get_globals(context)
        game = utils.common.get_game(sourceops)
        model = utils.common.get_model(sourceops)
        return sourceops and game and model

    def invoke(self, context, event):
        sourceops = utils.common.get_globals(context)
        game = utils.common.get_game(sourceops)
        model = utils.common.get_model(sourceops)

        if not utils.game.verify(game):
            self.report({'ERROR'}, 'Game is invalid')
            return {'CANCELLED'}

        source_model = Model(game, model)

        if not source_model.compile_qc():
            self.report({'ERROR'}, 'Failed to compile QC')
            return {'CANCELLED'}

        self.report({'INFO'}, 'Compiled QC')
        return {'FINISHED'}
