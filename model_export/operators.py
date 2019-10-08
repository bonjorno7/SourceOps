import os
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

    def execute(self, context):
        game = common.get_game(context)
        if not game or not game.verify():
            self.report({'ERROR'}, "Game is invalid")
            return {'CANCELLED'}

        model = common.get_model(context)
        if not model:
            self.report({'ERROR'}, "Model is invalid")
            return {'CANCELLED'}

        if not model.export_meshes(context):
            self.report({'ERROR'}, "Failed to export meshes")
            return {'CANCELLED'}

        self.report({'INFO'}, "Exported meshes")
        return {'FINISHED'}


class GenerateQC(bpy.types.Operator):
    """Generate the QC file for this model"""
    bl_idname = "sourceops.generate_qc"
    bl_label = "Generate QC"

    def execute(self, context):
        game = common.get_game(context)
        if not game or not game.verify():
            self.report({'ERROR'}, "Game is invalid")
            return {'CANCELLED'}

        model = common.get_model(context)
        if not model:
            self.report({'ERROR'}, "Model is invalid")
            return {'CANCELLED'}

        if not model.generate_qc(context):
            self.report({'ERROR'}, "Failed to generate QC")
            return {'CANCELLED'}

        self.report({'INFO'}, "Generated QC")
        return {'FINISHED'}


class EditQC(bpy.types.Operator):
    """Edit the QC file for this model"""
    bl_idname = "sourceops.edit_qc"
    bl_label = "Edit QC"

    def execute(self, context):
        game = common.get_game(context)
        if not game or not game.verify():
            self.report({'ERROR'}, "Game is invalid")
            return {'CANCELLED'}

        model = common.get_model(context)
        if not model:
            self.report({'ERROR'}, "Model is invalid")
            return {'CANCELLED'}

        if not model.edit_qc(context):
            self.report({'ERROR'}, "Failed to open QC")
            return {'CANCELLED'}

        self.report({'INFO'}, "Opened QC in blender text editor")
        return {'FINISHED'}


class CompileQC(bpy.types.Operator):
    """Compile this model using the QC"""
    bl_idname = "sourceops.compile_qc"
    bl_label = "Compile QC"

    def execute(self, context):
        game = common.get_game(context)
        if not game or not game.verify():
            self.report({'ERROR'}, "Game is invalid")
            return {'CANCELLED'}

        model = common.get_model(context)
        if not model:
            self.report({'ERROR'}, "Model is invalid")
            return {'CANCELLED'}

        if not model.compile_qc(context):
            self.report({'ERROR'}, "Failed to compile QC")
            return {'CANCELLED'}

        self.report({'INFO'}, "Compiled QC")
        return {'FINISHED'}


class ViewModel(bpy.types.Operator):
    """Open this model in HLMV"""
    bl_idname = "sourceops.view_model"
    bl_label = "View Model"

    def execute(self, context):
        game = common.get_game(context)
        if not game or not game.verify():
            self.report({'ERROR'}, "Game is invalid")
            return {'CANCELLED'}

        model = common.get_model(context)
        if not model:
            self.report({'ERROR'}, "Model is invalid")
            return {'CANCELLED'}

        if not model.view(context):
            self.report({'ERROR'}, "Model not found")
            return {'CANCELLED'}

        self.report({'INFO'}, "Opening HLMV")
        return {'FINISHED'}
