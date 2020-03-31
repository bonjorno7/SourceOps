import bpy
import bmesh
import mathutils
from .. pyvmf import pyvmf


class DispLoop:
    def __init__(self, mesh, loop):
        self.index = loop.index
        self.xyz = mesh.vertices[loop.vertex_index].co[0:3]

        if mesh.uv_layers:
            self.uv = mesh.uv_layers.active.data[loop.index].uv[0:2]
        else:
            self.uv = [0, 0]

        if mesh.vertex_colors:
            self.alpha = mesh.vertex_colors.active.data[loop.index].color[0]
        else:
            self.alpha = 1.0

        self.position = [0, 0, 0]
        self.direction = [0, 0, 0]
        self.distance = [0, 0, 0]


class DispFace:
    def __init__(self, face):
        self.index = face.index
        self.loops = [loop.index for loop in face.loops]
        self.neighbors = [self.find_neighbor(edge) for edge in face.edges]
        self.boundaries = [self.find_boundary(edge) for edge in face.edges]
        self.is_corner = self.boundaries[0] and self.boundaries[3]

    def find_neighbor(self, edge):
        return next((face.index for face in edge.link_faces if face.index != self.index), -1)

    def find_boundary(self, edge):
        return edge.is_boundary or not edge.smooth


class Disp:
    def __init__(self, corner_face, disp_faces, disp_loops):
        self.setup_face_grid(corner_face, disp_faces)
        self.setup_loop_grid(disp_loops)

    def setup_face_grid(self, corner_face, all_faces):

        # Setup face grid
        self.face_grid = []

        # Start in the corner
        edge_face = corner_face

        # Iterate through rows
        for row in range(16):

            # Add an empty row
            self.face_grid.append([])

            # Start at the edge
            column_face = edge_face

            # Iterate through columns
            for column in range(16):

                # Add this polygon to the grid
                self.face_grid[row].append(column_face)

                # Stop at the end of the row
                if column_face.boundaries[2]:
                    break

                # Move to the right
                column_face = all_faces[column_face.neighbors[2]]

            # Stop at the end of the column
            if edge_face.boundaries[1]:
                break

            # Move upwards
            edge_face = all_faces[edge_face.neighbors[1]]

    def setup_loop_grid(self, all_loops):

        # Setup loop grid
        self.loop_grid = []

        # Determine the size of the face grid
        size = len(self.face_grid)

        # Iterate through face rows
        for row in range(size):

            # Add a new loop row
            self.loop_grid.append([])

            # Iterate through face columns
            for column in range(size):

                # Add the bottom left loop of each face
                self.loop_grid[row].append(all_loops[self.face_grid[row][column].loops[0]])

            # Add the bottom right loop of the last face
            self.loop_grid[row].append(all_loops[self.face_grid[row][size - 1].loops[3]])

        # Add an extra loop row
        self.loop_grid.append([])

        # Iterate through columns in the last face row
        for column in range(size):

            # Add the top left loop of each face
            self.loop_grid[size].append(all_loops[self.face_grid[size - 1][column].loops[1]])

        # Add the top right loop of the top right face
        self.loop_grid[size].append(all_loops[self.face_grid[size - 1][size - 1].loops[2]])


class DispGroup:
    def __init__(self, mesh):

        # Setup bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)

        # Setup loops and faces
        self.loops = [DispLoop(mesh, loop) for loop in mesh.loops]
        self.faces = [DispFace(face) for face in bm.faces]

        # Setup displacements
        corners = [face for face in self.faces if face.is_corner]
        self.displacements = [Disp(face, self.faces, self.loops) for face in corners]

        # Populate displacements
        self.get_position_and_direction_and_distance()

        # Free bmesh
        bm.free()


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
