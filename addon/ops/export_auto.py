import bpy
from .. utils import common
from .. types . model_export . model import Model


class SOURCEOPS_OT_ExportAuto(bpy.types.Operator):
    bl_idname = 'sourceops.export_auto'
    bl_options = {'REGISTER'}
    bl_label = 'Export Auto'
    bl_description = 'Export '

    @classmethod
    def poll(cls, context):
        sourceops = common.get_globals(context)
        game = common.get_game(sourceops)
        model = common.get_model(sourceops)
        return sourceops and game and model

    def invoke(self, context, event):
        sourceops = common.get_globals(context)
        game = common.get_game(sourceops)

        if not common.verify_game(game):
            self.report({'ERROR'}, 'Game is invalid')
            return {'CANCELLED'}

        for model in sourceops.model_items:
            source_model = Model(game, model)

            if not source_model.generate_qc():
                self.report({'ERROR'}, f'Failed to generate QC for {model.display}')
                return {'CANCELLED'}

            if not source_model.export_meshes():
                self.report({'ERROR'}, f'Failed to export meshes for {model.display}')
                return {'CANCELLED'}

            if not source_model.compile_qc():
                self.report({'ERROR'}, f'Failed to compile QC for {model.display}')
                return {'CANCELLED'}

        self.report({'INFO'}, 'Exported Everything')
        return {'FINISHED'}
