import os
import subprocess
import math
import bpy
import bmesh
import mathutils
from .. import common


class CollisionProps(bpy.types.PropertyGroup):
    """Properties used by the collision generator"""
    bl_idname = "BASE_PG_CollisionProps"

    target: bpy.props.EnumProperty(
        name="Target Object",
        description="The object to put the collision mesh in",
        items=(
            ('NEW', "New", "Create new objects for the collision meshes"),
            ('SELF', "Self", "Overwrite the objects with collision meshes"),
        ),
        default='NEW',
    )

    modifiers: bpy.props.EnumProperty(
        name="Modifiers",
        description="What to do with the original object's modifiers",
        items=(
            ('APPLY', "Apply",
             "Apply the object's modifiers before generating the collision mesh"),
            ('IGNORE', "Ignore",
             "Ignore the object's modifiers, keep them if target is self"),
        ),
        default='APPLY',
    )

    thickness: bpy.props.FloatProperty(
        name="Thickness",
        description="Thickness of the collision bodies in hammer units",
        default=16,
    )


class SurfCollision(bpy.types.Operator):
    """Generate flawless but expensive collision meshes for the selected objects"""
    bl_idname = "base.surf_collision"
    bl_label = "Generate Collision"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def generate_collision(self, bm, matrix, distance):
        """Turn the bmesh into a collision mesh"""
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bmesh.ops.split_edges(bm, edges=bm.edges)

        geom = bmesh.ops.extrude_face_region(bm, geom=bm.faces)
        faces = [item for item in geom['geom']
                 if isinstance(item, bmesh.types.BMFace)]

        for face in faces:
            vec = face.normal * -distance
            bmesh.ops.translate(bm, vec=vec, space=matrix, verts=face.verts)

            avg = mathutils.Vector()
            for vert in face.verts:
                avg += vert.co / 3
            bmesh.ops.pointmerge(bm, verts=face.verts, merge_co=avg)

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        for face in bm.faces:
            face.smooth = True

    def execute(self, context):
        """Iterate through all selected objects and make collision meshes for them"""
        scale = context.scene.BASE.settings.scale
        colset = context.scene.BASE.collision
        apply = colset.modifiers == 'APPLY'

        selected_objects = context.selected_objects
        for obj in selected_objects:
            if obj.type != 'MESH':
                continue
            bm = bmesh.new()
            bm.from_mesh(obj.to_mesh(context.depsgraph,
                                     apply_modifiers=True) if apply else obj.data)
            self.generate_collision(
                bm, obj.matrix_world, colset.thickness / scale)

            if colset.target == 'NEW':
                mesh = bpy.data.meshes.new(name=obj.data.name + ".col")
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
                if apply:
                    obj.modifiers.clear()

        return {'FINISHED'}
