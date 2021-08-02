import bpy
from .. import utils
from .. types . model_export . model import Model


class SOURCEOPS_OT_ExportAuto(bpy.types.Operator):
    bl_idname = 'sourceops.export_auto'
    bl_options = {'REGISTER'}
    bl_label = 'Export Auto'
    bl_description = 'Generate QC, export meshes, compile QC, view model.\nShift click to execute with last used settings'

    all_models: bpy.props.BoolProperty(name='All Models', description='Export all models in the scene', default=False)
    generate_qc: bpy.props.BoolProperty(name='Generate QC', description='Generate the QC based on your settings', default=True)
    export_meshes: bpy.props.BoolProperty(name='Export Meshes', description='Export the meshes and animations as SMD/FBX', default=True)
    compile_qc: bpy.props.BoolProperty(name='Compile QC', description='Compile the QC to an MDL', default=True)
    view_model: bpy.props.BoolProperty(name='View Model', description='Open the selected model in HLMV', default=False)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'all_models')

        col.prop(self, 'generate_qc')
        col.prop(self, 'export_meshes')
        col.prop(self, 'compile_qc')

        row = col.row()
        row.enabled = not self.all_models
        row.prop(self, 'view_model')

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

        if not utils.game.verify(game):
            self.report({'ERROR'}, 'Game is invalid')
            return {'CANCELLED'}

        if event.shift:
            return self.execute(context)
        else:
            return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        prefs = utils.common.get_prefs(context)
        game = utils.common.get_game(prefs)
        sourceops = utils.common.get_globals(context)

        if self.all_models:
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

        if self.generate_qc and not source_model.generate_qc():
            self.report({'ERROR'}, f'Failed to generate QC for {model.name}')
            return False

        if self.export_meshes and not source_model.export_meshes():
            self.report({'ERROR'}, f'Failed to export meshes for {model.name}')
            return False

        if self.compile_qc and not source_model.compile_qc():
            self.report({'ERROR'}, f'Failed to compile QC for {model.name}')
            return False

        if (not self.all_models and self.view_model) and not source_model.view_model():
            self.report({'ERROR'}, f'Failed to open HLMV for {model.name}')
            return False

        return True
