import bpy
import bmesh
import mathutils
from .. pyvmf import pyvmf


class DispLoop:
    def __init__(self, index):
        self.index = index
        self.xyz = [0, 0, 0]
        self.uv = [0, 0]
        self.alpha = 1.0
        self.position = [0, 0, 0]
        self.direction = [0, 0, 0]
        self.distance = [0, 0, 0]


class DispVertex:
    def __init__(self, index):
        self.index = index
        self.connected = []
        self.boundary = False
        self.corner = False
        self.polygons = []


class DispPolygon:
    def __init__(self, index):
        self.index = index
        self.vertices = []
        self.processed = False
        self.neighbors = [None] * 4


class DispGroup:
    def __init__(self, mesh):

        # Setup mesh, vertices, loops, polygons, and displacements
        self.mesh = mesh
        self.loops = [DispLoop(i) for i in range(len(mesh.loops))]
        self.vertices = [DispVertex(i) for i in range(len(mesh.vertices))]
        self.polygons = [DispPolygon(i) for i in range(len(mesh.polygons))]
        self.displacements = []

        # Populate displacements
        self.get_xyz_and_uv_and_alpha()
        self.get_connected_and_marked()
        self.get_boundary_and_corner()
        self.get_polygons_and_vertices()
        self.process_polygons()
        self.sort_polygons()
        self.get_position_and_direction_and_distance()


    def get_xyz_and_uv_and_alpha(self):

        # Iterate through mesh loops
        for mesh_loop in self.mesh.loops:

            # Get displacement loop
            loop = self.loops[mesh_loop.index]

            # Get XYZ
            loop.xyz = self.mesh.vertices[mesh_loop.vertex_index].co[0:3]

            # Get UV
            if self.mesh.uv_layers:
                loop.uv = self.mesh.uv_layers.active.data[mesh_loop.index].uv[0:2]

            # Get alpha
            if self.mesh.vertex_colors:
                loop.alpha = self.mesh.vertex_colors.active.data[mesh_loop.index].color[0]


    def get_connected_and_marked(self):

        # Iterate through mesh edges
        for mesh_edge in self.mesh.edges:

            # Get temporary vertices in edge
            vertex_a = self.vertices[mesh_edge.vertices[0]]
            vertex_b = self.vertices[mesh_edge.vertices[1]]

            # Add vertices to each other's connected lists
            vertex_a.connected.append(vertex_b)
            vertex_b.connected.append(vertex_a)

            # If the edge is freestyle marked, its vertices are boundary
            vertex_a.boundary |= mesh_edge.use_freestyle_mark
            vertex_b.boundary |= mesh_edge.use_freestyle_mark


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
            count = len([v for v in vertex.connected if v.boundary])

            # If all of, or more than 2, connected vertices are boundary, this vert is a corner
            vertex.corner |= count > 2 or count == len(vertex.connected)


    def get_polygons_and_vertices(self):

        # Iterate through mesh polygons
        for mesh_polygon in self.mesh.polygons:

            # Get the displacement polygon
            polygon = self.polygons[mesh_polygon.index]

            # Iterate through polygon loop indices
            for index in mesh_polygon.loop_indices:

                # Get the displacement vertex
                vertex = self.vertices[self.mesh.loops[index].vertex_index]

                # Store the vertices in the polygon
                polygon.vertices.append(vertex)

                # Store the polygon in the vertices
                vertex.polygons.append(polygon)

    # Rotate this polygon counter clockwise by the given amount of steps
    def rotate_polygon(self, polygon, steps):

        # Rotate the list to put this index at the start
        polygon.vertices = polygon.vertices[steps:] + polygon.vertices[:steps]

    # Find the polygons on the left, top, right, and bottom of this polygon
    def find_neighbors(self, polygon):

        # If this polygon has been processed already
        if polygon.processed:

            # End the recursion
            return

        # Make sure this polygon isn't processed again
        polygon.processed = True

        # Iterate through the sides of this polygon
        for side in range(4):

            # Get the list of polygons that the current vertex is in
            polygons = polygon.vertices[side].polygons

            # Get both vertices that are in the current edge
            vertices = [polygon.vertices[side], polygon.vertices[(side + 1) % 4]]

            # Get the unprocessed polygon of the current vertex that has both edge vertices
            polygon.neighbors[side] = next((f for f in polygons if not f.processed and all(v in f.vertices for v in vertices)), None)

            # If a polygon is found on the current side, and it hasn't already been processed
            if polygon.neighbors[side] and not polygon.neighbors[side].processed:

                # Find the current vertex in this neighboring polygon
                index = polygon.neighbors[side].vertices.index(polygon.vertices[side])

                # Rotate this neighboring polygon so that the current vertex is in the correct corner
                self.rotate_polygon(polygon, (index + 3) % 4)

                # Find the neighbors of this neighboring polygon
                self.find_neighbors(polygon.neighbors[side])


    def process_polygons(self):

        # Keep going until all polygons are processed
        while True:

            # Start at any unsorted polygon
            polygon = next((f for f in self.polygons if not f.processed), None)

            # If none are found, we're done
            if not polygon:
                break

            # Process the polygon and its neighbords recursively
            self.find_neighbors(polygon)


    def sort_polygons(self):

        # Find bottom left corner polygons
        corners = [f for f in self.polygons if f.vertices[0].corner]

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
                polygon = edge

                # Iterate through columns
                for column in range(16):

                    # Add this polygon to the grid
                    grid[row].append(polygon)

                    # Stop at the end of the row
                    if polygon.vertices[2].boundary and polygon.vertices[3].boundary:
                        break

                    # Move to the right
                    polygon = polygon.neighbors[2]

                    # Stop at the end of the row??
                    if not polygon:
                        print('no polygon on the right')
                        break

                # Stop at the end of the column
                if edge.vertices[1].boundary and edge.vertices[2].boundary:
                    break

                # Move upwards
                edge = edge.neighbors[1]

                # Stop at the end of the column??
                if not polygon:
                    print('no polygon above')
                    break

            # Add the displacement to the list
            self.displacements.append(grid)


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
