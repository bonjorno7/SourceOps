import bpy
from .. import utils
from .. types . model_export . model import Model


class SOURCEOPS_OT_ExportMeshes(bpy.types.Operator):
    bl_idname = 'sourceops.export_meshes'
    bl_options = {'REGISTER'}
    bl_label = 'Export Meshes'
    bl_description = 'Export this model\'s meshes'

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

        if not source_model.export_meshes():
            self.report({'ERROR'}, 'Failed to export meshes')
            return {'CANCELLED'}

        self.report({'INFO'}, 'Exported meshes')
        return {'FINISHED'}
