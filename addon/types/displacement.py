import bpy
import bmesh
import mathutils
from .. pyvmf import pyvmf
from .. utils import common
import pathlib


class DispLoop:
    def __init__(self, mesh, loop):
        self.index = loop.index
        self.xyz = mesh.vertices[loop.vertex_index].co[0:3]

        if mesh.uv_layers:
            uv = mesh.uv_layers.active.data[loop.index].uv[0:2]
            self.uv = [uv[0] * 128, uv[1] * 128]
        else:
            self.uv = [0, 0]

        if mesh.vertex_colors:
            self.alpha = mesh.vertex_colors.active.data[loop.index].color[0]
        else:
            self.alpha = 1.0

        self.offset = [self.xyz[0] - self.uv[0], self.xyz[1] - self.uv[1], self.xyz[2]]

        #x = (self.xyz[0] - self.uv[0]) ** 2
        #y = (self.xyz[1] - self.uv[1]) ** 2
        #z = (self.xyz[2] - 0) ** 2
        #self.direction = (x + y + z) ** 0.5

        #self.direction = [0, 0, 0]
        #self.distance = [0, 0, 0]
        #self.position = [0, 0, 0]
        #self.offset = [0, 0, 0]

    #def calculate(self):
    #    pass
        # Direction from UV to XYZ
        # Distance between UV and XYZ
        # Position interpolated between the UVs of the corners
        # Offset between Position and UV


class DispFace:
    def __init__(self, face):
        self.index = face.index
        self.loops = [loop.index for loop in face.loops]
        self.edges = [True] * 4
        self.faces = [-1] * 4

        for index, edge in enumerate(face.edges):
            if edge.smooth and not edge.is_boundary:
                self.edges[index] = False
                self.faces[index] = next((f.index for f in edge.link_faces if f != face), -1)

        self.processed = False
        self.oriented = False

    def rotate(self, steps):
        self.loops = self.loops[steps:] + self.loops[:steps]
        self.edges = self.edges[steps:] + self.edges[:steps]
        self.faces = self.faces[steps:] + self.faces[:steps]
        self.oriented = True


class DispInfo:
    def __init__(self, corner_face, disp_faces, disp_loops):

        # Setup the grid
        self.grid = []

        # Start at the corner
        edge_face = corner_face

        # Iterate through rows
        for row in range(16):

            # Add a new row
            self.grid.append([])

            # If we're on the last row
            if edge_face.edges[1]:

                # Add another row
                self.grid.append([])

            # Start at the edge
            current_face = edge_face

            # Iterate through columns
            for column in range(16):

                # Add the bottom left loop of this face to this position
                self.grid[row].append(disp_loops[current_face.loops[0]])

                # If we're on the last row
                if edge_face.edges[1]:

                    # Add the top left loop of this face to the position above
                    self.grid[row + 1].append(disp_loops[current_face.loops[1]])

                    # If we're also on the last column
                    if current_face.edges[2]:

                        # Add the top right loop of this face to the position on the above right
                        self.grid[row + 1].append(disp_loops[current_face.loops[2]])

                # If we're on the last column
                if current_face.edges[2]:

                    # Add the bottom right loop of this face to the position on the right
                    self.grid[row].append(disp_loops[current_face.loops[3]])

                    # And exit this row
                    break

                # Otherwise move to the right
                current_face = disp_faces[current_face.faces[2]]

            # If we're on the last row
            if edge_face.edges[1]:

                # Exit the grid
                break

            # Otherwise move upwards
            edge_face = disp_faces[edge_face.faces[1]]


class DispGroup:
    def __init__(self, mesh):

        # Setup bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)

        # Setup loops and faces
        self.loops = [DispLoop(mesh, loop) for loop in mesh.loops]
        self.faces = [DispFace(face) for face in bm.faces]
        self.orient_faces()

        # Find corners and setup displacements
        corners = [face for face in self.faces if face.edges[0] and face.edges[3]]
        self.displacements = [DispInfo(face, self.faces, self.loops) for face in corners]

        # Populate displacements
        self.get_position_and_direction_and_distance()

        # Free bmesh
        bm.free()


    def orient_faces(self):

        # Continue until all faces are oriented
        while True:

            # Find a face that hasn't yet been oriented
            face = next((face for face in self.faces if not face.oriented), None)

            # If all faces are oriented, we're done
            if not face:
                break

            # Start with the neighbors of this face
            layer = self.orient_neighbors(face)

            # Continue until all neighbors are oriented
            while layer:

                # Create the next set of neighbors
                neighbors = set()

                # Iterate through faces in this layer
                for face in layer:

                    # Add the oriented faces to the neighbors
                    neighbors.update(self.orient_neighbors(face))

                # And prepare for the next round
                layer = neighbors


    def orient_neighbors(self, face):

        # This face is hereby processed and oriented
        face.processed = True
        face.oriented = True

        # Find neighboring faces
        neighbors = [(self.faces[index] if index != -1 else None) for index in face.faces]

        # Iterate through those neighbors to orient them
        for index, neighbor in enumerate(neighbors):

            # Make sure it exists and hasn't been oriented yet
            if not neighbor or neighbor.oriented:
                continue

            # If this neighbor is on the top, its index is 1
            # If this neighbor is oriented correctly, this face would be the neighbor's neighbor 3
            # Subtract these: 3 - 1 = 2
            # Rotate 180 degrees: 2 + 2 = 4
            # I go with 6 instead of 2, just to be sure we get a positive number, and then % 4 it to make sure it fits in the list
            # So if orientation is correct, it will do nothing
            # But what if this face is the neighbor's neighbor 2?
            # Subtract: 2 - 1 = 1
            # Rotate 180: 1 + 2 = 3
            # So it will rotate 3 steps counter-clockwise
            # Meaning it goes from 2 to 1 to 0 to 3
            # Hopefully this makes sense
            steps = (neighbor.faces.index(face.index) - index + 6) % 4

            # If we should rotate, rotate
            if steps != 0:
                neighbor.rotate(steps)

            # Otherwise just say that we did
            else:
                neighbor.oriented = True

        # Return all neighbors that exist and haven't been processed yet
        return set(face for face in neighbors if face and not face.processed)


    def get_position_and_direction_and_distance(self):

        pass # Direction and distance
        # TODO: Interpolate the position of the vertex on the brush polygon from the corners
        # TODO: Calculate the direction and distance from that vertex to the new coordinates


