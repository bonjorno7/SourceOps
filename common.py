# <import>
import os, subprocess, math
import bpy, bmesh, mathutils
import unicodedata, string
# </import>

# <variables>
filename_chars_valid = "-_.() %s%s" % (string.ascii_letters, string.digits)
filename_chars_replace = " "
filename_char_limit = 255
# </variables>

# <functions>
def get_globals(context):
    return context.scene.SOURCEOPS

def get_settings(context):
    return get_globals(context).settings

def get_game(context):
    return get_settings(context).game()

def get_scale(context):
    return get_settings(context).scale

def get_model(context):
    return get_globals(context).model()

def remove_if_exists(path):
    if os.path.isfile(path):
        os.remove(path)

def fix_slashes(path):
    return path.replace("\\", "/")

def clean_filename(filename, whitelist=filename_chars_valid, replace=filename_chars_replace, char_limit=filename_char_limit):
    for r in replace:
        filename = filename.replace(r, "_")
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()
    cleaned_filename = "".join(c for c in cleaned_filename if c in whitelist)
    return cleaned_filename[:char_limit]   

def verify_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

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