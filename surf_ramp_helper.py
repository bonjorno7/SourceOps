# <SETTING UP>

# <add-on definitions>
bl_info = {
    "name": "Surf Ramp Helper",
    "author": "bonjorno7",
    "version": (0, 3),
    "blender": (2, 80, 0),
    "location": "3D View > Sidebar",
    "description": "Adds modifiers to a surf ramp profile",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
}
# </add-on definitions>

# <importing libraries>
import bpy
from bpy.types import Operator, Menu, Panel, PropertyGroup
# </importing libraries>

# </SETTING UP>



# <THE ACTUAL CODE>

# <functions>
def add_modifiers_ramp_textured(self, context):
    for o in bpy.context.selected_objects:
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_add(type='TRIANGULATE')
        bpy.context.object.modifiers["Triangulate"].show_in_editmode = False
        bpy.context.object.modifiers["Triangulate"].quad_method = 'FIXED'
        bpy.ops.object.modifier_add(type='ARRAY')
        bpy.context.object.modifiers["Array"].show_in_editmode = False
        bpy.context.object.modifiers["Array"].fit_type = 'FIT_CURVE'
        bpy.context.object.modifiers["Array"].relative_offset_displace[0] = 0.0
        bpy.context.object.modifiers["Array"].relative_offset_displace[1] = 0.0
        bpy.context.object.modifiers["Array"].relative_offset_displace[2] = 1.0
        bpy.context.object.modifiers["Array"].use_merge_vertices = True
        bpy.context.object.modifiers["Array"].use_merge_vertices_cap = True
        bpy.ops.object.modifier_add(type='CURVE')
        bpy.context.object.modifiers["Curve"].deform_axis = 'POS_Z'
        o.data.use_auto_smooth = True
        for f in o.data.polygons: f.use_smooth = True

def add_modifiers_ramp_cap(self, context):
    for o in bpy.context.selected_objects:
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_add(type='TRIANGULATE')
        bpy.context.object.modifiers["Triangulate"].show_in_editmode = False
        bpy.context.object.modifiers["Triangulate"].quad_method = 'FIXED'
        o.data.use_auto_smooth = True
        for f in o.data.polygons: f.use_smooth = True

def add_modifiers_ramp_hull(self, context):
    for o in bpy.context.selected_objects:
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_add(type='TRIANGULATE')
        bpy.context.object.modifiers["Triangulate"].show_in_editmode = False
        bpy.context.object.modifiers["Triangulate"].quad_method = 'FIXED'
        bpy.ops.object.modifier_add(type='ARRAY')
        bpy.context.object.modifiers["Array"].show_in_editmode = False
        bpy.context.object.modifiers["Array"].fit_type = 'FIT_CURVE'
        bpy.context.object.modifiers["Array"].relative_offset_displace[0] = 0.0
        bpy.context.object.modifiers["Array"].relative_offset_displace[1] = 0.0
        bpy.context.object.modifiers["Array"].relative_offset_displace[2] = 1.0
        bpy.context.object.modifiers["Array"].use_merge_vertices = False
        bpy.context.object.modifiers["Array"].use_merge_vertices_cap = False
        bpy.ops.object.modifier_add(type='CURVE')
        bpy.context.object.modifiers["Curve"].deform_axis = 'POS_Z'
        o.data.use_auto_smooth = False
        for f in o.data.polygons: f.use_smooth = True

def clear_modifiers(self, context):
    for o in bpy.context.selected_objects:
        if o.type != 'MESH': continue
        bpy.context.view_layer.objects.active = o
        o.modifiers.clear()
        o.data.use_auto_smooth = False
        for f in o.data.polygons: f.use_smooth = False
# </functions>

# <classes>
class SRH_panel_automatic(Panel):
    bl_idname = "surf_ramp_helper.panel_automatic"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "Surf Ramp Helper"
    bl_label = "Automatic"

    def draw(self, context):
        foobarbaz = 0

class SRH_panel_manual(Panel):
    bl_idname = "surf_ramp_helper.panel_manual"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "Surf Ramp Helper"
    bl_label = "Manual"

    def draw(self, context):
        self.layout.operator("surf_ramp_helper.ramp_textured", icon = "MESH_CUBE",)
        self.layout.operator("surf_ramp_helper.ramp_cap", icon = "MESH_PLANE")
        self.layout.operator("surf_ramp_helper.ramp_hull", icon = "MESH_ICOSPHERE")
        self.layout.operator("surf_ramp_helper.clear_modifiers", icon = "X")

class SRH_ramp_textured(Operator):
    bl_idname = "surf_ramp_helper.ramp_textured"
    bl_label = "Textured"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifiers_ramp_textured(self, context)
        return {'FINISHED'}

class SRH_ramp_cap(Operator):
    bl_idname = "surf_ramp_helper.ramp_cap"
    bl_label = "Cap"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifiers_ramp_cap(self, context)
        return {'FINISHED'}

class SRH_ramp_hull(Operator):
    bl_idname = "surf_ramp_helper.ramp_hull"
    bl_label = "Hull"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifiers_ramp_hull(self, context)
        return {'FINISHED'}
    
class SRH_clear_modifiers(Operator):
    bl_idname = "surf_ramp_helper.clear_modifiers"
    bl_label = "Clear"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        clear_modifiers(self, context)
        return {'FINISHED'}
# </classes>

# </THE ACTUAL CODE>



# <REGISTRATION>

# <registering>
def register():
    #bpy.utils.register_class(SRH_panel_automatic)
    bpy.utils.register_class(SRH_panel_manual)
    bpy.utils.register_class(SRH_ramp_textured)
    bpy.utils.register_class(SRH_ramp_cap)
    bpy.utils.register_class(SRH_ramp_hull)
    bpy.utils.register_class(SRH_clear_modifiers)
# </registering>

# <unregistering>
def unregister():
    #bpy.utils.unregister_class(SRH_panel_automatic)
    bpy.utils.unregister_class(SRH_panel_manual)
    bpy.utils.unregister_class(SRH_ramp_textured)
    bpy.utils.unregister_class(SRH_ramp_cap)
    bpy.utils.unregister_class(SRH_ramp_hull)
    bpy.utils.unregister_class(SRH_clear_modifiers)
# </unregistering>

# <main>
if __name__ == "__main__":
    register()
# </main>

# </REGISTRATION>