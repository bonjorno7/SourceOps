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
from bpy.props import BoolProperty
from bpy.types import Operator, Menu, Panel
# </importing libraries>

# </SETTING UP>



# <THE ACTUAL CODE>

# <functions>
def add_modifiers_ramp_reference(self, context):
    for o in bpy.context.selected_objects:
        if o.type != 'MESH': continue
        bpy.context.view_layer.objects.active = o
        o.modifiers.clear()
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
        if context.scene.srh_change_names: o.name = "Ramp Reference"

def add_modifiers_ramp_cap_start(self, context):
    for o in bpy.context.selected_objects:
        if o.type != 'MESH': continue
        bpy.context.view_layer.objects.active = o
        o.modifiers.clear()
        bpy.ops.object.modifier_add(type='TRIANGULATE')
        bpy.context.object.modifiers["Triangulate"].show_in_editmode = False
        bpy.context.object.modifiers["Triangulate"].quad_method = 'FIXED'
        o.data.use_auto_smooth = True
        for f in o.data.polygons: f.use_smooth = True
        if context.scene.srh_change_names: o.name = "Ramp Cap Start"

def add_modifiers_ramp_cap_end(self, context):
    for o in bpy.context.selected_objects:
        if o.type != 'MESH': continue
        bpy.context.view_layer.objects.active = o
        o.modifiers.clear()
        bpy.ops.object.modifier_add(type='TRIANGULATE')
        bpy.context.object.modifiers["Triangulate"].show_in_editmode = False
        bpy.context.object.modifiers["Triangulate"].quad_method = 'FIXED'
        o.data.use_auto_smooth = True
        for f in o.data.polygons: f.use_smooth = True
        if context.scene.srh_change_names: o.name = "Ramp Cap End"

def add_modifiers_ramp_collision(self, context):
    for o in bpy.context.selected_objects:
        if o.type != 'MESH': continue
        bpy.context.view_layer.objects.active = o
        o.modifiers.clear()
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
        if context.scene.srh_change_names: o.name = "Ramp Collision"

def clear_modifiers(self, context):
    for o in bpy.context.selected_objects:
        if o.type != 'MESH': continue
        bpy.context.view_layer.objects.active = o
        o.modifiers.clear()
        o.data.use_auto_smooth = False
        for f in o.data.polygons: f.use_smooth = False

def apply_source_settings(self, context):
    if context.scene.srh_source_settings == True:
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].overlay.grid_subdivisions = 8
                area.spaces[0].clip_start = 1.0
                area.spaces[0].clip_end = 100000.0
                break
    else:
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].overlay.grid_subdivisions = 10
                area.spaces[0].clip_start = 0.1
                area.spaces[0].clip_end = 1000.0
                break
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
        self.layout.operator("surf_ramp_helper.ramp_reference", icon = "MESH_CUBE",)
        self.layout.operator("surf_ramp_helper.ramp_cap_start", icon = "MESH_PLANE")
        self.layout.operator("surf_ramp_helper.ramp_cap_end", icon = "MESH_PLANE")
        self.layout.operator("surf_ramp_helper.ramp_collision", icon = "MESH_ICOSPHERE")
        self.layout.operator("surf_ramp_helper.clear_modifiers", icon = "X")

class SRH_panel_options(Panel):
    bl_idname = "surf_ramp_helper.panel_options"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "Surf Ramp Helper"
    bl_label = "Options"

    def draw(self, context):
        self.layout.prop(context.scene, "srh_change_names")
        self.layout.prop(context.scene, "srh_source_settings")

class SRH_ramp_reference(Operator):
    bl_idname = "surf_ramp_helper.ramp_reference"
    bl_label = "Reference"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifiers_ramp_reference(self, context)
        return {'FINISHED'}

class SRH_ramp_cap_start(Operator):
    bl_idname = "surf_ramp_helper.ramp_cap_start"
    bl_label = "Cap Start"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifiers_ramp_cap_start(self, context)
        return {'FINISHED'}

class SRH_ramp_cap_end(Operator):
    bl_idname = "surf_ramp_helper.ramp_cap_end"
    bl_label = "Cap End"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifiers_ramp_cap_end(self, context)
        return {'FINISHED'}

class SRH_ramp_collision(Operator):
    bl_idname = "surf_ramp_helper.ramp_collision"
    bl_label = "Collision"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifiers_ramp_collision(self, context)
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
    bpy.utils.register_class(SRH_panel_automatic)
    bpy.utils.register_class(SRH_panel_manual)
    bpy.utils.register_class(SRH_panel_options)
    bpy.utils.register_class(SRH_ramp_reference)
    bpy.utils.register_class(SRH_ramp_cap_start)
    bpy.utils.register_class(SRH_ramp_cap_end)
    bpy.utils.register_class(SRH_ramp_collision)
    bpy.utils.register_class(SRH_clear_modifiers)

    bpy.types.Scene.srh_change_names = BoolProperty(
        name = "Change Names",
        description = "Change names of objects when applying modifiers to them. Clear does not change these names back.",
        default = False,
    )

    bpy.types.Scene.srh_source_settings = BoolProperty(
        name = "Source Settings",
        description = "Change Grid Subdivisions from 10 to 8, Clip Start from 0.1 to 1, and Clip End from 1000 to 100000",
        default = False,
        update = apply_source_settings,
    )
# </registering>

# <unregistering>
def unregister():
    bpy.utils.unregister_class(SRH_panel_automatic)
    bpy.utils.unregister_class(SRH_panel_manual)
    bpy.utils.unregister_class(SRH_panel_options)
    bpy.utils.unregister_class(SRH_ramp_reference)
    bpy.utils.unregister_class(SRH_ramp_cap_start)
    bpy.utils.unregister_class(SRH_ramp_cap_end)
    bpy.utils.unregister_class(SRH_ramp_collision)
    bpy.utils.unregister_class(SRH_clear_modifiers)
    del bpy.types.Scene.srh_change_names
    del bpy.types.Scene.srh_source_settings
# </unregistering>

# <main>
if __name__ == "__main__":
    register()
# </main>

# </REGISTRATION>