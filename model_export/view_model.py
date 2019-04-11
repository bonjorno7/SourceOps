# <import>
import os, subprocess, math
import bpy, bmesh, mathutils
from .. import common
# </import>

# <operators>
class BASE_OT_ViewModel(bpy.types.Operator):
    """Open this model in HLMV"""
    bl_idname = "base.view_model"
    bl_label = "View Model"

    @classmethod
    def poll(cls, context):
        settings = context.scene.BASE.settings
        games = settings.games
        game_index = settings.game_index

        if games and game_index >= 0:
            game = games[game_index]

            if game.path:
                models = context.scene.BASE.models
                model_index = context.scene.BASE.model_index

                if models and model_index >= 0:
                    model = models[model_index]
                    return model.name and model.meshes

        return False

    def execute(self, context):
        settings = context.scene.BASE.settings
        game_path = settings.games[settings.game_index].path
        model = context.scene.BASE.models[context.scene.BASE.model_index]
        model_path = game_path + os.sep + "models" + os.sep + model.name + ".mdl"
        dx90path = game_path + os.sep + "models" + os.sep + model.name + ".dx90.vtx"

        hlmv = os.path.split(game_path)[0] + "\\bin\\hlmv.exe"
        args = [hlmv, "-game", game_path, model_path]
        print(hlmv + "    " + model_path + "\n")

        if os.path.isfile(hlmv):
            if os.path.isfile(dx90path):
                subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            else: self.report({"WARNING"}, "Model not found")
        else: self.report({'ERROR'}, "HLMV not found, your game path is invalid")

        return {'FINISHED'}
# </operators>