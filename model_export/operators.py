import bpy
from .. import common


class AddModel(bpy.types.Operator):
    """Create a model"""
    bl_idname = "sourceops.add_model"
    bl_label = "Add Model"

    def execute(self, context):
        g = common.get_globals(context)
        g.models.add()
        g.model_index = len(g.models) - 1
        return {'FINISHED'}


class RemoveModel(bpy.types.Operator):
    """Remove the selected model"""
    bl_idname = "sourceops.remove_model"
    bl_label = "Remove Model"

    @classmethod
    def poll(cls, context):
        g = common.get_globals(context)
        return len(g.models) > 0

    def execute(self, context):
        g = common.get_globals(context)
        g.models.remove(g.model_index)
        g.model_index = min(
            max(0, g.model_index - 1),
            len(g.models) - 1
        )
        return {'FINISHED'}


class MoveModel(bpy.types.Operator):
    """Move the selected model up or down in the list"""
    bl_idname = "sourceops.move_model"
    bl_label = "Move Model"

    direction: bpy.props.EnumProperty(items=(
        ('UP', "Up", "Move the item up"),
        ('DOWN', "Down", "Move the item down"),
    ))

    @classmethod
    def poll(cls, context):
        g = common.get_globals(context)
        return len(g.models) > 1

    def execute(self, context):
        g = common.get_globals(context)
        neighbor = g.model_index + (-1 if self.direction == 'UP' else 1)
        g.models.move(neighbor, g.model_index)
        list_length = len(g.models) - 1
        g.model_index = max(0, min(neighbor, list_length))
        return {'FINISHED'}


class ExportMeshes(bpy.types.Operator):
    """Export this model's meshes"""
    bl_idname = "sourceops.export_meshes"
    bl_label = "Export Meshes"

    @classmethod
    def poll(cls, context):
        game = common.get_game(context)
        if game and game.is_valid():
            model = common.get_model(context)
            return model and model.name

    def execute(self, context):
        model = common.get_model(context)
        if not model.export_meshes(context):
            self.report({"WARNING"}, "Failed to export meshes")
        return {'FINISHED'}


class GenerateQC(bpy.types.Operator):
    """Generate the QC file for this model"""
    bl_idname = "sourceops.generate_qc"
    bl_label = "Generate QC"

    @classmethod
    def poll(cls, context):
        game = common.get_game(context)
        if game and game.is_valid():
            model = common.get_model(context)
            return model and model.name

    def execute(self, context):
        model = common.get_model(context)
        if not model.generate_qc(context):
            self.report({"WARNING"}, "Failed to generate QC")
        return {'FINISHED'}


class CompileQC(bpy.types.Operator):
    """Compile this model using the QC"""
    bl_idname = "sourceops.compile_qc"
    bl_label = "Compile QC"

    @classmethod
    def poll(cls, context):
        game = common.get_game(context)
        if game and game.is_valid():
            model = common.get_model(context)
            return model and model.name

    def execute(self, context):
        model = common.get_model(context)
        if not model.compile_qc(context):
            self.report({"WARNING"}, "Failed to compile QC")
        return {'FINISHED'}


class ViewModel(bpy.types.Operator):
    """Open this model in HLMV"""
    bl_idname = "sourceops.view_model"
    bl_label = "View Model"

    @classmethod
    def poll(cls, context):
        game = common.get_game(context)
        if game and game.is_valid():
            model = common.get_model(context)
            return model and model.name

    def execute(self, context):
        model = common.get_model(context)
        if not model.view(context):
            self.report({"WARNING"}, "Model not found")
        return {'FINISHED'}
