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
