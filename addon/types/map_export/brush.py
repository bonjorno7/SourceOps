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


def calc_uv_axes(settings: typing.Any, bm: bmesh.types.BMesh, face: bmesh.types.BMFace):
    points = [loop.vert.co.copy() for loop in face.loops[0:3]]

    u_vals = []
    v_vals = []

    if len(bm.loops.layers.uv) > 0:
        uv_layer = bm.loops.layers.uv.verify()

        for loop in face.loops[0:3]:
            uv = loop[uv_layer].uv
            u_vals.append(uv[0])
            v_vals.append(uv[1])

    else:
        u_vals = [0, 0, 1]
        v_vals = [0, 1, 1]

    p1, p2, p3 = points
    u1, u2, u3 = u_vals
    v1, v2, v3 = v_vals

    tangent = -1 * ((p2 - p1) * (v3 - v1) - (p3 - p1) * (v2 - v1))
    bitangent = mathutils.Quaternion(face.normal, math.radians(90)) @ tangent

    # TODO: Calculate scale and offset

    tangent.normalize()
    bitangent.normalize()

    u_axis = f'[{tangent[0]} {tangent[1]} {tangent[2]} 0] {settings.texture_scale}'
    v_axis = f'[{bitangent[0]} {bitangent[1]} {bitangent[2]} 0] {settings.texture_scale}'

    return u_axis, v_axis


def convert_objects(settings: typing.Any, objects: typing.List[bpy.types.Object]):
    solids = []

    for obj in objects:
        if obj.type != 'MESH':
            print(f'Skipping {obj.name} because it is not a mesh')
            continue

        depsgraph = bpy.context.evaluated_depsgraph_get()

        bm = bmesh.new()
        bm.from_object(obj, depsgraph)

        parts = sort_into_parts(bm)

        for part in parts:
            solid = pyvmf.Solid()

            for face in part:
                side = pyvmf.Side()

                face.normal_flip()

                side.plane.clear()

                for vert in face.verts[0:3]:
                    vertex = pyvmf.Vertex(*vert.co)

                    vertex.multiply(settings.geometry_scale)

                    if settings.align_to_grid:
                        vertex.align_to_grid()

                    side.plane.append(vertex)

                u_axis, v_axis = calc_uv_axes(settings, bm, face)
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
