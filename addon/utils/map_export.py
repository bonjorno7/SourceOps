import bpy
import bmesh
import mathutils
import math


def get_texture_size(obj: bpy.types.Object, face: bmesh.types.BMFace):
    if face.material_index in range(len(obj.material_slots)):
        face_material = obj.material_slots[face.material_index].material

        if face_material and face_material.use_nodes:
            for mat_node in face_material.node_tree.nodes:
                if mat_node.type == 'TEX_IMAGE':
                    return mat_node.image.size[0]

    return -1


def calc_uv_axes(p1: mathutils.Vector, p2: mathutils.Vector, p3: mathutils.Vector, uv1: mathutils.Vector, uv2: mathutils.Vector, uv3: mathutils.Vector, allow_skewed_textures: bool, texture_size: float, texture_scale: float):
    '''Calculate U and V axes for brush plane using provided UV coordinates'''
    
    normal = mathutils.Vector.cross(p2 - p1, p3 - p1).normalized()

    u1, u2, u3 = uv1[0], uv2[0], uv3[0]
    v1, v2, v3 = 1.0 - uv1[1], 1.0 - uv2[1], 1.0 - uv3[1]

    uv_side_a = mathutils.Vector((u2 - u1, v2 - v1))
    uv_side_b = mathutils.Vector((u3 - u1, v3 - v1))
    tangent = (p2 - p1) * uv_side_b.y - (p3 - p1) * uv_side_a.y
    side_v = (p3 - p1) * uv_side_a.x - (p2 - p1) * uv_side_b.x
    determinant = uv_side_a.x * uv_side_b.y - uv_side_b.x * uv_side_a.y

    epsilon = 0.0001

    if abs(determinant) > epsilon:
        tangent = tangent / determinant
        side_v = side_v / determinant

    if not allow_skewed_textures:
        bitangent = mathutils.Quaternion(normal, math.radians(90)) @ tangent
        bitangent.normalize()
        bitangent = bitangent * side_v.dot(bitangent)
    else:
        bitangent = side_v

    # Scale
    if texture_size > 0:
        u_scale = tangent.magnitude / texture_size
        v_scale = bitangent.magnitude / texture_size
    else:
        u_scale = 1
        v_scale = 1

    # Offset
    tangent_space_transform = mathutils.Matrix((
        [tangent.x, bitangent.x, normal.x],
        [tangent.y, bitangent.y, normal.y],
        [tangent.z, bitangent.z, normal.z]
    ))
    if texture_size > 0 and abs(tangent_space_transform.determinant()) > epsilon:
        tangent_space_transform.invert()
        t1 = tangent_space_transform @ p1
        u_offset = (1 - (t1.x - u1) * texture_size) % texture_size
        v_offset = (1 - (t1.y - v1) * texture_size) % texture_size
    else:
        u_offset = 0
        v_offset = 0

    tangent.normalize()
    bitangent.normalize()

    u_axis = f'[{tangent[0]} {tangent[1]} {tangent[2]} {u_offset}] {u_scale * texture_scale}'
    v_axis = f'[{bitangent[0]} {bitangent[1]} {bitangent[2]} {v_offset}] {v_scale * texture_scale}'

    return u_axis, v_axis