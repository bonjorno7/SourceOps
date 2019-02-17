# <import>
import os, math, bpy, bmesh
from . import common
# </import>

# <classes>
class AutoHull(bpy.types.Operator):
    """Generate collision meshes for the selected objects"""
    bl_idname = "base.auto_hull"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == 'MESH' or obj.type == 'FONT':
                bm = bmesh.new()
                bm.from_mesh(obj.data)

                concave_edges = []
                for edge in bm.edges:
                    if angle between the faces == concave: # how do I do this
                        concave_edges += edge

                for edge in concave_edges:
                    select the whole edgeloop # how do I do this
                    bpy.ops.mesh.rip('INVOKE_DEFAULT')

                checked_faces = []
                for face in bm.faces:
                    unselect everything # how do I do this
                    select the face # how do I do this
                    if face in checked_faces: continue
                    bpy.ops.mesh.select_linked(limit=False)
                    checked_faces += currently selected face # how do I do this
                    bpy.ops.mesh.convex_hull()

                smooth everything
                add triangulate modifier

                bm.to_mesh(some new mesh)
                bm.free()

        return {'FINISHED'}
# </classes>