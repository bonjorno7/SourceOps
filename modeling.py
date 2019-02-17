# <libraries>
import bpy, bmesh, mathutils
from . import common
# </libraries>

# <collision generator>
class GenerateCollision(bpy.types.Operator):
    """Generate flawless but expensive collision meshes for the selected objects"""
    bl_idname = "base.surf_ramp_generate_collision"
    bl_label = "Generate Collision"
    bl_options = {"REGISTER", "UNDO"}

    def generate_collision(self, bm, matrix, scale):
        """Turn the bmesh into a collision mesh"""
        bmesh.ops.triangulate(bm, faces = bm.faces)
        bmesh.ops.split_edges(bm, edges = bm.edges)

        geom = bmesh.ops.extrude_face_region(bm, geom = bm.faces)
        faces = [item for item in geom['geom'] if isinstance(item, bmesh.types.BMFace)]

        for face in faces:
            vec = face.normal * -8 / scale
            bmesh.ops.translate(bm, vec = vec, space = matrix, verts = face.verts)

            avg = mathutils.Vector()
            for vert in face.verts: avg += vert.co / 3
            bmesh.ops.pointmerge(bm, verts = face.verts, merge_co = avg)

        bmesh.ops.recalc_face_normals(bm, faces = bm.faces)
        for face in bm.faces: face.smooth = True

    def execute(self, context):
        """Iterate through all selected objects and make collision meshes for them"""
        scale = context.scene.BASE.settings.scale

        for obj in context.selected_objects:
            if obj.type != 'MESH': continue
            bm = bmesh.new()
            bm.from_mesh(obj.to_mesh(context.depsgraph, apply_modifiers = True))

            mesh = bpy.data.meshes.new(name = obj.data.name + ".col")
            self.generate_collision(bm, obj.matrix_world, scale)
            bm.to_mesh(mesh)

            collision = bpy.data.objects.new(obj.name + ".col", mesh)
            collection = common.find_collection(context, obj)
            collection.objects.link(collision)

        return {'FINISHED'}
# </collision generator>

# <surf ramp tool>
class SurfRamp(bpy.types.PropertyGroup):
    """Properties for the Surf Ramp Tool"""
    curve: bpy.props.PointerProperty(
        name = "",
        description = "Select your Ramp Curve object here",
        type = bpy.types.Object,
        poll = common.is_curve,
    )

    segment: bpy.props.PointerProperty(
        name = "",
        description = "Select your Ramp Reference mesh here",
        type = bpy.types.Object,
        poll = common.is_mesh,
    )

    start_cap: bpy.props.PointerProperty(
        name = "",
        description = "Select your Reference Start Cap here",
        type = bpy.types.Object,
        poll = common.is_mesh,
    )

    end_cap: bpy.props.PointerProperty(
        name = "",
        description = "Select your Reference End Cap here",
        type = bpy.types.Object,
        poll = common.is_mesh,
    )

class SurfRampModify(bpy.types.Operator):
    """Add the appropriate modifiers to the chosen objects"""
    bl_idname = "base.surf_ramp_modify"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    kind: bpy.props.EnumProperty(items = (
        ('REFERENCE', "Reference", "Visible in game but not tangible"),
        ('COLLISION', "Collision", "Tangible in game but not visible"),
        ('CLEAR', "Clear", "Remove modifiers"),
    ))

    def execute(self, context):
        sr = context.scene.BASE.surf_ramp
        if not sr.segment: return {"FINISHED"}
        sr.segment.modifiers.clear()
        if self.kind == 'CLEAR': return {"FINISHED"}

        array = sr.segment.modifiers.new("Array", 'ARRAY')
        array.show_expanded = False
        array.show_in_editmode = False
        array.fit_type = 'FIT_CURVE'
        array.relative_offset_displace = (0, 0, 1)
        array.use_merge_vertices = True if self.kind == 'REFERENCE' else False
        array.use_merge_vertices_cap = True if self.kind == 'REFERENCE' else False
        if sr.start_cap:
            array.start_cap = sr.start_cap
        if sr.end_cap:
            array.end_cap = sr.end_cap

        curve = sr.segment.modifiers.new("Curve", 'CURVE')
        curve.show_expanded = False
        curve.show_in_editmode = False
        curve.deform_axis = 'POS_Z'
        if sr.curve:
            array.curve = sr.curve
            curve.object = sr.curve

        return {"FINISHED"}
# </surf ramp tool>

# <panel>
class ModelingPanel(bpy.types.Panel):
    bl_idname = "base.modeling_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Modeling"

    def draw(self, context):
        box = self.layout.box()
        box.label(text = "Collision", icon = 'MESH_ICOSPHERE')
        box.operator("base.surf_ramp_generate_collision")

        box = self.layout.box()
        box.label(text = "Surf Ramp Tool", icon = 'MARKER')

        surf_ramp = context.scene.BASE.surf_ramp
        common.add_prop(box, "Curve", surf_ramp, "curve")
        common.add_prop(box, "Segment", surf_ramp, "segment")
        common.add_prop(box, "Start Cap", surf_ramp, "start_cap")
        common.add_prop(box, "End Cap", surf_ramp, "end_cap")

        row = box.row()
        row.operator("base.surf_ramp_modify", text = "Reference").kind = 'REFERENCE'
        row.operator("base.surf_ramp_modify", text = "Collision").kind = 'COLLISION'
# </panel>