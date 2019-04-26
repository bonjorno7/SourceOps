# <import>
import os, subprocess, math
import bpy, bmesh, mathutils
# </import>

# <functions>
def is_mesh(self, obj):
    """Return whether the object is a mesh"""
    return obj.type == 'MESH'

def is_curve(self, obj):
    """Return whether the object is a curve"""
    return obj.type == 'CURVE'

def add_prop(layout, label, scope, prop):
    """Add a property to a panel with a label before it"""
    row = layout.row().split(factor=0.5)
    row.label(text=label)
    row.split().row().prop(scope, prop, text="")

def add_enum(layout, label, scope, prop):
    """Add an expanded emum property to a panel with a label before it"""
    row = layout.row().split(factor = 0.5)
    row.label(text = label)
    row.split().row().prop(scope, prop, expand=True)

def triangulate(me):
    """Triangulate the mesh"""
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()

def fill_holes(me):
    """Fill boundary edges with faces, copying surrounding customdata"""
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.holes_fill(bm, edges=bm.edges, sides=1000000)
    bm.to_mesh(me)
    bm.free()

def find_collection(context, item):
    """Return the first collection this item is in, if none return the scene collection"""
    collections = item.users_collection
    if len(collections) > 0:
        return collections[0]
    return context.scene.collection
# </functions>