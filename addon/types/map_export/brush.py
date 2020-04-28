import bpy
import bmesh
import mathutils
import math
from .. pyvmf import pyvmf


class Converter:
    def __init__(self, settings, meshes: list):
        self.solids = []

        for mesh in meshes:
            parts = self.sort_into_parts(mesh)

            for part in parts:
                solid = pyvmf.Solid()

                for polygon in part:
                    side = pyvmf.Side()

                    polygon.flip()

                    side.plane.clear()

                    for vertex_index in polygon.vertices[0:3]:
                        vertex = mesh.vertices[vertex_index]
                        vertex = pyvmf.Vertex(*vertex.co)

                        vertex.multiply(settings.geometry_scale)

                        if settings.align_to_grid:
                            vertex.align_to_grid()

                        side.plane.append(vertex)

                    u_axis, v_axis = self.calc_uv_axes(settings, mesh, polygon)
                    side.uaxis = pyvmf.Convert.string_to_uvaxis(u_axis)
                    side.vaxis = pyvmf.Convert.string_to_uvaxis(v_axis)

                    side.lightmapscale = settings.lightmap_scale

                    try:
                        side.material = mesh.materials[polygon.material_index].name.upper()
                    except:
                        side.material = 'tools/toolsnodraw'.upper()

                    solid.add_sides(side)

                solid.editor = pyvmf.Editor()

                self.solids.append(solid)


    def sort_into_parts(self, mesh):
        parts = []

        bm = bmesh.new()
        bm.from_mesh(mesh)

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

            parts.append([mesh.polygons[f.index] for f in faces])

        bm.free()

        return parts


    def calc_uv_axes(self, settings, mesh, polygon):
        points = []
        u_vals = []
        v_vals = []

        for loop_index in range(polygon.loop_start, polygon.loop_start + 3):
            loop = mesh.loops[loop_index]

            point = mesh.vertices[loop.vertex_index].co
            points.append(mathutils.Vector(point))

            if mesh.uv_layers:
                uv = mesh.uv_layers.active.data[loop_index].uv
                u_vals.append(uv[0])
                v_vals.append(uv[1])

        if not mesh.uv_layers:
            u_vals = [0, 0, 1]
            v_vals = [0, 1, 1]

        p1, p2, p3 = points
        u1, u2, u3 = u_vals
        v1, v2, v3 = v_vals

        tangent = -1 * ((p2 - p1) * (v3 - v1) - (p3 - p1) * (v2 - v1))
        bitangent = mathutils.Quaternion(polygon.normal, math.radians(90)) @ tangent

        # TODO: Calculate scale and offset

        tangent.normalize()
        bitangent.normalize()

        u_axis = f'[{tangent[0]} {tangent[1]} {tangent[2]} 0] {settings.texture_scale}'
        v_axis = f'[{bitangent[0]} {bitangent[1]} {bitangent[2]} 0] {settings.texture_scale}'

        return u_axis, v_axis
