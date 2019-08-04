import os
import subprocess
import math
import bpy
import bmesh
import mathutils
from .. import common


class ViewModel(bpy.types.Operator):
    """Open this model in HLMV"""
    bl_idname = "base.view_model"
    bl_label = "View Model"

    @classmethod
    def poll(cls, context):
        base = context.scene.BASE
        settings = base.settings
        games = settings.games
        game_index = settings.game_index

        if games and game_index >= 0:
            game = games[game_index]

            if game.name != "Invalid Game":
                models = base.models
                model_index = base.model_index

                if models and model_index >= 0:
                    model = models[model_index]
                    return model.name

        return False

    def execute(self, context):
        base = context.scene.BASE
        settings = base.settings
        games = settings.games
        game_index = settings.game_index
        game = games[game_index]

        model = base.models[base.model_index]
        model_path = game.mod + os.sep + "models" + os.sep + model.name + ".mdl"
        dx90path = game.mod + os.sep + "models" + os.sep + model.name + ".dx90.vtx"

        args = [game.hlmv, "-game", game.mod, model_path]
        print(game.hlmv + "    " + model_path + "\n")

        if os.path.isfile(dx90path):
            subprocess.Popen(args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        else:
            self.report({"WARNING"}, "Model not found")

        return {'FINISHED'}
