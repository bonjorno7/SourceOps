import bpy
import time
from threading import Lock, Thread
from .. import utils
from .. types . model_export . model import Model


class SOURCEOPS_OT_ExportAuto(bpy.types.Operator):
    bl_idname = 'sourceops.export_auto'
    bl_options = {'REGISTER'}
    bl_label = 'Export Auto'
    bl_description = 'Export meshes, generate QC, compile QC, view model.\nShift click to export all models.\nCtrl click to customize export steps'

    ctrl: bpy.props.BoolProperty(name='Ctrl', description='Whether Ctrl was held during invoke', options={'HIDDEN', 'SKIP_SAVE'})
    shift: bpy.props.BoolProperty(name='Shift', description='Whether Shift was held during invoke', options={'HIDDEN', 'SKIP_SAVE'})

    all_models: bpy.props.BoolProperty(name='All Models', description='Export all models in the scene', default=False)
    export_meshes: bpy.props.BoolProperty(name='Export Meshes', description='Export the meshes and animations as SMD/FBX', default=True)
    generate_qc: bpy.props.BoolProperty(name='Generate QC', description='Generate the QC based on your settings', default=True)
    compile_qc: bpy.props.BoolProperty(name='Compile QC', description='Compile the QC to an MDL', default=True)
    view_model: bpy.props.BoolProperty(name='View Model', description='Open the selected model in HLMV', default=False)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'all_models')

        col.prop(self, 'export_meshes')
        col.prop(self, 'generate_qc')
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

        self.ctrl = event.ctrl
        self.shift = event.shift

        if self.ctrl:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)

    def execute(self, context):
        prefs = utils.common.get_prefs(context)
        game = utils.common.get_game(prefs)
        sourceops = utils.common.get_globals(context)

        start = time.time()

        if (not self.ctrl and self.shift) or (self.ctrl and self.all_models):
            source_models = [Model(game, model) for model in sourceops.model_items]

            for source_model in source_models:
                error = self.export(source_model)
                if error:
                    self.report({'ERROR'}, error)
                    return {'CANCELLED'}

            threads = [Thread(target=self.compile, args=[m], daemon=True) for m in source_models]
            self._lock = Lock()
            self._results = []

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            for error in self._results:
                self.report({'ERROR'}, error)

            if self._results:
                return {'CANCELLED'}

            self.report({'INFO'}, f'Exported all models in the scene in {round(time.time() - start, 1)} seconds')
            return {'FINISHED'}

        else:
            model = utils.common.get_model(sourceops)
            source_model = Model(game, model)

            error = self.export(source_model)
            if error:
                self.report({'ERROR'}, error)
                return {'CANCELLED'}

            error = self.compile(source_model)
            if error:
                self.report({'ERROR'}, error)
                return {'CANCELLED'}

            self.report({'INFO'}, f'Exported {model.name} in {round(time.time() - start, 1)} seconds')
            return {'FINISHED'}

    def export(self, source_model: Model):
        if not self.ctrl or self.export_meshes:
            error = source_model.export_meshes()
            if error:
                return error

        if not self.ctrl or self.generate_qc:
            error = source_model.generate_qc()
            if error:
                return error

    def compile(self, source_model: Model):
        if not self.ctrl or self.compile_qc:
            error = source_model.compile_qc()
            if error:
                with self._lock:
                    self._results.append(error)
                return

        if self.ctrl and (not self.all_models and self.view_model):
            error = source_model.view_model()
            if error:
                with self._lock:
                    self._results.append(error)
                return
