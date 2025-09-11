import bpy
import string
import unicodedata
import platform
import pathlib
import traceback
import shutil
import bmesh

from mathutils import Vector

def get_version():
    from ... import bl_info
    return '.'.join(str(n) for n in bl_info['version'])


def get_prefs(context):
    addons = context.preferences.addons
    module = __name__.partition('.')[0]
    return addons[module].preferences


def get_game(prefs):
    try:
        return prefs.game_items[prefs.game_index]
    except:
        return None


def get_globals(context):
    try:
        return context.scene.sourceops
    except:
        return None


def get_model(sourceops):
    try:
        return sourceops.model_items[sourceops.model_index]
    except:
        return None


def get_material_folder(model):
    try:
        return model.material_folder_items[model.material_folder_index]
    except:
        return None


def get_skin(model):
    try:
        return model.skin_items[model.skin_index]
    except:
        return None


def get_sequence(model):
    try:
        return model.sequence_items[model.sequence_index]
    except:
        return None


def get_event(sequence):
    try:
        return sequence.event_items[sequence.event_index]
    except:
        return None


def get_attachment(model):
    try:
        return model.attachment_items[model.attachment_index]
    except:
        return None

def get_particle(model):
    try:
        return model.particle_items[model.particle_index]
    except:
        return None

def get_map(sourceops):
    try:
        return sourceops.map_items[sourceops.map_index]
    except:
        return None


def split_column(layout):
    col = layout.column()
    col.use_property_split = True
    col.use_property_decorate = False
    return col

def align_column(layout):
    col = layout.column(align=True)
    col.use_property_split = True
    col.use_property_decorate = False
    return col

filename_chars_valid = '-_.() %s%s' % (string.ascii_letters, string.digits)
filename_chars_replace = ' '
filename_char_limit = 255


def clean_filename(filename, whitelist=filename_chars_valid, replace=filename_chars_replace, char_limit=filename_char_limit):
    for r in replace:
        filename = filename.replace(r, '_')
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()
    cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
    return cleaned_filename[:char_limit]   


def verify_folder(path):
    if not path.is_dir():
        try:
            path.mkdir(parents=True, exist_ok=True)
        except:
            print(f'Failed to create directory: {path}')
            traceback.print_exc()
    return path


def remove_duplicates(list_with_duplicates):
    return list(dict.fromkeys(list(list_with_duplicates)))


def documents():
    if platform.system() == 'Windows':
        import ctypes.wintypes
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)

        ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 1, buf)
        return pathlib.Path(buf.value)

    else:
        return pathlib.Path.home()


def appdata():
    user = bpy.utils.resource_path('USER')
    return pathlib.Path(user).resolve()


def resolve(path):
    if path:
        return str(pathlib.Path(bpy.path.abspath(path)).resolve())
    else:
        return ''


def get_illumposition(model):

    def illumpos_from_obj(obj):
        if obj.type != 'MESH':
            return None
    
        scene = bpy.context.scene
        depsgraph = bpy.context.evaluated_depsgraph_get()
        current_frame = scene.frame_current
        scene.frame_set(0)
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(mesh)
    
        illum_center = None
        if bm.verts:
            local_center = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
            illum_center = eval_obj.matrix_world @ local_center
    
        bm.free()
        eval_obj.to_mesh_clear()
        scene.frame_set(current_frame)
    
        return illum_center
    
    def get_collection_illumpos(collection):
        centers = []
    
        for obj in collection.all_objects:
            illum = illumpos_from_obj(obj)
            if illum is not None:
                centers.append(illum)
    
        if centers:
            return sum(centers, Vector()) / len(centers)
        return None


    if model.illumposition_source == 'MANUAL':
        return Vector(model.illumposition_vector)
    elif model.illumposition_source == 'REFERENCE':
        return Vector(get_collection_illumpos(model.reference)) if model.reference else None
    elif model.illumposition_source == 'COLLISION':
        return Vector(get_collection_illumpos(model.collision)) if model.collision else None
    else:
        return None


def update_wine(self, context):
    self['wine'] = resolve(self.wine)

def get_wine(self):
    wine = pathlib.Path(self.wine)
    which_path = shutil.which('wine')
    which = pathlib.Path(which_path) if which_path is not None else None

    if wine.is_file():
        return wine
    elif which is not None and which.is_file():
        return which
    else:
        raise Exception('Wine executable not found. make sure Wine is installed and accessible by Blender')
    