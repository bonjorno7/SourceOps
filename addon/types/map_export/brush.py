import bpy
import bmesh
import mathutils
import math
import typing
from .. pyvmf import pyvmf


def sort_into_parts(bm: bmesh.types.BMesh):
    parts = []

    bm.select_mode = {'FACE'}

    for face in bm.faces:
        face.hide_set(False)

    while True:
        face = next((f for f in bm.faces if not f.hide), None)

        if not face:
            break

        faces = set([face])

        while True:
            temp_faces = faces.copy()

            for face in temp_faces:
                for edge in face.edges:
                    faces.update(set(edge.link_faces))

            if len(temp_faces) == len(faces):
                break

        for face in faces:
            face.hide_set(True)

        parts.append(faces)

    return parts


def get_texture_size(obj: bpy.types.Object, face: bmesh.types.BMFace):
    texture_side_length = -1

    if face.material_index < len(obj.material_slots):
        face_material = obj.material_slots[face.material_index].material
        if face_material and face_material.use_nodes:
            for mat_node in face_material.node_tree.nodes:
                if mat_node.type == 'TEX_IMAGE':
                    texture_side_length = mat_node.image.size[0]
                    break

    return texture_side_length


def calc_uv_axes(settings: typing.Any, obj: bpy.types.Object, bm: bmesh.types.BMesh, face: bmesh.types.BMFace):
    points = [loop.vert.co.copy() for loop in face.loops[0:3]]

    u_vals = []
    v_vals = []

    if len(bm.loops.layers.uv) > 0:
        uv_layer = bm.loops.layers.uv.verify()

        for loop in face.loops[0:3]:
            uv = loop[uv_layer].uv
            u_vals.append(uv[0])
            v_vals.append(1 - uv[1])

    else:
        u_vals = [0, 0, 1]
        v_vals = [0, 1, 1]

    p1, p2, p3 = points
    u1, u2, u3 = u_vals
    v1, v2, v3 = v_vals

    uv_side_a = mathutils.Vector((u2 - u1, v2 - v1))
    uv_side_b = mathutils.Vector((u3 - u1, v3 - v1))
    tangent = (p2 - p1) * uv_side_b.y - (p3 - p1) * uv_side_a.y
    side_v = (p3 - p1) * uv_side_a.x - (p2 - p1) * uv_side_b.x
    determinant = uv_side_a.x * uv_side_b.y - uv_side_b.x * uv_side_a.y

    epsilon = 0.0001

    if abs(determinant) > epsilon:
        tangent = tangent / determinant
        side_v = side_v / determinant

    if not settings.allow_skewed_textures:
        bitangent = mathutils.Quaternion(face.normal, math.radians(90)) @ tangent
        bitangent.normalize()
        bitangent = bitangent * side_v.dot(bitangent)
    else:
        bitangent = side_v

    # Scale
    texture_side_length = get_texture_size(obj, face)
    if texture_side_length > 0:
        u_scale = tangent.magnitude / texture_side_length
        v_scale = bitangent.magnitude / texture_side_length
    else:
        u_scale = 1
        v_scale = 1

    # Offset
    tangent_space_transform = mathutils.Matrix((
        [tangent.x, bitangent.x, face.normal.x],
        [tangent.y, bitangent.y, face.normal.y],
        [tangent.z, bitangent.z, face.normal.z]
    ))
    if texture_side_length > 0 and abs(tangent_space_transform.determinant()) > epsilon:
        tangent_space_transform.invert()
        t1 = tangent_space_transform @ p1
        u_offset = (1 - (t1.x - u1) * texture_side_length) % texture_side_length
        v_offset = (1 - (t1.y - v1) * texture_side_length) % texture_side_length
    else:
        u_offset = 0
        v_offset = 0

    tangent.normalize()
    bitangent.normalize()

    u_axis = f'[{tangent[0]} {tangent[1]} {tangent[2]} {u_offset}] {u_scale * settings.texture_scale}'
    v_axis = f'[{bitangent[0]} {bitangent[1]} {bitangent[2]} {v_offset}] {v_scale * settings.texture_scale}'

    return u_axis, v_axis


def convert_object(settings: typing.Any, obj: bpy.types.Object):
    solids = []

    if obj.type != 'MESH':
        print(f'Skipping {obj.name} because it is not a mesh')
        return []

    depsgraph = bpy.context.evaluated_depsgraph_get()

    bm = bmesh.new()
    bm.from_object(obj, depsgraph)

    matrix = mathutils.Matrix.Scale(settings.geometry_scale, 4) @ obj.matrix_world
    bmesh.ops.transform(bm, matrix=matrix, space=mathutils.Matrix.Identity(4), verts=bm.verts)

    parts = sort_into_parts(bm)

    for part in parts:
        solid = pyvmf.Solid()

        for face in part:
            side = pyvmf.Side()

            face.normal_flip()

            side.plane.clear()

            for vert in face.verts[0:3]:
                vertex = pyvmf.Vertex(*vert.co)

                if settings.align_to_grid:
                    vertex.align_to_grid()

                side.plane.append(vertex)

            u_axis, v_axis = calc_uv_axes(settings, obj, bm, face)
            side.uaxis = pyvmf.Convert.string_to_uvaxis(u_axis)
            side.vaxis = pyvmf.Convert.string_to_uvaxis(v_axis)

            side.lightmapscale = settings.lightmap_scale

            try:
                side.material = obj.data.materials[face.material_index].name.upper()
            except:
                side.material = 'tools/toolsnodraw'.upper()

            solid.add_sides(side)

        solid.editor = pyvmf.Editor()

        solids.append(solid)

    bm.free()

    return solids


def convert_objects(settings: typing.Any, objects: typing.List[bpy.types.Object]):
    solids = []

    for obj in objects:
        result = convert_object(settings, obj)
        solids.extend(result)

    return solids