class DispConverter:
    def __init__(self, object):

        # Switch to object mode
        mode = object.mode
        if mode != 'OBJECT':
            bpy.ops.object.mode_set('OBJECT')

        # Make sure the mesh is unwrapped
        if not object.data.uv_layers.active:
            print('No UV layers found for displacement, unwrapping')
            bpy.ops.uv.unwrap()

        # Make sure the mesh has vertex colors
        if not object.data.vertex_colors:
            print('No vertex colors found for displacement, creating')
            object.data.vertex_colors.new(do_init=False)

        # Get the evaluated mesh
        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated = object.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
        mesh.transform(object.matrix_world)

        # Sort the mesh into displacements
        self.displacement_group = DispGroup(mesh)

        # Clear the evaluated mesh
        evaluated.to_mesh_clear()

        # Switch back to the original mode
        if mode != 'OBJECT':
            bpy.ops.object.mode_set(mode)

        # --- Export --- #

        # TODO: Flip winding based on dot product or something
        # TODO: Interpolate UVs from corners so that offsets align on seams
        # TODO: Flip winding in general because everything is inside out

        vmf = pyvmf.new_vmf()

        for disp in self.displacement_group.displacements:
            uv1 = disp.grid[0][0].uv
            uv2 = disp.grid[0][-1].uv
            uv3 = disp.grid[-1][-1].uv
            uv4 = disp.grid[-1][0].uv

            #uv1 = [uv1[0] * 256, uv1[1] * 256]
            #uv2 = [uv2[0] * 256, uv2[1] * 256]
            #uv3 = [uv3[0] * 256, uv3[1] * 256]
            #uv4 = [uv4[0] * 256, uv4[1] * 256]

            v1 = pyvmf.Vertex(uv1[0], uv1[1], 0)
            v2 = pyvmf.Vertex(uv2[0], uv2[1], 0)
            v3 = pyvmf.Vertex(uv3[0], uv3[1], 0)
            v4 = pyvmf.Vertex(uv4[0], uv4[1], 0)

            v5 = pyvmf.Vertex(uv1[0], uv1[1], -8)
            v6 = pyvmf.Vertex(uv2[0], uv2[1], -8)
            v7 = pyvmf.Vertex(uv3[0], uv3[1], -8)
            v8 = pyvmf.Vertex(uv4[0], uv4[1], -8)

            f1 = pyvmf.Side(dic={'plane': f'({v1.x} {v1.y} {v1.z}) ({v3.x} {v3.y} {v3.z}) ({v2.x} {v2.y} {v2.z})'}) # top
            f2 = pyvmf.Side(dic={'plane': f'({v7.x} {v7.y} {v7.z}) ({v5.x} {v5.y} {v5.z}) ({v6.x} {v6.y} {v6.z})'}) # bottom
            f3 = pyvmf.Side(dic={'plane': f'({v4.x} {v4.y} {v4.z}) ({v7.x} {v7.y} {v7.z}) ({v3.x} {v3.y} {v3.z})'}) # front
            f4 = pyvmf.Side(dic={'plane': f'({v6.x} {v6.y} {v6.z}) ({v1.x} {v1.y} {v1.z}) ({v2.x} {v2.y} {v2.z})'}) # back
            f5 = pyvmf.Side(dic={'plane': f'({v3.x} {v3.y} {v3.z}) ({v6.x} {v6.y} {v6.z}) ({v2.x} {v2.y} {v2.z})'}) # right
            f6 = pyvmf.Side(dic={'plane': f'({v1.x} {v1.y} {v1.z}) ({v8.x} {v8.y} {v8.z}) ({v4.x} {v4.y} {v4.z})'}) # left

            dic = {f'row{index}': ' '.join(f'{vert.offset[0]} {vert.offset[1]} {vert.offset[2]}' for vert in row) for index, row in enumerate(disp.grid)}
            f1.dispinfo = pyvmf.DispInfo(dic={'power': 2, 'startposition': f'[{v1.x} {v1.y} {v1.z}]'}, children=[pyvmf.Child('offsets', dic)])

            solid = pyvmf.Solid()
            solid.add_sides(f1, f2, f3, f4, f5, f6)
            solid.editor = pyvmf.Editor()
            vmf.add_solids(solid)

        path = pathlib.Path(bpy.path.abspath('//vmf/test.vmf')).resolve()
        common.verify_folder(str(path.parent))
        path = str(path)
        vmf.export(path)
