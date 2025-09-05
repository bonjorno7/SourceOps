import bpy
import bmesh
import mathutils
import typing
from .. pyvmf import pyvmf
from ... utils import map_export


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

            points = []

            for vert in face.verts[0:3]:
                vertex = pyvmf.Vertex(*vert.co)

                if settings.align_to_grid:
                    vertex.align_to_grid()

                side.plane.append(vertex)
                points.append(mathutils.Vector((vertex.x, vertex.y, vertex.z)))

            uvs = []

            if len(bm.loops.layers.uv) > 0:
                uv_layer = bm.loops.layers.uv.verify()

                for loop in face.loops[0:3]:
                    uvs.append(loop[uv_layer].uv)

            else:
                uvs.append(mathutils.Vector((0, 0)))
                uvs.append(mathutils.Vector((0, 1)))
                uvs.append(mathutils.Vector((1, 1)))

            p1, p2, p3 = points
            uv1, uv2, uv3 = uvs
            texture_size = map_export.get_texture_size(obj, face)
            texture_scale = settings.texture_scale
            allow_skewed_textures = settings.allow_skewed_textures
            u_axis, v_axis = map_export.calc_uv_axes(p1, p2, p3, uv1, uv2, uv3, allow_skewed_textures, texture_size, texture_scale)

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
