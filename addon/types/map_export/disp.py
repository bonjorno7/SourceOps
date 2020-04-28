import bpy
import bmesh
import mathutils
import pathlib
from .. pyvmf import pyvmf


class Loop:
    def __init__(self, settings, loop: bpy.types.MeshLoop, mesh: bpy.types.Mesh):
        self.index = loop.index

        xyz = mesh.vertices[loop.vertex_index].co[0:3]
        self.xyz = [number * settings.geometry_scale for number in xyz]

        if mesh.uv_layers:
            self.uv = mesh.uv_layers.active.data[loop.index].uv[0:2]
            self.uv = [number * settings.uv_scale for number in self.uv]

            if settings.align_to_grid:
                self.uv = [round(number) for number in self.uv]

        else:
            self.uv = [0, 0]

        if mesh.vertex_colors:
            self.alpha = round(mesh.vertex_colors.active.data[loop.index].color[0] * 255)
        else:
            self.alpha = 255

    def calculate_offset(self, uv):
        self.uv = uv[0:2]
        self.offset = [self.xyz[0] - self.uv[0], self.xyz[1] - self.uv[1], self.xyz[2]]


class Face:
    def __init__(self, settings, face: bmesh.types.BMFace, disp_loops: list):
        self.index = face.index
        self.material = face.material_index
        self.loops = [disp_loops[loop.index] for loop in face.loops]
        self.edges = [True] * 4
        self.faces = [-1] * 4

        for index, edge in enumerate(face.edges):
            if edge.smooth and not edge.is_boundary:
                self.edges[index] = False
                self.faces[index] = next((f.index for f in edge.link_faces if f != face), -1)

        self.processed = False
        self.oriented = False

    def rotate(self, steps: int):
        self.loops = self.loops[steps:] + self.loops[:steps]
        self.edges = self.edges[steps:] + self.edges[:steps]
        self.faces = self.faces[steps:] + self.faces[:steps]
        self.oriented = True

    @property
    def top_left_loop(self):
        return self.loops[0]

    @property
    def bottom_left_loop(self):
        return self.loops[1]

    @property
    def bottom_right_loop(self):
        return self.loops[2]

    @property
    def top_right_loop(self):
        return self.loops[3]

    @property
    def left_edge(self):
        return self.edges[0]

    @property
    def bottom_edge(self):
        return self.edges[1]

    @property
    def right_edge(self):
        return self.edges[2]

    @property
    def top_edge(self):
        return self.edges[3]

    @property
    def left_face(self):
        return self.faces[0]

    @property
    def bottom_face(self):
        return self.faces[1]

    @property
    def right_face(self):
        return self.faces[2]

    @property
    def top_face(self):
        return self.faces[3]


class Disp:
    def __init__(self, settings, corner_face: Face, disp_faces: list, mesh: bpy.types.Mesh):

        # Try to get the material from the mesh
        try:
            self.material = mesh.materials[corner_face.material].name.upper()

        # Otherwise just use nodraw
        except:
            self.material = 'tools/toolsnodraw'.upper()

        # Setup the grid
        self.grid = []

        # Start at the corner
        edge_face = corner_face

        # Iterate through rows
        for row in range(16):

            # Add a new row
            self.grid.append([])

            # If we're on the last row
            if edge_face.top_edge:

                # Add another row
                self.grid.append([])

            # Start at the edge
            current_face = edge_face

            # Iterate through columns
            for column in range(16):

                # Add the bottom left loop of this face to this position
                self.grid[row].append(current_face.bottom_left_loop)

                # If we're on the last row
                if current_face.top_edge:

                    # Add the top left loop of this face to the position above
                    self.grid[row + 1].append(current_face.top_left_loop)

                    # If we're also on the last column
                    if current_face.right_edge:

                        # Add the top right loop of this face to the position on the above right
                        self.grid[row + 1].append(current_face.top_right_loop)

                # If we're on the last column
                if current_face.right_edge:

                    # Add the bottom right loop of this face to the position on the right
                    self.grid[row].append(current_face.bottom_right_loop)

                    # And exit this row
                    break

                # Otherwise move to the right
                current_face = disp_faces[current_face.right_face]

            # If we're on the last row
            if edge_face.top_edge:

                # Exit the grid
                break

            # Otherwise move upwards
            edge_face = disp_faces[edge_face.top_face]

        # Setup offsets and alphas
        self.offsets = {}
        self.alphas = {}

        # Get the size of the loop grid
        grid_size = len(self.grid) - 1

        # Get the UV coordinates of the grid corners
        self.bottom_left = mathutils.Vector(self.grid[0][0].uv)
        self.bottom_right = mathutils.Vector(self.grid[0][-1].uv)
        self.top_right = mathutils.Vector(self.grid[-1][-1].uv)
        self.top_left = mathutils.Vector(self.grid[-1][0].uv)

        # Iterate through rows
        for row, loops in enumerate(self.grid):

            # Iterate through columns
            for column, loop in enumerate(loops):

                # Interpolate between the left and right
                horizontal = column / grid_size
                top = self.top_left.lerp(self.top_right, horizontal)
                bottom = self.bottom_left.lerp(self.bottom_right, horizontal)

                # Interpolate between the bottom and top
                vertical = row / grid_size
                center = bottom.lerp(top, vertical)

                # Update UV and calculate offset
                loop.calculate_offset(center)

            # Add this row to offsets and alphas
            self.offsets[f'row{row}'] = ' '.join(f'{loop.offset[0]} {loop.offset[1]} {loop.offset[2]}' for loop in loops)
            self.alphas[f'row{row}'] = ' '.join(f'{loop.alpha}' for loop in loops)


