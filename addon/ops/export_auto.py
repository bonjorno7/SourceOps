import bpy
from .. import utils
from .. types . model_export . model import Model


class SOURCEOPS_OT_ExportAuto(bpy.types.Operator):
    bl_idname = 'sourceops.export_auto'
    bl_options = {'REGISTER'}
    bl_label = 'Export Auto'
    bl_description = '''Generate QC, export meshes, and compile QC
Shift click to do this for all models in the scene'''

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

        if not utils.game.verify(game):
            self.report({'ERROR'}, 'Game is invalid')
            return {'CANCELLED'}

        if event.shift:
            for model in sourceops.model_items:
                if not self.export(game, model):
                    return {'CANCELLED'}

            self.report({'INFO'}, 'Exported all models in the scene')
            return {'FINISHED'}

        else:
            model = utils.common.get_model(sourceops)
            if not self.export(game, model):
                return {'CANCELLED'}

            self.report({'INFO'}, f'Exported {model.name}')
            return {'FINISHED'}

    def export(self, game, model):
        source_model = Model(game, model)

        if not source_model.generate_qc():
            self.report({'ERROR'}, f'Failed to generate QC for {model.name}')
            return False

        if not source_model.export_meshes():
            self.report({'ERROR'}, f'Failed to export meshes for {model.name}')
            return False

        if not source_model.compile_qc():
            self.report({'ERROR'}, f'Failed to compile QC for {model.name}')
            return False

        return True
