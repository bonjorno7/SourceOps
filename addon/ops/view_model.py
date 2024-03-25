import bpy
from .. import utils
from .. types . model_export . model import Model


class SOURCEOPS_OT_ViewModel(bpy.types.Operator):
    bl_idname = 'sourceops.view_model'
    bl_options = {'REGISTER'}
    bl_label = 'View Model'
    bl_description = 'View this model in HLMV'

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
        error = source_model.view_model()

        if error:
            self.report({'ERROR'}, error)
            return {'CANCELLED'}

        plusplus = '++' if source_model.hlmv.stem.endswith('plusplus') else ''
        self.report({'INFO'}, f'Viewing model in HLMV{plusplus}')
        return {'FINISHED'}
