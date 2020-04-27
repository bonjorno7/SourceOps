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

                polygon.flip()

                side.plane.clear()

                for vertex_index in polygon.vertices[0:3]:
                    vertex = mesh.vertices[vertex_index]
                    vertex = pyvmf.Vertex(*vertex.co)

                    vertex.multiply(settings.geometry_scale)

                    if settings.align_to_grid:
                        vertex.align_to_grid()

                    side.plane.append(vertex)

                tangent, bitangent = self.calc_tangents(mesh, polygon)
                tx, ty, tz = tangent
                bx, by, bz = bitangent

                side.uaxis = pyvmf.Convert.string_to_uvaxis(f'[{tx} {ty} {tz} 0] 0.5')
                side.vaxis = pyvmf.Convert.string_to_uvaxis(f'[{bx} {by} {bz} 0] 0.5')

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
