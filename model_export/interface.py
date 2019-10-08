import bpy
from .. import common


class ModelList(bpy.types.UIList):
    """List of models"""
    bl_idname = "SOURCEOPS_UL_ModelList"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, translate=False)


class ModelExportPanel(bpy.types.Panel):
    """The parent panel for model export"""
    bl_idname = "SOURCEOPS_PT_ModelExportPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "SourceOps"
    bl_label = "Model Export"

    def draw_header(self, context):
        self.layout.label(icon='EXPORT')

    def draw(self, context):
        pass


class ModelPanel(bpy.types.Panel):
    """The panel for model list and some operators"""
    bl_idname = "SOURCEOPS_PT_ModelPanel"
    bl_parent_id = "SOURCEOPS_PT_ModelExportPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "SourceOps"
    bl_label = "Models"

    def draw_header(self, context):
        self.layout.label(icon='CUBE')

    def draw(self, context):
        g = common.get_globals(context)
        row = self.layout.row()
        row.template_list("SOURCEOPS_UL_ModelList", "", g, "models", g, "model_index", rows=4)
        col = row.column(align=True)
        col.operator("sourceops.add_model", text="", icon='ADD')
        col.operator("sourceops.remove_model", text="", icon='REMOVE')
        col.separator()
        col.operator("sourceops.move_model", text="", icon='TRIA_UP').direction = 'UP'
        col.operator("sourceops.move_model", text="", icon='TRIA_DOWN').direction = 'DOWN'

        if g.models:
            self.layout.operator("sourceops.export_meshes")
            self.layout.operator("sourceops.generate_qc")
            self.layout.operator("sourceops.edit_qc")
            self.layout.operator("sourceops.compile_qc")
            self.layout.operator("sourceops.view_model")

            model = g.models[g.model_index]
            common.add_prop(self.layout, "Reference", model, "reference")
            common.add_prop(self.layout, "Collision", model, "collision")
            common.add_prop(self.layout, "Bodygroups", model, "bodygroups")
            common.add_prop(self.layout, "Stacking", model, "stacking")


class PropertiesPanel(bpy.types.Panel):
    """The panel for model properties"""
    bl_idname = "SOURCEOPS_PT_PropertiesPanel"
    bl_parent_id = "SOURCEOPS_PT_ModelExportPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "SourceOps"
    bl_label = "Properties"

    @classmethod
    def poll(cls, context):
        return common.get_model(context)

    def draw_header(self, context):
        self.layout.label(icon='PROPERTIES')

    def draw(self, context):
        model = common.get_model(context)

        common.add_prop(self.layout, "Surface", model, "surface_prop")
        flow = self.layout.grid_flow(even_columns=True)
        col = flow.column()
        col.prop(model, "autocenter")
        col = flow.column()
        col.prop(model, "mostly_opaque")
