import bpy
import bmesh
import mathutils
import pathlib
from .. pyvmf import pyvmf


class Converter:
    def __init__(self, settings, meshes: list):
        self.solids = []

        for mesh in meshes:
            solid = pyvmf.Solid()

            for polygon in mesh.polygons:
                side = pyvmf.Side()

                for index, vertex in enumerate(polygon.vertices[0:3]):
                    v = mathutils.Vector(mesh.vertices[vertex].co)
                    v *= settings.geometry_scale

                    if settings.align_to_grid:
                        v.x = round(v.x)
                        v.y = round(v.y)
                        v.z = round(v.z)

                    side.plane[2 - index] = pyvmf.Vertex(v.x, v.y, v.z)
                    side.lightmapscale = settings.lightmap_scale

                solid.add_sides(side)

            solid.editor = pyvmf.Editor()

            self.solids.append(solid)


    def calc_tangents(self, mesh, polygon):
        points = []
        u_vals = []
        v_vals = []

        for loop_index in range(polygon.loop_start, polygon.loop_start + 3):
            loop = mesh.loops[loop_index]

            point = mesh.vertices[loop.vertex_index].co
            points.append(mathutils.Vector(point))

            uv = mesh.uv_layers.active.data[loop_index].uv
            u_vals.append(uv[0])
            v_vals.append(uv[1])

        p1, p2, p3 = points
        u1, u2, u3 = u_vals
        v1, v2, v3 = v_vals

        tangent = mathutils.Vector((p2 - p1) * (v3 - v1) - (p3 - p1) * (v2 - v1))
        bitangent = mathutils.Vector((p3 - p1) * (u2 - u1) - (p2 - p1) * (u3 - u1))

        tangent.negate()

        # TODO: Calculate scale and offset

        tangent.normalize()
        bitangent.normalize()

        return tangent, bitangent