class Group:
    def __init__(self, settings, mesh: bpy.types.Mesh):

        # Setup a bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)

        # Setup loops and faces
        disp_loops = [Loop(settings, loop, mesh) for loop in mesh.loops]
        disp_faces = [Face(settings, face, disp_loops) for face in bm.faces]

        # Free the bmesh
        bm.free()

        # Orient displacement faces
        self.orient_faces(disp_faces)

        # Find corners and setup displacements
        corners = [face for face in disp_faces if face.left_edge and face.bottom_edge]
        self.disps = [Disp(settings, face, disp_faces, mesh) for face in corners]

    # Make sure all displacement faces are oriented correctly
    def orient_faces(self, disp_faces: list):

        # Continue until all faces are oriented
        while True:

            # Find a face that hasn't yet been oriented
            face = next((face for face in disp_faces if not face.oriented), None)

            # If all faces are oriented, we're done
            if not face:
                break

            # Start with the neighbors of this face
            layer = self.orient_neighbors(face, disp_faces)

            # Continue until all neighbors are oriented
            while layer:

                # Create the next set of neighbors
                neighbors = set()

                # Iterate through faces in this layer
                for face in layer:

                    # Add the oriented faces to the neighbors
                    neighbors.update(self.orient_neighbors(face, disp_faces))

                # And prepare for the next round
                layer = neighbors

    # Make the orientation of the neighbors of this face match its own
    def orient_neighbors(self, face: Face, disp_faces: list):

        # This face is hereby processed and oriented
        face.processed = True
        face.oriented = True

        # Find neighboring faces
        neighbors = [(disp_faces[index] if index != -1 else None) for index in face.faces]

        # Iterate through those neighbors to orient them
        for index, neighbor in enumerate(neighbors):

            # Make sure it exists and hasn't been oriented yet
            if not neighbor or neighbor.oriented:
                continue

            # Determine how much to rotate this neighbor so that it's oriented the same way as this face
            steps = (neighbor.faces.index(face.index) - index + 6) % 4

            # If we should rotate, rotate
            if steps != 0:
                neighbor.rotate(steps)

            # Otherwise just say that we did
            else:
                neighbor.oriented = True

        # Return all neighbors that exist and haven't been processed yet
        return set(face for face in neighbors if face and not face.processed)


class Converter:
    def __init__(self, settings, meshes: list):

        # Setup a list of displacements
        self.disps = []

        # Iterate through our meshes
        for mesh in meshes:

            # Sort the mesh into displacements
            self.disps.extend(Group(settings, mesh).disps)

        # Setup a list of solids
        self.solids = []

        # Iterate through our displacements
        for disp in self.disps:

            # Get the displacement UV corners
            uv1 = disp.bottom_left
            uv2 = disp.bottom_right
            uv3 = disp.top_right
            uv4 = disp.top_left

            # Get the top brush corners
            v1 = pyvmf.Vertex(uv1.x, uv1.y, 0)
            v2 = pyvmf.Vertex(uv2.x, uv2.y, 0)
            v3 = pyvmf.Vertex(uv3.x, uv3.y, 0)
            v4 = pyvmf.Vertex(uv4.x, uv4.y, 0)

            # Get the bottom brush corners
            v5 = pyvmf.Vertex(uv1.x, uv1.y, -8)
            v6 = pyvmf.Vertex(uv2.x, uv2.y, -8)
            v7 = pyvmf.Vertex(uv3.x, uv3.y, -8)
            v8 = pyvmf.Vertex(uv4.x, uv4.y, -8)

            # Create brush sides
            f1 = pyvmf.Side(dic={'plane': f'({v1.x} {v1.y} {v1.z}) ({v3.x} {v3.y} {v3.z}) ({v2.x} {v2.y} {v2.z})'}) # Top
            f2 = pyvmf.Side(dic={'plane': f'({v7.x} {v7.y} {v7.z}) ({v5.x} {v5.y} {v5.z}) ({v6.x} {v6.y} {v6.z})'}) # Bottom
            f3 = pyvmf.Side(dic={'plane': f'({v4.x} {v4.y} {v4.z}) ({v7.x} {v7.y} {v7.z}) ({v3.x} {v3.y} {v3.z})'}) # Front
            f4 = pyvmf.Side(dic={'plane': f'({v6.x} {v6.y} {v6.z}) ({v1.x} {v1.y} {v1.z}) ({v2.x} {v2.y} {v2.z})'}) # Back
            f5 = pyvmf.Side(dic={'plane': f'({v3.x} {v3.y} {v3.z}) ({v6.x} {v6.y} {v6.z}) ({v2.x} {v2.y} {v2.z})'}) # Right
            f6 = pyvmf.Side(dic={'plane': f'({v1.x} {v1.y} {v1.z}) ({v8.x} {v8.y} {v8.z}) ({v4.x} {v4.y} {v4.z})'}) # Left

            # Set texture and lightmap scales
            for side in [f1, f2, f3, f4, f5, f6]:
                side.uaxis.scale = settings.texture_scale
                side.vaxis.scale = settings.texture_scale
                side.lightmapscale = settings.lightmap_scale

            # Add material to top face
            f1.material = disp.material

            # Setup dispinfo for the top brush side
            size = len(disp.grid) - 1
            power = 4 if size == 16 else 3 if size == 8 else 2
            dic = {'power': power, 'startposition': f'[{v1.x} {v1.y} {v1.z}]'}
            offsets = pyvmf.Child('offsets', disp.offsets)
            alphas = pyvmf.Child('alphas', disp.alphas)
            f1.dispinfo = pyvmf.DispInfo(dic=dic, children=[offsets, alphas])

            # Create a solid of the sides and append it
            solid = pyvmf.Solid()
            solid.add_sides(f1, f2, f3, f4, f5, f6)
            solid.editor = pyvmf.Editor()
            self.solids.append(solid)
