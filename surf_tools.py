# <libraries>
import bpy, bmesh, mathutils
from . import common
# </libraries>

# <collision generator>
class BASE_PG_Collision(bpy.types.PropertyGroup):
    """Properties used by the collision generator"""
    target: bpy.props.EnumProperty(
        name = "Target Object",
        description = "The object to put the collision mesh in",
        items = (
            ('NEW', "New", "Create new objects for the collision meshes"),
            ('SELF', "Self", "Overwrite the objects with collision meshes"),
        ),
        default = 'NEW',
    )

    modifiers: bpy.props.EnumProperty(
        name = "Modifiers",
        description = "What to do with the original object's modifiers",
        items = (
            ('APPLY', "Apply", "Apply the object's modifiers before generating the collision mesh"),
            ('IGNORE', "Ignore", "Ignore the object's modifiers, keep them if target is self"),
        ),
        default = 'APPLY',
    )

    thickness: bpy.props.FloatProperty(
        name = "Thickness",
        description = "Thickness of the collision bodies in hammer units",
        default = 16,
    )

class BASE_OT_SurfCollision(bpy.types.Operator):
    """Generate flawless but expensive collision meshes for the selected objects"""
    bl_idname = "base.surf_collision"
    bl_label = "Generate Collision"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def generate_collision(self, bm, matrix, distance):
        """Turn the bmesh into a collision mesh"""
        bmesh.ops.triangulate(bm, faces = bm.faces)
        bmesh.ops.split_edges(bm, edges = bm.edges)

        geom = bmesh.ops.extrude_face_region(bm, geom = bm.faces)
        faces = [item for item in geom['geom'] if isinstance(item, bmesh.types.BMFace)]

        for face in faces:
            vec = face.normal * -distance
            bmesh.ops.translate(bm, vec = vec, space = matrix, verts = face.verts)

            avg = mathutils.Vector()
            for vert in face.verts: avg += vert.co / 3
            bmesh.ops.pointmerge(bm, verts = face.verts, merge_co = avg)

        bmesh.ops.recalc_face_normals(bm, faces = bm.faces)
        for face in bm.faces: face.smooth = True

    def execute(self, context):
        """Iterate through all selected objects and make collision meshes for them"""
        scale = context.scene.BASE.settings.scale
        colset = context.scene.BASE.collision
        apply = colset.modifiers == 'APPLY'

        selected_objects = context.selected_objects
        for obj in selected_objects:
            if obj.type != 'MESH': continue
            bm = bmesh.new()
            bm.from_mesh(obj.to_mesh(context.depsgraph, apply_modifiers = True) if apply else obj.data)
            self.generate_collision(bm, obj.matrix_world, colset.thickness / scale)

            if colset.target == 'NEW':
                mesh = bpy.data.meshes.new(name = obj.data.name + ".col")
                bm.to_mesh(mesh)

                new_object = bpy.data.objects.new(obj.name + ".col", mesh)
                collection = common.find_collection(context, obj)
                collection.objects.link(new_object)
                new_object.matrix_local = obj.matrix_local

                obj.select_set(False)
                new_object.select_set(True)

            elif colset.target == 'SELF':
                bm.to_mesh(obj.data)
                obj.data.use_auto_smooth = False
                if apply: obj.modifiers.clear()

        return {'FINISHED'}
# </collision generator>

# <surf ramp tool>
class BASE_PG_SurfRamp(bpy.types.PropertyGroup):
    """Properties for the Surf Ramp Tool"""
    curve: bpy.props.PointerProperty(
        name = "Curve",
        description = "Select your Ramp Curve object here",
        type = bpy.types.Object,
        poll = common.is_curve,
    )

    segment: bpy.props.PointerProperty(
        name = "Segment",
        description = "Select your Ramp Reference mesh here",
        type = bpy.types.Object,
        poll = common.is_mesh,
    )

    start_cap: bpy.props.PointerProperty(
        name = "Start Cap",
        description = "Select your Reference Start Cap here",
        type = bpy.types.Object,
        poll = common.is_mesh,
    )

    end_cap: bpy.props.PointerProperty(
        name = "End Cap",
        description = "Select your Reference End Cap here",
        type = bpy.types.Object,
        poll = common.is_mesh,
    )

class BASE_OT_SurfRampify(bpy.types.Operator):
    """Add the appropriate modifiers to the chosen objects"""
    bl_idname = "base.surf_rampify"
    bl_label = "Add Modifiers"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        sr = context.scene.BASE.surf_ramp
        return sr.curve and sr.segment

    def execute(self, context):
        sr = context.scene.BASE.surf_ramp
        sr.segment.modifiers.clear()

        array = sr.segment.modifiers.new("Array", 'ARRAY')
        array.show_expanded = True
        array.show_in_editmode = False
        array.fit_type = 'FIT_CURVE'
        array.relative_offset_displace = (0, 0, 1)
        array.use_merge_vertices = True
        array.use_merge_vertices_cap = True
        if sr.start_cap: array.start_cap = sr.start_cap
        if sr.end_cap: array.end_cap = sr.end_cap

        curve = sr.segment.modifiers.new("Curve", 'CURVE')
        curve.show_expanded = True
        curve.show_in_editmode = False
        curve.deform_axis = 'POS_Z'
        array.curve = sr.curve
        curve.object = sr.curve

        return {"FINISHED"}
# </surf ramp tool>

# <panels>
class BASE_PT_SurfTools(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Surf Tools"

    def draw_header(self, context):
        self.layout.label(icon = 'MARKER')

    def draw(self, context):
        pass

class BASE_PT_Collision(bpy.types.Panel):
    bl_parent_id = "BASE_PT_SurfTools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Collision Generator"

    def draw_header(self, context):
        self.layout.label(icon = 'MESH_ICOSPHERE')

    def draw(self, context):
        collision = context.scene.BASE.collision
        common.add_enum(self.layout, "Target", collision, "target")
        common.add_enum(self.layout, "Modifiers", collision, "modifiers")
        common.add_prop(self.layout, "Thickness", collision, "thickness")
        self.layout.operator("base.surf_collision")

class BASE_PT_CurvedRamp(bpy.types.Panel):
    bl_parent_id = "BASE_PT_SurfTools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Curved Ramp Tool"

    def draw_header(self, context):
        self.layout.label(icon = 'CURVE_DATA')

    def draw(self, context):
        surf_ramp = context.scene.BASE.surf_ramp
        common.add_prop(self.layout, "Curve", surf_ramp, "curve")
        common.add_prop(self.layout, "Segment", surf_ramp, "segment")
        if surf_ramp.segment:
            common.add_prop(self.layout, "Start Cap", surf_ramp, "start_cap")
            common.add_prop(self.layout, "End Cap", surf_ramp, "end_cap")
        self.layout.operator("base.surf_rampify")
# </panels>