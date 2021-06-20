import bpy
from bpy.types import Object, TriangulateModifier
from pathlib import Path
from typing import List


MESH_TYPES = {'CURVE', 'FONT', 'MESH', 'SURFACE'}
OBJECT_TYPES = MESH_TYPES | {'ARMATURE'}


def export_fbx(path: Path, objects: List[Object]):
    '''Export objects to FBX with settings for Source.'''
    frame_current = bpy.context.scene.frame_current
    bpy.context.scene.frame_current = bpy.context.scene.frame_start

    collection = bpy.data.collections.new('SourceOps')
    bpy.context.scene.collection.children.link(collection)

    active_layer_collection = bpy.context.view_layer.active_layer_collection
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[-1]

    obj_hide_viewport = {}
    obj_triangulate_mod = {}

    for obj in objects:
        if obj.type in OBJECT_TYPES:
            collection.objects.link(obj)
            obj_hide_viewport[obj] = obj.hide_viewport
            obj.hide_viewport = False

        if obj.type in MESH_TYPES:
            mod: TriangulateModifier = obj.modifiers.new('Triangulate', 'TRIANGULATE')
            obj_triangulate_mod[obj] = mod
            mod.min_vertices = 4
            mod.quad_method = 'FIXED'
            mod.ngon_method = 'CLIP'
            mod.keep_custom_normals = True

    try:
        bpy.ops.export_scene.fbx(filepath=str(path), use_active_collection=True, global_scale=0.01)
    except:
        raise

    finally:
        for obj, triangulate_mod in obj_triangulate_mod.items():
            obj.modifiers.remove(triangulate_mod)

        for obj, hide_viewport in obj_hide_viewport.items():
            obj.hide_viewport = hide_viewport

        bpy.context.view_layer.active_layer_collection = active_layer_collection
        bpy.data.collections.remove(collection)
        bpy.context.scene.frame_current = frame_current
