import bpy
from bpy.types import Bone, Object, PoseBone, TriangulateModifier
from mathutils import Matrix
from pathlib import Path
from typing import List


MESH_TYPES = {'CURVE', 'FONT', 'MESH', 'SURFACE'}
OBJECT_TYPES = MESH_TYPES | {'ARMATURE'}


def export_fbx(path: Path, armature: Object, objects: List[Object], prepend_armature: bool, ignore_transforms: bool):
    '''Export objects to FBX with settings for Source.'''
    frame_current = bpy.context.scene.frame_current
    bpy.context.scene.frame_current = bpy.context.scene.frame_start

    collection = bpy.data.collections.new('SourceOps')
    bpy.context.scene.collection.children.link(collection)

    active_layer_collection = bpy.context.view_layer.active_layer_collection
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[-1]

    if armature and armature.animation_data and armature.animation_data.action:
        action = armature.animation_data.action
        armature.animation_data_clear()

        for pose_bone in armature.pose.bones:
            pose_bone: PoseBone
            bone: Bone = pose_bone.bone
            pose_bone.matrix = bone.matrix_local
    else:
        action = None

    obj_hide_viewport = {}
    obj_matrix_local = {}
    obj_matrix_parent_inverse = {}
    bone_name = {}
    obj_triangulate_mod = {}

    if armature:
        objects.append(armature)

    for obj in set(objects):
        if obj.type in OBJECT_TYPES:
            collection.objects.link(obj)
            obj_hide_viewport[obj] = obj.hide_viewport
            obj.hide_viewport = False

            if ignore_transforms:
                obj_matrix_local[obj] = obj.matrix_local.copy()
                obj.matrix_local = Matrix.Identity(4)
                obj_matrix_parent_inverse[obj] = obj.matrix_parent_inverse.copy()
                obj.matrix_parent_inverse = Matrix.Identity(4)

        if obj.type == 'ARMATURE':
            if prepend_armature:
                for bone in obj.data.bones:
                    bone_name[bone] = bone.name
                    bone.name = f'{obj.name}.{bone.name}'

        if obj.type in MESH_TYPES:
            mod: TriangulateModifier = obj.modifiers.new('Triangulate', 'TRIANGULATE')
            obj_triangulate_mod[obj] = mod
            mod.min_vertices = 4
            mod.quad_method = 'FIXED'
            mod.ngon_method = 'CLIP'
            mod.keep_custom_normals = True

    try:
        bpy.ops.export_scene.fbx(
            filepath=str(path),
            use_active_collection=True,
            global_scale=0.01,
            add_leaf_bones=False,
            bake_anim=False,
        )

    except:
        raise

    finally:
        for obj, triangulate_mod in obj_triangulate_mod.items():
            obj.modifiers.remove(triangulate_mod)

        if prepend_armature:
            for bone, name in bone_name.items():
                bone.name = name

        if ignore_transforms:
            for obj, matrix_parent_inverse in obj_matrix_parent_inverse.items():
                obj.matrix_parent_inverse = matrix_parent_inverse

            for obj, matrix_local in obj_matrix_local.items():
                obj.matrix_local = matrix_local

        for obj, hide_viewport in obj_hide_viewport.items():
            obj.hide_viewport = hide_viewport

        if action:
            armature.animation_data_create()
            armature.animation_data.action = action

        bpy.context.view_layer.active_layer_collection = active_layer_collection
        bpy.data.collections.remove(collection)
        bpy.context.scene.frame_current = frame_current
