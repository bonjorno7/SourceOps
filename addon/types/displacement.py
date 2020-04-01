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
        self.faces = [self.find_face(edge) for edge in face.edges]
        self.edges = [self.find_edge(edge) for edge in face.edges]
        self.is_corner = self.edges[0] and self.edges[3]

    def find_face(self, edge):
        return next((face.index for face in edge.link_faces if face.index != self.index), -1)

    def find_edge(self, edge):
        return edge.is_boundary or not edge.smooth


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
                if current_face.edges[1]:

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

        # Setup loops, faces, and displacements
        self.loops = [DispLoop(mesh, loop) for loop in mesh.loops]
        self.faces = [DispFace(face) for face in bm.faces]
        self.displacements = [DispInfo(face, self.faces, self.loops) for face in self.faces if face.is_corner]

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
