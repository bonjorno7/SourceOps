import bpy
from .. ui . panels import SOURCEOPS_PT_MainPanel


class SOURCEOPS_OT_CallPanel(bpy.types.Operator, SOURCEOPS_PT_MainPanel):
    bl_idname = 'sourceops.call_panel'
    bl_options = {'REGISTER'}
    bl_label = 'SourceOps Panel'
    bl_description = 'Display the SourceOps panel'

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self, context):
        return {'FINISHED'}

    def check(self, context):
        return True
