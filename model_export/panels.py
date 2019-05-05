import bpy
from .. import common


class ModelExportPanel(bpy.types.Panel):
    bl_idname = "BASE_PT_ModelExportPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Model Export"

    def draw_header(self, context):
        self.layout.label(icon='EXPORT')

    def draw(self, context):
        pass


class ModelPanel(bpy.types.Panel):
    bl_idname = "BASE_PT_ModelPanel"
    bl_parent_id = "BASE_PT_ModelExportPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Models"

    def draw_header(self, context):
        self.layout.label(icon='CUBE')

    def draw(self, context):
        base = context.scene.BASE
        row = self.layout.row()
        row.template_list("BASE_UL_ModelList", "", base,
                          "models", base, "model_index", rows=4)
        col = row.column(align=True)
        col.operator("base.add_model", text="", icon='ADD')
        col.operator("base.remove_model", text="", icon='REMOVE')
        col.separator()
        col.operator("base.move_model", text="",
                     icon='TRIA_UP').direction = 'UP'
        col.operator("base.move_model", text="",
                     icon='TRIA_DOWN').direction = 'DOWN'

        flow = self.layout.grid_flow(even_columns=True)
        col = flow.column()
        col.operator("base.export_model")
        col = flow.column()
        col.operator("base.view_model")


class MeshPanel(bpy.types.Panel):
    bl_idname = "BASE_PT_MeshPanel"
    bl_parent_id = "BASE_PT_ModelExportPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Meshes"

    @classmethod
    def poll(cls, context):
        models = context.scene.BASE.models
        model_index = context.scene.BASE.model_index
        return models and model_index >= 0

    def draw_header(self, context):
        self.layout.label(icon='MESH_DATA')

    def draw(self, context):
        models = context.scene.BASE.models
        model_index = context.scene.BASE.model_index
        model = models[model_index]

        row = self.layout.row()
        row.template_list("BASE_UL_MeshList", "", model,
                          "meshes", model, "mesh_index", rows=4)
        col = row.column(align=True)
        col.operator("base.add_mesh", text="", icon='ADD')
        col.operator("base.remove_mesh", text="", icon='REMOVE')
        col.separator()
        col.operator("base.move_mesh", text="",
                     icon='TRIA_UP').direction = 'UP'
        col.operator("base.move_mesh", text="",
                     icon='TRIA_DOWN').direction = 'DOWN'


class PropertiesPanel(bpy.types.Panel):
    bl_idname = "BASE_PT_PropertiesPanel"
    bl_parent_id = "BASE_PT_ModelExportPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Properties"

    @classmethod
    def poll(cls, context):
        models = context.scene.BASE.models
        model_index = context.scene.BASE.model_index
        return models and model_index >= 0

    def draw_header(self, context):
        self.layout.label(icon='PROPERTIES')

    def draw(self, context):
        models = context.scene.BASE.models
        model_index = context.scene.BASE.model_index
        model = models[model_index]

        common.add_prop(self.layout, "Surface", model, "surface_prop")
        flow = self.layout.grid_flow(even_columns=True)
        col = flow.column()
        col.prop(model, "autocenter")
        col = flow.column()
        col.prop(model, "mostly_opaque")
