import bpy
import bmesh
import mathutils
from .. pyvmf import pyvmf
from .. utils import common
import pathlib


class DispLoop:
    def __init__(self, loop: bpy.types.MeshLoop, mesh: bpy.types.Mesh):
        self.index = loop.index
        self.xyz = mesh.vertices[loop.vertex_index].co[0:3]

        if mesh.uv_layers:
            uv = mesh.uv_layers.active.data[loop.index].uv[0:2]
            self.uv = [uv[0] * 256, uv[1] * 256]
        else:
            self.uv = [0, 0]

        if mesh.vertex_colors:
            self.alpha = round(mesh.vertex_colors.active.data[loop.index].color[0] * 255)
        else:
            self.alpha = 255

    def calculate_offset(self, uv):
        self.uv = uv[0:2]
        self.offset = [self.xyz[0] - self.uv[0], self.xyz[1] - self.uv[1], self.xyz[2]]


class DispFace:
    def __init__(self, face: bmesh.types.BMFace, disp_loops: list):
        self.index = face.index
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


class DispInfo:
    def __init__(self, corner_face: DispFace, disp_faces: list):

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
        bottom_left = mathutils.Vector(self.grid[0][0].uv)
        bottom_right = mathutils.Vector(self.grid[0][-1].uv)
        top_right = mathutils.Vector(self.grid[-1][-1].uv)
        top_left = mathutils.Vector(self.grid[-1][0].uv)

        # Iterate through rows
        for row, loops in enumerate(self.grid):

            # Iterate through columns
            for column, loop in enumerate(loops):

                # Interpolate between the left and right
                horizontal = column / grid_size
                top = top_left.lerp(top_right, horizontal)
                bottom = bottom_left.lerp(bottom_right, horizontal)

                # Interpolate between the bottom and top
                vertical = row / grid_size
                center = bottom.lerp(top, vertical)

                # Update UV and calculate offset
                loop.calculate_offset(center)

            # Add this row to offsets and alphas
            self.offsets[f'row{row}'] = ' '.join(f'{loop.offset[0]} {loop.offset[1]} {loop.offset[2]}' for loop in loops)
            self.alphas[f'row{row}'] = ' '.join(f'{loop.alpha}' for loop in loops)


class DispGroup:
    def __init__(self, mesh: bpy.types.Mesh):

        # Setup bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)

        # Setup loops and faces
        self.loops = [DispLoop(loop, mesh) for loop in mesh.loops]
        self.faces = [DispFace(face, self.loops) for face in bm.faces]
        self.orient_faces()

        # Find corners and setup displacements
        corners = [face for face in self.faces if face.left_edge and face.bottom_edge]
        self.displacements = [DispInfo(face, self.faces) for face in corners]

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

        # TODO: Flip winding based on cross product or something? Because mirrored UVs don't work
        # TODO: Allow scaling UV and XYZ and lightmapscale by separate values
        # TODO: Export loop alphas as well
        # TODO: Read / write existing VMF files
        # TODO: Test how normals behave in game

        vmf = pyvmf.new_vmf()

        for disp in self.displacement_group.displacements:
            uv1 = disp.grid[0][0].uv
            uv2 = disp.grid[0][-1].uv
            uv3 = disp.grid[-1][-1].uv
            uv4 = disp.grid[-1][0].uv

            v1 = pyvmf.Vertex(uv1[0], uv1[1], 0)
            v2 = pyvmf.Vertex(uv2[0], uv2[1], 0)
            v3 = pyvmf.Vertex(uv3[0], uv3[1], 0)
            v4 = pyvmf.Vertex(uv4[0], uv4[1], 0)

            v5 = pyvmf.Vertex(uv1[0], uv1[1], -8)
            v6 = pyvmf.Vertex(uv2[0], uv2[1], -8)
            v7 = pyvmf.Vertex(uv3[0], uv3[1], -8)
            v8 = pyvmf.Vertex(uv4[0], uv4[1], -8)

            f1 = pyvmf.Side(dic={'plane': f'({v1.x} {v1.y} {v1.z}) ({v3.x} {v3.y} {v3.z}) ({v2.x} {v2.y} {v2.z})'}) # Top
            f2 = pyvmf.Side(dic={'plane': f'({v7.x} {v7.y} {v7.z}) ({v5.x} {v5.y} {v5.z}) ({v6.x} {v6.y} {v6.z})'}) # Bottom
            f3 = pyvmf.Side(dic={'plane': f'({v4.x} {v4.y} {v4.z}) ({v7.x} {v7.y} {v7.z}) ({v3.x} {v3.y} {v3.z})'}) # Front
            f4 = pyvmf.Side(dic={'plane': f'({v6.x} {v6.y} {v6.z}) ({v1.x} {v1.y} {v1.z}) ({v2.x} {v2.y} {v2.z})'}) # Back
            f5 = pyvmf.Side(dic={'plane': f'({v3.x} {v3.y} {v3.z}) ({v6.x} {v6.y} {v6.z}) ({v2.x} {v2.y} {v2.z})'}) # Right
            f6 = pyvmf.Side(dic={'plane': f'({v1.x} {v1.y} {v1.z}) ({v8.x} {v8.y} {v8.z}) ({v4.x} {v4.y} {v4.z})'}) # Left

            size = len(disp.grid) - 1
            power = 4 if size == 16 else 3 if size == 8 else 2
            dic = {'power': power, 'startposition': f'[{v1.x} {v1.y} {v1.z}]'}
            offsets = pyvmf.Child('offsets', disp.offsets)
            alphas = pyvmf.Child('alphas', disp.alphas)
            f1.dispinfo = pyvmf.DispInfo(dic=dic, children=[offsets, alphas])

            solid = pyvmf.Solid()
            solid.add_sides(f1, f2, f3, f4, f5, f6)
            solid.editor = pyvmf.Editor()
            vmf.add_solids(solid)

        path = pathlib.Path(bpy.path.abspath('//vmf/test.vmf')).resolve()
        common.verify_folder(str(path.parent))
        path = str(path)
        vmf.export(path)
