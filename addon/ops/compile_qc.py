import bpy
from .. utils import common
from .. types . model import Model


class SOURCEOPS_OT_CompileQC(bpy.types.Operator):
    bl_idname = 'sourceops.compile_qc'
    bl_options = {'REGISTER'}
    bl_label = 'Compile QC'
    bl_description = 'Compile this model\'s QC file'

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

        if not source_model.compile_qc():
            self.report({'ERROR'}, 'Failed to compile QC')
            return {'CANCELLED'}

        self.report({'INFO'}, 'Compiled QC')
        return {'FINISHED'}
