# <libraries>
import bpy
from . import common
# </libraries>

# <classes>
class BSE_RAMP_TOOL_Panel(bpy.types.Panel):
    bl_idname = "bse.ramp_tool_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "Blender Source Extras"
    bl_label = "Ramp Tool"

    def draw(self, context):
        scope = context.scene.BSE_RAMP_TOOL_properties
        common.add_prop(self, "Reference", scope, "reference")
        common.add_prop(self, "Cap Start", scope, "cap_start")
        common.add_prop(self, "Cap End", scope, "cap_end")
        common.add_prop(self, "Collision", scope, "collision")
        common.add_prop(self, "Curve", scope, "curve")
        self.layout.operator("bse.ramp_tool_add_modifiers")
        self.layout.operator("bse.ramp_tool_remove_modifiers")

class BSE_RAMP_TOOL_PropertyGroup(bpy.types.PropertyGroup):
    reference = bpy.props.PointerProperty(
        name = "",
        description = "Select your Ramp Reference object here",
        type = bpy.types.Object,
        poll = common.is_mesh,
    )

    cap_start = bpy.props.PointerProperty(
        name = "",
        description = "Select your Ramp Cap Start object here",
        type = bpy.types.Object,
        poll = common.is_mesh,
    )

    cap_end = bpy.props.PointerProperty(
        name = "",
        description = "Select your Ramp Cap End object here",
        type = bpy.types.Object,
        poll = common.is_mesh,
    )

    collision = bpy.props.PointerProperty(
        name = "",
        description = "Select your Ramp Collision object here",
        type = bpy.types.Object,
        poll = common.is_mesh,
    )

    curve = bpy.props.PointerProperty(
        name = "",
        description = "Select your Ramp Curve object here",
        type = bpy.types.Object,
        poll = common.is_curve,
    )

class BSE_RAMP_TOOL_AddModifiers(bpy.types.Operator):
    """Add the appropriate modifiers and smoothing to the chosen objects"""
    bl_idname = "bse.ramp_tool_add_modifiers"
    bl_label = "Add Modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scope = context.scene.BSE_RAMP_TOOL_properties
        reference = scope.reference
        cap_start = scope.cap_start
        cap_end = scope.cap_end
        collision = scope.collision
        curve = scope.curve

        if reference != None:
            if reference.type == 'MESH':
                reference.data.use_auto_smooth = True
                for f in reference.data.polygons: f.use_smooth = True
                context.view_layer.objects.active = reference
                reference.modifiers.clear()
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
                if cap_start != None:
                    if cap_start.type == 'MESH':
                        context.object.modifiers["Array"].start_cap = cap_start
                if cap_end != None:
                    if cap_end.type == 'MESH':
                        context.object.modifiers["Array"].end_cap = cap_end
                if curve != None:
                    if curve.type == 'CURVE':
                        context.object.modifiers["Array"].curve = curve
                        context.object.modifiers["Curve"].object = curve

        if cap_start != None:
            if cap_start.type == 'MESH':
                cap_start.data.use_auto_smooth = True
                for f in cap_start.data.polygons: f.use_smooth = True
                context.view_layer.objects.active = cap_start
                cap_start.modifiers.clear()
                bpy.ops.object.modifier_add(type='TRIANGULATE')
                context.object.modifiers["Triangulate"].show_in_editmode = False
                context.object.modifiers["Triangulate"].quad_method = 'FIXED'

        if cap_end != None:
            if cap_end.type == 'MESH':
                cap_end.data.use_auto_smooth = True
                for f in cap_end.data.polygons: f.use_smooth = True
                context.view_layer.objects.active = cap_end
                cap_end.modifiers.clear()
                bpy.ops.object.modifier_add(type='TRIANGULATE')
                context.object.modifiers["Triangulate"].show_in_editmode = False
                context.object.modifiers["Triangulate"].quad_method = 'FIXED'

        if collision != None:
            if collision.type == 'MESH':
                collision.data.use_auto_smooth = False
                for f in collision.data.polygons: f.use_smooth = True
                context.view_layer.objects.active = collision
                collision.modifiers.clear()
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
                if curve != None:
                    if curve.type == 'CURVE':
                        context.object.modifiers["Array"].curve = curve
                        context.object.modifiers["Curve"].object = curve

        context.view_layer.objects.active = None
        return {'FINISHED'}

class BSE_RAMP_TOOL_RemoveModifiers(bpy.types.Operator):
    """Remove all modifiers and smoothing for the chosen objects"""
    bl_idname = "bse.ramp_tool_remove_modifiers"
    bl_label = "Remove Modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scope = context.scene.BSE_RAMP_TOOL_properties
        reference = scope.reference
        cap_start = scope.cap_start
        cap_end = scope.cap_end
        collision = scope.collision

        if reference != None:
            if reference.type == 'MESH':
                reference.data.use_auto_smooth = False
                for f in reference.data.polygons: f.use_smooth = False
                context.view_layer.objects.active = reference
                reference.modifiers.clear()

        if cap_start != None:
            if cap_start.type == 'MESH':
                cap_start.data.use_auto_smooth = False
                for f in cap_start.data.polygons: f.use_smooth = False
                context.view_layer.objects.active = cap_start
                cap_start.modifiers.clear()

        if cap_end != None:
            if cap_end.type == 'MESH':
                cap_end.data.use_auto_smooth = False
                for f in cap_end.data.polygons: f.use_smooth = False
                context.view_layer.objects.active = cap_end
                cap_end.modifiers.clear()

        if collision != None:
            if collision.type == 'MESH':
                collision.data.use_auto_smooth = False
                for f in collision.data.polygons: f.use_smooth = False
                context.view_layer.objects.active = collision
                collision.modifiers.clear()

        context.view_layer.objects.active = None
        return {'FINISHED'}
# </classes>

# <registration>
classes = (
    BSE_RAMP_TOOL_Panel,
    BSE_RAMP_TOOL_PropertyGroup,
    BSE_RAMP_TOOL_AddModifiers,
    BSE_RAMP_TOOL_RemoveModifiers,
)

def register():
    for c in classes: bpy.utils.register_class(c)
    bpy.types.Scene.BSE_RAMP_TOOL_properties = bpy.props.PointerProperty(type = BSE_RAMP_TOOL_PropertyGroup)

def unregister():
    for c in classes: bpy.utils.unregister_class(c)
    del bpy.types.Scene.BSE_RAMP_TOOL_properties
# </registration>