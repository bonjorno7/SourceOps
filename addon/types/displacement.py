import bpy
import bmesh
import mathutils
from .. pyvmf import pyvmf


class TempVert:
    def __init__(self):
        self.connected = []
        self.boundary = False
        self.corner = False


class DispVert:
    def __init__(self):
        self.xyz = [0, 0, 0]
        self.uv = [0, 0]
        self.alpha = 1.0

        boundary = False
        corner = False
        self.faces = []

        self.direction = [0, 0, 0]
        self.distance = 1.0


class DispFace:
    def __init__(self):
        self.verts = []
        self.processed = False
        self.neighbors = [None] * 4

    # Rotate this face counter clockwise by the given amount of steps
    def rotate(self, steps):

        # Rotate the list to put this index at the start
        self.verts = self.verts[steps:] + self.verts[:steps]

    # Find the faces on the left, top, right, and bottom of this face
    def find_neighbors(self):

        # If this face has been processed already
        if self.processed:

            # End the recursion
            return

        # Make sure this face isn't processed again
        self.processed = True

        # Iterate through the sides of this face
        for side in range(4):

            # Get the list of faces that the current vert is in
            faces = self.verts[side].faces

            # Get both verts that are in the current edge
            verts = [self.verts[side], self.verts[(side + 1) % 4]]

            # Get the unprocessed face of the current vert that has both edge verts
            self.neighbors[side] = next((f for f in faces if not f.processed and all(v in f.verts for v in verts)), None)

            # If a face is found on the current side, and it hasn't already been processed
            if self.neighbors[side] and not self.neighbors[side].processed:

                # Find the current vert in this neighboring face
                index = self.neighbors[side].verts.index(self.verts[side])

                # Rotate this neighboring face so that the current vert is in the correct corner
                self.neighbors[side].rotate((index + 3) % 4)

                # Find the neighbors of this neighboring face
                self.neighbors[side].find_neighbors()


class Displacement:
    pass


class DisplacementGroup:
    def __init__(self, mesh):

        # Setup mesh, temporary verts, displacement verts and faces, and displacements
        self.mesh = mesh
        self.temp_verts = [TempVert()] * len(mesh.vertices)
        self.disp_verts = [DispVert()] * len(mesh.loops)
        self.disp_faces = [DispFace()] * len(mesh.faces)
        self.displacements = []

        self.get_connections_and_marked()
        self.get_boundaries_and_corners()
        self.get_xyz_uv_alpha_boundary_corner()
        self.get_faces_and_verts()
        self.process_faces()
        self.sort_faces()
        self.direction_and_distance()


    def get_connections_and_marked(self):

        # Iterate through mesh edges
        for edge in self.mesh.edges:

            # Get edge verts
            vert_a = self.temp_verts[edge.vertices[0]]
            vert_b = self.temp_verts[edge.vertices[1]]

            # Add verts to each other's connected lists
            vert_a.connected.append(vert_b)
            vert_b.connected.append(vert_a)

            # If the edge is freestyle marked, its verts are boundary
            vert_a.boundary |= edge.use_freestyle_mark
            vert_b.boundary |= edge.use_freestyle_mark


    def get_boundaries_and_corners(self):

        # Iterate through temporary verts
        for vert in self.temp_verts:

            # If there are fewer than 4 connected verts, this is vert is boundary
            vert.boundary |= len(vert.connected) < 4

            # Skip non-boundary verts
            if not vert.boundary:
                continue

            # If there are 2 connected verts, this vert is a corner
            vert.corner |= len(vert.connected) == 2

            # Skip if we've already determined this is a corner
            if vert.corner:
                continue

            # Count the amount of connected boundary verts
            count = len(v for v in vert.connected if v.boundary)

            # If all of, or more than 2, connected verts are boundary, this vert is a corner
            vert.corner |= count > 2 or count == len(vert.connected)


    def get_xyz_uv_alpha_boundary_corner(self):

        # Iterate through mesh loops
        for loop in self.mesh.loops:

            # Get displacement vert and temprary vert
            disp_vert = self.disp_verts[loop.index]
            temp_vert = self.temp_verts[loop.vertex_index]

            # Get XYZ, UV, and alpha
            disp_vert.xyz = self.mesh.vertices[loop.vertex_index].co[0:3]
            disp_vert.uv = self.mesh.uv_layers.active.data[loop.index].uv[0:2]
            disp_vert.alpha = self.mesh.vertex_colors.active.data[loop.index].color[0]

            # Get boundary and corner
            disp_vert.boundary = temp_vert.boundary
            disp_vert.corner = temp_vert.corner


    def get_faces_and_verts(self):

        # Iterate through mesh polygons
        for polygon in self.mesh.polygons:

            # Iterate through polygon loop indices
            for index in polygon.loop_indices:

                # Store the verts in the face
                self.disp_faces[polygon.index].verts.append(self.disp_verts[index])

                # Store the face in the verts
                self.disp_verts[index].faces.append(self.disp_faces[polygon.index])


    def process_faces(self):

        # Keep going until all faces are processed
        while True:

            # Start at any unsorted face
            face = next((f for f in self.disp_faces if not f.processed), None)

            # If none are found, we're done
            if not face:
                break

            # Process the face and its neighbords recursively
            face.find_neighbors()


    def sort_faces(self):

        # Find bottom left corner faces
        corners = [f for f in self.disp_faces if f.verts[0].corner]

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
                    if face.verts[2].boundary and face.verts[3].boundary:
                        break

                    # Move to the right
                    face = face.neighbors[2]

                # Stop at the end of the column
                if edge.verts[1].boundary and edge.verts[2].boundary:
                    break

                # Move upwards
                edge = edge.neighbors[1]


    def direction_and_distance(self):

        pass # Direction and distance
        # TODO: Interpolate the position of the point on the brush face from the corners
        # TODO: Calculate the direction and distance from that point to the new coordinates


    def from_blender(self, object):

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


        # This is where it should start, preparing the mesh should be done from the place that calls this



        # This is where it should end, afterwards the displacements should be exported and the scene cleaned up


        # Clear the evaluated mesh
        evaluated.to_mesh_clear()
