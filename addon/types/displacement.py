import bpy
import bmesh
import mathutils
from .. pyvmf import pyvmf


class Vertex:
    def __init__(self):
        self.connected = []
        self.boundary = False
        self.corner = False


class Point:
    def __init__(self):
        self.xyz = None
        self.uv = None
        self.alpha = None

        self.boundary = False
        self.corner = False
        self.faces = []

        self.position = None
        self.direction = None
        self.distance = None


class Face:
    def __init__(self):
        self.points = []
        self.processed = False
        self.neighbors = [None] * 4


class DisplacementGroup:
    def __init__(self, mesh):

        # Setup mesh, vertices, points, faces, and displacements
        self.mesh = mesh
        self.vertices = [Vertex()] * len(mesh.vertices)
        self.points = [Point()] * len(mesh.loops)
        self.faces = [Face()] * len(mesh.polygons)
        self.displacements = []

        # Populate displacements
        self.get_xyz_and_uv_and_alpha()
        self.get_connected_and_marked()
        self.get_boundary_and_corner()
        self.get_faces_and_points()
        self.process_faces()
        self.sort_faces()
        self.get_position_and_direction_and_distance()


    def get_xyz_and_uv_and_alpha(self):

        # Iterate through mesh loops
        for loop in self.mesh.loops:

            # Get displacement point
            point = self.points[loop.index]

            # Get XYZ
            try:
                point.xyz = self.mesh.vertices[loop.vertex_index].co[0:3]
            except:
                point.xyz = [0, 0, 0]

            # Get UV
            try:
                point.uv = self.mesh.uv_layers.active.data[loop.index].uv[0:2]
            except:
                point.uv = [0, 0]

            # Get alpha
            try:
                point.alpha = self.mesh.vertex_colors.active.data[loop.index].color[0]
            except:
                point.alpha = 1.0


    def get_connected_and_marked(self):

        # Iterate through mesh edges
        for edge in self.mesh.edges:

            # Get temporary vertices in edge
            vertex_a = self.vertices[edge.vertices[0]]
            vertex_b = self.vertices[edge.vertices[1]]

            # Add vertices to each other's connected lists
            vertex_a.connected.append(vertex_b)
            vertex_b.connected.append(vertex_a)

            # If the edge is freestyle marked, its vertices are boundary
            vertex_a.boundary |= edge.use_freestyle_mark
            vertex_b.boundary |= edge.use_freestyle_mark


    def get_boundary_and_corner(self):

        # Iterate through temporary vertices
        for vertex in self.vertices:

            # If there are fewer than 4 connected vertices, this is vertex is boundary
            vertex.boundary |= len(vertex.connected) < 4

            # Skip non-boundary vertices
            if not vertex.boundary:
                continue

            # If there are 2 connected vertices, this vertex is a corner
            vertex.corner |= len(vertex.connected) == 2

            # Skip if we've already determined this is a corner
            if vertex.corner:
                continue

            # Count the amount of connected boundary vertices
            count = len(v for v in vertex.connected if v.boundary)

            # If all of, or more than 2, connected vertices are boundary, this vert is a corner
            vertex.corner |= count > 2 or count == len(vertex.connected)

        # Iterate through mesh loops
        for loop in self.mesh.loops:

            # Get displacement point and temporary vertex
            point = self.points[loop.index]
            vertex = self.vertices[loop.vertex_index]

            # Get boundary and corner
            point.boundary = vertex.boundary
            point.corner = vertex.corner


    def get_faces_and_points(self):

        # Iterate through mesh polygons
        for polygon in self.mesh.polygons:

            # Iterate through polygon loop indices
            for index in polygon.loop_indices:

                # Store the points in the face
                self.faces[polygon.index].points.append(self.points[index])

                # Store the face in the points
                self.points[index].faces.append(self.faces[polygon.index])

    # Rotate this face counter clockwise by the given amount of steps
    def rotate_face(self, face, steps):

        # Rotate the list to put this index at the start
        face.points = face.points[steps:] + face.points[:steps]

    # Find the faces on the left, top, right, and bottom of this face
    def find_neighbors(self, face):

        # If this face has been processed already
        if face.processed:

            # End the recursion
            return

        # Make sure this face isn't processed again
        face.processed = True

        # Iterate through the sides of this face
        for side in range(4):

            # Get the list of faces that the current point is in
            faces = face.points[side].faces

            # Get both points that are in the current edge
            points = [face.points[side], face.points[(side + 1) % 4]]

            # Get the unprocessed face of the current point that has both edge points
            face.neighbors[side] = next((f for f in faces if not f.processed and all(v in f.points for v in points)), None)

            # If a face is found on the current side, and it hasn't already been processed
            if face.neighbors[side] and not face.neighbors[side].processed:

                # Find the current point in this neighboring face
                index = face.neighbors[side].points.index(face.points[side])

                # Rotate this neighboring face so that the current point is in the correct corner
                self.rotate_face(face, (index + 3) % 4)

                # Find the neighbors of this neighboring face
                self.find_neighbors(face.neighbors[side])


    def process_faces(self):

        # Keep going until all faces are processed
        while True:

            # Start at any unsorted face
            face = next((f for f in self.faces if not f.processed), None)

            # If none are found, we're done
            if not face:
                break

            # Process the face and its neighbords recursively
            self.find_neighbors(face)


    def sort_faces(self):

        # Find bottom left corner faces
        corners = [f for f in self.faces if f.points[0].corner]

        # Iterate through those corners
        for corner in corners:

            # Create a displacement
            grid = []

            # Start in the corner
            edge = corner

            # Iterate through rows
            for row in range(16):

                # Add an empty row
                grid.append([])

                # Start at the edge
                face = edge

                # Iterate through columns
                for column in range(16):

                    # Add this face to the grid
                    grid[row].append(face)

                    # Stop at the end of the row
                    if face.points[2].boundary and face.points[3].boundary:
                        break

                    # Move to the right
                    face = face.neighbors[2]

                # Stop at the end of the column
                if edge.points[1].boundary and edge.points[2].boundary:
                    break

                # Move upwards
                edge = edge.neighbors[1]


    def get_position_and_direction_and_distance(self):

        pass # Direction and distance
        # TODO: Interpolate the position of the point on the brush face from the corners
        # TODO: Calculate the direction and distance from that point to the new coordinates


class DisplacementConverter:
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
        self.displacement_group = DisplacementGroup(mesh)

        # Clear the evaluated mesh
        evaluated.to_mesh_clear()

        # Switch back to the original mode
        if mode != 'OBJECT':
            bpy.ops.object.mode_set(mode)
