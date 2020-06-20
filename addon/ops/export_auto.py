import bpy
from .. utils import common
from .. types . model_export . model import Model


class SOURCEOPS_OT_ExportAuto(bpy.types.Operator):
    bl_idname = 'sourceops.export_auto'
    bl_options = {'REGISTER'}
    bl_label = 'Export Auto'
    bl_description = '''Generate QC, export meshes, and compile QC
Shift click to do this for all models in the scene'''

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

        if event.shift:
            for model in sourceops.model_items:
                if not self.export(game, model):
                    return {'CANCELLED'}

            self.report({'INFO'}, 'Exported all models in the scene')
            return {'FINISHED'}

        else:
            model = common.get_model(sourceops)
            if not self.export(game, model):
                return {'CANCELLED'}

            self.report({'INFO'}, f'Exported {model.display}')
            return {'FINISHED'}

    def export(self, game, model):
        source_model = Model(game, model)

        if not source_model.generate_qc():
            self.report({'ERROR'}, f'Failed to generate QC for {model.display}')
            return False

        if not source_model.export_meshes():
            self.report({'ERROR'}, f'Failed to export meshes for {model.display}')
            return False

        if not source_model.compile_qc():
            self.report({'ERROR'}, f'Failed to compile QC for {model.display}')
            return False

        return True
