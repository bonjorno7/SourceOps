import bpy
import bmesh
import mathutils
from .. pyvmf import pyvmf
import pathlib


class DispSettings:
    def __init__(self, path, objects, align_to_grid, brush_scale, geometry_scale, lightmap_scale):
        self.path = path
        self.objects = objects
        self.align_to_grid = align_to_grid
        self.brush_scale = brush_scale
        self.geometry_scale = geometry_scale
        self.lightmap_scale = lightmap_scale


class DispLoop:
    def __init__(self, settings: DispSettings, loop: bpy.types.MeshLoop, mesh: bpy.types.Mesh):
        self.index = loop.index

        xyz = mesh.vertices[loop.vertex_index].co[0:3]
        self.xyz = [number * settings.geometry_scale for number in xyz]

        if mesh.uv_layers:
            self.uv = mesh.uv_layers.active.data[loop.index].uv[0:2]
            self.uv = [number * settings.brush_scale for number in self.uv]

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


class DispFace:
    def __init__(self, settings: DispSettings, face: bmesh.types.BMFace, disp_loops: list):
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


class DispInfo:
    def __init__(self, settings: DispSettings, corner_face: DispFace, disp_faces: list, mesh: bpy.types.Mesh):

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
    def __init__(self, settings: DispSettings, mesh: bpy.types.Mesh):

        # Setup a bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)

        # Setup loops and faces
        disp_loops = [DispLoop(settings, loop, mesh) for loop in mesh.loops]
        disp_faces = [DispFace(settings, face, disp_loops) for face in bm.faces]

        # Free the bmesh
        bm.free()

        # Orient displacement faces
        self.orient_faces(disp_faces)

        # Find corners and setup displacements
        corners = [face for face in disp_faces if face.left_edge and face.bottom_edge]
        self.displacements = [DispInfo(settings, face, disp_faces, mesh) for face in corners]

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
    def orient_neighbors(self, face: DispFace, disp_faces: list):

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


class DispExporter:
    def __init__(self, settings: DispSettings):

        # Setup a list of displacements
        self.displacements = []

        # Configure the scene
        scene_settings = self.configure_scene(settings.objects)

        # Iterate through our objects
        for object in settings.objects:

            # Get the evaluated mesh
            depsgraph = bpy.context.evaluated_depsgraph_get()
            evaluated = object.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)

            # Apply object transforms
            mesh.transform(object.matrix_world)

            # Sort the mesh into displacements
            self.displacements.extend(DispGroup(settings, mesh).displacements)

            # Clear the evaluated mesh
            evaluated.to_mesh_clear()

        # Restore the scene
        self.restore_scene(settings.objects, scene_settings)

        # TODO: Flip winding based on cross product or something? Because mirrored UVs don't work
        # TODO: Read / write existing VMF files, remove stuff in the given visgroup first

        # Create a new VMF file
        vmf = pyvmf.new_vmf()

        # Iterate through our displacements
        for disp in self.displacements:

            # Get the displacement UV corners
            uv1 = disp.grid[0][0].uv
            uv2 = disp.grid[0][-1].uv
            uv3 = disp.grid[-1][-1].uv
            uv4 = disp.grid[-1][0].uv

            # Get the top brush corners
            v1 = pyvmf.Vertex(uv1[0], uv1[1], 0)
            v2 = pyvmf.Vertex(uv2[0], uv2[1], 0)
            v3 = pyvmf.Vertex(uv3[0], uv3[1], 0)
            v4 = pyvmf.Vertex(uv4[0], uv4[1], 0)

            # Get the bottom brush corners
            v5 = pyvmf.Vertex(uv1[0], uv1[1], -8)
            v6 = pyvmf.Vertex(uv2[0], uv2[1], -8)
            v7 = pyvmf.Vertex(uv3[0], uv3[1], -8)
            v8 = pyvmf.Vertex(uv4[0], uv4[1], -8)

            # Create brush sides
            f1 = pyvmf.Side(dic={'plane': f'({v1.x} {v1.y} {v1.z}) ({v3.x} {v3.y} {v3.z}) ({v2.x} {v2.y} {v2.z})', 'lightmapscale': settings.lightmap_scale, 'material' : disp.material}) # Top
            f2 = pyvmf.Side(dic={'plane': f'({v7.x} {v7.y} {v7.z}) ({v5.x} {v5.y} {v5.z}) ({v6.x} {v6.y} {v6.z})', 'lightmapscale': settings.lightmap_scale}) # Bottom
            f3 = pyvmf.Side(dic={'plane': f'({v4.x} {v4.y} {v4.z}) ({v7.x} {v7.y} {v7.z}) ({v3.x} {v3.y} {v3.z})', 'lightmapscale': settings.lightmap_scale}) # Front
            f4 = pyvmf.Side(dic={'plane': f'({v6.x} {v6.y} {v6.z}) ({v1.x} {v1.y} {v1.z}) ({v2.x} {v2.y} {v2.z})', 'lightmapscale': settings.lightmap_scale}) # Back
            f5 = pyvmf.Side(dic={'plane': f'({v3.x} {v3.y} {v3.z}) ({v6.x} {v6.y} {v6.z}) ({v2.x} {v2.y} {v2.z})', 'lightmapscale': settings.lightmap_scale}) # Right
            f6 = pyvmf.Side(dic={'plane': f'({v1.x} {v1.y} {v1.z}) ({v8.x} {v8.y} {v8.z}) ({v4.x} {v4.y} {v4.z})', 'lightmapscale': settings.lightmap_scale}) # Left

            # Setup dispinfo for the top brush side
            size = len(disp.grid) - 1
            power = 4 if size == 16 else 3 if size == 8 else 2
            dic = {'power': power, 'startposition': f'[{v1.x} {v1.y} {v1.z}]'}
            offsets = pyvmf.Child('offsets', disp.offsets)
            alphas = pyvmf.Child('alphas', disp.alphas)
            f1.dispinfo = pyvmf.DispInfo(dic=dic, children=[offsets, alphas])

            # Create a solid of the sides and add it to the VMF
            solid = pyvmf.Solid()
            solid.add_sides(f1, f2, f3, f4, f5, f6)
            solid.editor = pyvmf.Editor()
            vmf.add_solids(solid)

        # Export the VMF to a file
        path = pathlib.Path(settings.path).resolve()
        if path.suffix.lower() != '.vmf':
            path = path.with_suffix('.vmf')
        path.parent.mkdir(parents=True, exist_ok=True)
        vmf.export(str(path))

    # Make sure all objects are accesible to the code
    def configure_scene(self, objects):
        scene_settings = {o: {} for o in objects}

        if bpy.context.active_object:
            scene_settings['mode'] = bpy.context.active_object.mode
            bpy.ops.object.mode_set(mode='OBJECT')
        else:
            scene_settings['mode'] = 'OBJECT'

        for object in objects:
            scene_settings[object]['in_scene'] = bpy.context.scene.collection in object.users_collection
            if not scene_settings[object]['in_scene']:
                bpy.context.scene.collection.objects.link(object)

            scene_settings[object]['hide_viewport'] = True if object.hide_viewport else False
            object.hide_viewport = False

        return scene_settings

    # Restore everything to how it was before export
    def restore_scene(self, objects, scene_settings):
        for object in objects:
            if not scene_settings[object]['in_scene']:
                bpy.context.scene.collection.objects.unlink(object)

            object.hide_viewport = scene_settings[object]['hide_viewport']

        if scene_settings['mode'] != 'OBJECT':
            bpy.ops.object.mode_set(mode=scene_settings['mode'])
