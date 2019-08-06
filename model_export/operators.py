import bpy
from .. import common


class AddModel(bpy.types.Operator):
    """Create a model"""
    bl_idname = "base.add_model"
    bl_label = "Add Model"

    def execute(self, context):
        base = common.get_globals(context)
        base.models.add()
        base.model_index = len(base.models) - 1
        return {'FINISHED'}


class RemoveModel(bpy.types.Operator):
    """Remove the selected model"""
    bl_idname = "base.remove_model"
    bl_label = "Remove Model"

    @classmethod
    def poll(cls, context):
        base = common.get_globals(context)
        return len(base.models) > 0

    def execute(self, context):
        base = common.get_globals(context)
        base.models.remove(base.model_index)
        base.model_index = min(
            max(0, base.model_index - 1),
            len(base.models) - 1
        )
        return {'FINISHED'}


class MoveModel(bpy.types.Operator):
    """Move the selected model up or down in the list"""
    bl_idname = "base.move_model"
    bl_label = "Move Model"

    direction: bpy.props.EnumProperty(items=(
        ('UP', "Up", "Move the item up"),
        ('DOWN', "Down", "Move the item down"),
    ))

    @classmethod
    def poll(cls, context):
        base = common.get_globals(context)
        return len(base.models) > 1

    def execute(self, context):
        base = common.get_globals(context)
        neighbor = base.model_index + (-1 if self.direction == 'UP' else 1)
        base.models.move(neighbor, base.model_index)
        list_length = len(base.models) - 1
        base.model_index = max(0, min(neighbor, list_length))
        return {'FINISHED'}


class ExportModel(bpy.types.Operator):
    """Export this model's meshes, generate a QC and compile it"""
    bl_idname = "base.export_model"
    bl_label = "Export Model"

    @classmethod
    def poll(cls, context):
        game = common.get_game(context)
        if game and game.is_valid():
            model = common.get_model(context)
            return model and model.name

    def execute(self, context):
        model = common.get_model()
        if not model.export(context):
            self.report({"WARNING"}, "Failed to export")
        return {'FINISHED'}


class ViewModel(bpy.types.Operator):
    """Open this model in HLMV"""
    bl_idname = "base.view_model"
    bl_label = "View Model"

    @classmethod
    def poll(cls, context):
        game = common.get_game(context)
        if game and game.is_valid():
            model = common.get_model(context)
            return model and model.name

    def execute(self, context):
        model = common.get_model()
        if not model.view(context):
            self.report({"WARNING"}, "Model not found")
        return {'FINISHED'}
