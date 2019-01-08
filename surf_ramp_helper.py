# <SETTING UP>

# <add-on definitions>
bl_info = {
    "name": "Surf Ramp Helper",
    "author": "bonjorno7",
    "version": (0, 5),
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
from bpy.props import BoolProperty, EnumProperty
from bpy.types import Operator, Menu, Panel
# </importing libraries>

# </SETTING UP>



# <THE ACTUAL CODE>

# <functions>
def add_modifiers_ramp_reference(context, object):
    context.view_layer.objects.active = object
    object.modifiers.clear()
    bpy.ops.object.modifier_add(type='TRIANGULATE')
    context.object.modifiers["Triangulate"].show_in_editmode = False
    context.object.modifiers["Triangulate"].quad_method = 'FIXED'
    bpy.ops.object.modifier_add(type='ARRAY')
    context.object.modifiers["Array"].show_in_editmode = False
    context.object.modifiers["Array"].fit_type = 'FIT_CURVE'
    context.object.modifiers["Array"].relative_offset_displace[0] = 0.0
    context.object.modifiers["Array"].relative_offset_displace[1] = 0.0
    context.object.modifiers["Array"].relative_offset_displace[2] = 1.0
    context.object.modifiers["Array"].use_merge_vertices = True
    context.object.modifiers["Array"].use_merge_vertices_cap = True
    bpy.ops.object.modifier_add(type='CURVE')
    context.object.modifiers["Curve"].deform_axis = 'POS_Z'
    object.data.use_auto_smooth = True
    for f in object.data.polygons: f.use_smooth = True
    if context.scene.srh_change_names: object.name = "Ramp Reference"

def add_modifiers_ramp_cap_start(context, object):
    context.view_layer.objects.active = object
    object.modifiers.clear()
    bpy.ops.object.modifier_add(type='TRIANGULATE')
    context.object.modifiers["Triangulate"].show_in_editmode = False
    context.object.modifiers["Triangulate"].quad_method = 'FIXED'
    object.data.use_auto_smooth = True
    for f in object.data.polygons: f.use_smooth = True
    if context.scene.srh_change_names: object.name = "Ramp Cap Start"

def add_modifiers_ramp_cap_end(context, object):
    context.view_layer.objects.active = object
    object.modifiers.clear()
    bpy.ops.object.modifier_add(type='TRIANGULATE')
    context.object.modifiers["Triangulate"].show_in_editmode = False
    context.object.modifiers["Triangulate"].quad_method = 'FIXED'
    object.data.use_auto_smooth = True
    for f in object.data.polygons: f.use_smooth = True
    if context.scene.srh_change_names: object.name = "Ramp Cap End"

def add_modifiers_ramp_collision(context, object):
    context.view_layer.objects.active = object
    object.modifiers.clear()
    bpy.ops.object.modifier_add(type='TRIANGULATE')
    context.object.modifiers["Triangulate"].show_in_editmode = False
    context.object.modifiers["Triangulate"].quad_method = 'FIXED'
    bpy.ops.object.modifier_add(type='ARRAY')
    context.object.modifiers["Array"].show_in_editmode = False
    context.object.modifiers["Array"].fit_type = 'FIT_CURVE'
    context.object.modifiers["Array"].relative_offset_displace[0] = 0.0
    context.object.modifiers["Array"].relative_offset_displace[1] = 0.0
    context.object.modifiers["Array"].relative_offset_displace[2] = 1.0
    context.object.modifiers["Array"].use_merge_vertices = False
    context.object.modifiers["Array"].use_merge_vertices_cap = False
    bpy.ops.object.modifier_add(type='CURVE')
    context.object.modifiers["Curve"].deform_axis = 'POS_Z'
    object.data.use_auto_smooth = False
    for f in object.data.polygons: f.use_smooth = True
    if context.scene.srh_change_names: object.name = "Ramp Collision"

def clear_modifiers(context, object):
    context.view_layer.objects.active = object
    object.modifiers.clear()
    object.data.use_auto_smooth = False
    for f in object.data.polygons: f.use_smooth = False

def apply_source_settings(self, context):
    if context.scene.srh_source_settings:
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

def all_mesh_objects(self, context):
    l = []
    l.append(("_NO_OBJECT_", "", ""))
    for o in bpy.data.objects:
        if o.type == 'MESH':
            l.append((o.name, o.name, ""))
    return l

def all_curve_objects(self, context):
    l = []
    l.append(("_NO_OBJECT_", "", ""))
    for o in bpy.data.objects:
        if o.type == 'CURVE':
            l.append((o.name, o.name, ""))
    return l
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
        r = self.layout.row()
        s = r.split()
        c = s.column()
        c.label(text = "Reference")
        s = s.split()
        c = s.column()
        c.prop(context.scene, "srh_choose_ramp_reference")

        r = self.layout.row()
        s = r.split()
        c = s.column()
        c.label(text = "Cap Start")
        s = s.split()
        c = s.column()
        c.prop(context.scene, "srh_choose_ramp_cap_start")

        r = self.layout.row()
        s = r.split()
        c = s.column()
        c.label(text = "Cap End")
        s = s.split()
        c = s.column()
        c.prop(context.scene, "srh_choose_ramp_cap_end")

        r = self.layout.row()
        s = r.split()
        c = s.column()
        c.label(text = "Collision")
        s = s.split()
        c = s.column()
        c.prop(context.scene, "srh_choose_ramp_collision")

        r = self.layout.row()
        s = r.split()
        c = s.column()
        c.label(text = "Curve")
        s = s.split()
        c = s.column()
        c.prop(context.scene, "srh_choose_ramp_curve")

        self.layout.operator("surf_ramp_helper.auto_add_modifiers", icon = "AUTO")
        self.layout.operator("surf_ramp_helper.auto_remove_modifiers", icon = "X")

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
    """Add the appropriate modifiers and smoothing to the selected ramp reference segment"""
    bl_idname = "surf_ramp_helper.ramp_reference"
    bl_label = "Reference"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for o in bpy.context.selected_objects:
            if o.type == 'MESH':
                add_modifiers_ramp_reference(context, o)
        return {'FINISHED'}

class SRH_ramp_cap_start(Operator):
    """Add the appropriate modifiers and smoothing to the selected ramp cap start segment"""
    bl_idname = "surf_ramp_helper.ramp_cap_start"
    bl_label = "Cap Start"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for o in bpy.context.selected_objects:
            if o.type == 'MESH':
                add_modifiers_ramp_cap_start(context, o)
        return {'FINISHED'}

class SRH_ramp_cap_end(Operator):
    """Add the appropriate modifiers and smoothing to the selected ramp cap end segment"""
    bl_idname = "surf_ramp_helper.ramp_cap_end"
    bl_label = "Cap End"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for o in bpy.context.selected_objects:
            if o.type == 'MESH':
                add_modifiers_ramp_cap_end(context, o)
        return {'FINISHED'}

class SRH_ramp_collision(Operator):
    """Add the appropriate modifiers and smoothing to the selected ramp collision segment"""
    bl_idname = "surf_ramp_helper.ramp_collision"
    bl_label = "Collision"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for o in bpy.context.selected_objects:
            if o.type == 'MESH':
                add_modifiers_ramp_collision(context, o)
        return {'FINISHED'}

class SRH_clear_modifiers(Operator):
    """Remove all modifiers and smoothing for the selected mesh objects"""
    bl_idname = "surf_ramp_helper.clear_modifiers"
    bl_label = "Clear"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for o in bpy.context.selected_objects:
            if o.type == 'MESH':
                clear_modifiers(context, o)
        return {'FINISHED'}

class SRH_auto_add_modifiers(Operator):
    """Add the appropriate modifiers and smoothing to the chosen objects"""
    bl_idname = "surf_ramp_helper.auto_add_modifiers"
    bl_label = "Add Modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ramp_reference = bpy.data.objects.get(context.scene.srh_choose_ramp_reference)
        ramp_cap_start = bpy.data.objects.get(context.scene.srh_choose_ramp_cap_start)
        ramp_cap_end = bpy.data.objects.get(context.scene.srh_choose_ramp_cap_end)
        ramp_collision = bpy.data.objects.get(context.scene.srh_choose_ramp_collision)
        ramp_curve = bpy.data.objects.get(context.scene.srh_choose_ramp_curve)

        if ramp_reference != None:
            if ramp_reference.type == 'MESH':
                add_modifiers_ramp_reference(context, ramp_reference)
                if ramp_cap_start != None:
                    if ramp_cap_start.type == 'MESH':
                        context.object.modifiers["Array"].start_cap = ramp_cap_start
                if ramp_cap_end != None:
                    if ramp_cap_end.type == 'MESH':
                        context.object.modifiers["Array"].end_cap = ramp_cap_end
                if ramp_curve != None:
                    if ramp_curve.type == 'CURVE':
                        context.object.modifiers["Array"].curve = ramp_curve
                        context.object.modifiers["Curve"].object = ramp_curve

        if ramp_cap_start != None:
            if ramp_cap_start.type == 'MESH':
                add_modifiers_ramp_cap_start(context, ramp_cap_start)

        if ramp_cap_end != None:
            if ramp_cap_end.type == 'MESH':
                add_modifiers_ramp_cap_end(context, ramp_cap_end)

        if ramp_collision != None:
            if ramp_collision.type == 'MESH':
                add_modifiers_ramp_collision(context, ramp_collision)
                if ramp_curve != None:
                    if ramp_curve.type == 'CURVE':
                        context.object.modifiers["Array"].curve = ramp_curve
                        context.object.modifiers["Curve"].object = ramp_curve

        return {'FINISHED'}

class SRH_auto_remove_modifiers(Operator):
    """Remove all modifiers and smoothing for the chosen objects"""
    bl_idname = "surf_ramp_helper.auto_remove_modifiers"
    bl_label = "Remove Modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ramp_reference = bpy.data.objects.get(context.scene.srh_choose_ramp_reference)
        ramp_cap_start = bpy.data.objects.get(context.scene.srh_choose_ramp_cap_start)
        ramp_cap_end = bpy.data.objects.get(context.scene.srh_choose_ramp_cap_end)
        ramp_collision = bpy.data.objects.get(context.scene.srh_choose_ramp_collision)

        if ramp_reference != None:
            if ramp_reference.type == 'MESH':
                clear_modifiers(context, ramp_reference)

        if ramp_cap_start != None:
            if ramp_cap_start.type == 'MESH':
                clear_modifiers(context, ramp_cap_start)

        if ramp_cap_end != None:
            if ramp_cap_end.type == 'MESH':
                clear_modifiers(context, ramp_cap_end)

        if ramp_collision != None:
            if ramp_collision.type == 'MESH':
                clear_modifiers(context, ramp_collision)

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
    bpy.utils.register_class(SRH_auto_add_modifiers)
    bpy.utils.register_class(SRH_auto_remove_modifiers)

    bpy.types.Scene.srh_change_names = BoolProperty(
        name = "Change Names",
        description = "Change names of objects when applying modifiers to them. Clear does not change these names back.",
        default = False,
    )

    bpy.types.Scene.srh_source_settings = BoolProperty(
        name = "Source Settings",
        description = "Change Grid Subdivisions from 10 to 8, Clip Start from 0.1 to 1, and Clip End from 1000 to 100000",
        update = apply_source_settings,
        default = False,
    )

    bpy.types.Scene.srh_choose_ramp_reference = EnumProperty(
        name = "",
        description = "Select your Ramp Reference object here.",
        items = all_mesh_objects,
        default = None,
    )

    bpy.types.Scene.srh_choose_ramp_cap_start = EnumProperty(
        name = "",
        description = "Select your Ramp Cap Start object here.",
        items = all_mesh_objects,
        default = None,
    )

    bpy.types.Scene.srh_choose_ramp_cap_end = EnumProperty(
        name = "",
        description = "Select your Ramp Cap End object here.",
        items = all_mesh_objects,
        default = None,
    )

    bpy.types.Scene.srh_choose_ramp_collision = EnumProperty(
        name = "",
        description = "Select your Ramp Collision object here.",
        items = all_mesh_objects,
        default = None,
    )

    bpy.types.Scene.srh_choose_ramp_curve = EnumProperty(
        name = "",
        description = "Select your Ramp Curve object here.",
        items = all_curve_objects,
        default = None,
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
    bpy.utils.unregister_class(SRH_auto_apply_modifiers)
    bpy.utils.unregister_class(SRH_auto_remove_modifiers)
    del bpy.types.Scene.srh_change_names
    del bpy.types.Scene.srh_source_settings
    del bpy.types.Scene.srh_choose_ramp_reference
    del bpy.types.Scene.srh_choose_ramp_cap_start
    del bpy.types.Scene.srh_choose_ramp_cap_end
    del bpy.types.Scene.srh_choose_ramp_collision
    del bpy.types.Scene.srh_choose_ramp_curve
# </unregistering>

# <main>
if __name__ == "__main__":
    register()
# </main>

# </REGISTRATION>