import bpy
import bmesh
import mathutils


class Lookup:
    def __init__(self):
        self.bones = []

    def __getitem__(self, key):
        return self.bones.index(key)

    def from_blender(self, armature):
        for bone in armature.data.bones:
            name = f'{armature.name}.{bone.name}'
            self.bones.append(name)


class Node:
    def __init__(self):
        self.index = 0
        self.name = ''
        self.parent = 0

    def from_blender(self, lookup, armature, bone):
        name = f'{armature.name}.{bone.name}'

        if bone.parent:
            parent = lookup[f'{armature.name}.{bone.parent.name}']
        else:
            parent = -1

        self.index = lookup[name]
        self.name = name
        self.parent = parent

    def to_string(self):
        return f'{self.index} "{self.name}" {self.parent}\n'


class Nodes:
    def __init__(self):
        self.nodes = []

    def from_blender(self, lookup, armature):
        for bone in armature.data.bones:
            node = Node()
            node.from_blender(lookup, armature, bone)
            self.nodes.append(node)

    def to_string(self):
        header = f'nodes\n'

        if self.nodes:
            nodes = ''.join(bone.to_string() for bone in self.nodes)
        else:
            nodes = f'0 "implicit_root" -1\n'

        footer = f'end\n'
        return f'{header}{nodes}{footer}'


class RestBone:
    def __init__(self):
        self.index = 0
        self.translation = [0, 0, 0]
        self.rotation = [0, 0, 0]

    def from_blender(self, lookup, armature, bone):
        name = f'{armature.name}.{bone.name}'

        if bone.parent:
            parent = bone.parent.matrix_local.inverted_safe()
            matrix = parent @ bone.matrix_local

        else:
            transforms = armature.matrix_world
            matrix = transforms @ bone.matrix_local

        self.index = lookup[name]
        self.translation = matrix.to_translation()[0:3]
        self.rotation = matrix.to_euler()[0:3]

    def to_string(self):
        index = f'{self.index}'
        translation = ' '.join(f'{n:.6f}' for n in self.translation)
        rotation = ' '.join(f'{n:.6f}' for n in self.rotation)
        return f'{index}  {translation}  {rotation}\n'


class RestFrame:
    def __init__(self):
        self.bones = []

    def from_blender(self, lookup, armature):
        for bone in armature.data.bones:
            rest_bone = RestBone()
            rest_bone.from_blender(lookup, armature, bone)
            self.bones.append(rest_bone)

    def to_string(self):
        time = f'time 0\n'
        bones = ''.join(bone.to_string() for bone in self.bones)
        return f'{time}{bones}'


class PoseBone:
    def __init__(self):
        self.index = 0
        self.translation = [0, 0, 0]
        self.rotation = [0, 0, 0]

    def from_blender(self, lookup, armature, bone):
        name = f'{armature.name}.{bone.name}'

        if bone.parent:
            parent = bone.parent.matrix.inverted_safe()
            matrix = parent @ bone.matrix

        else:
            transforms = armature.matrix_world
            matrix = transforms @ bone.matrix

        self.index = lookup[name]
        self.translation = matrix.to_translation()[0:3]
        self.rotation = matrix.to_euler()[0:3]

    def to_string(self):
        index = f'{self.index}'
        translation = ' '.join(f'{n:.6f}' for n in self.translation)
        rotation = ' '.join(f'{n:.6f}' for n in self.rotation)
        return f'{index}  {translation}  {rotation}\n'


class PoseFrame:
    def __init__(self):
        self.time = 0
        self.bones = []

    def from_blender(self, lookup, armature, time):
        self.time = time

        for bone in armature.pose.bones:
            pose_bone = PoseBone()
            pose_bone.from_blender(lookup, armature, bone)
            self.bones.append(pose_bone)

    def to_string(self):
        time = f'time {self.time}\n'
        bones = ''.join(bone.to_string() for bone in self.bones)
        return f'{time}{bones}'


class Skeleton:
    def __init__(self):
        self.frames = []

    def from_blender(self, lookup, armature, type):
        if type == 'REFERENCE':
            frame = RestFrame()
            frame.from_blender(lookup, armature)
            self.frames.append(frame)

        elif type == 'ANIMATION':
            start = bpy.context.scene.frame_start
            end = bpy.context.scene.frame_end + 1

            current = bpy.context.scene.frame_current

            for time in range(start, end):
                bpy.context.scene.frame_set(time)

                frame = PoseFrame()
                frame.from_blender(lookup, armature, time)
                self.frames.append(frame)

            bpy.context.scene.frame_set(current)

    def to_string(self):
        header = f'skeleton\n'

        if self.frames:
            frames = ''.join(frame.to_string() for frame in self.frames)
        else:
            zeroes = ' '.join(f'{0:.6f}' for n in range(3))
            frames = f'time 0\n0  {zeroes}  {zeroes}\n'

        footer = f'end\n'
        return f'{header}{frames}{footer}'


class Vertex:
    def __init__(self):
        self.coords = [0, 0, 0]
        self.normal = [0, 0, 0]
        self.uvs = [0, 0]
        self.bones = []

    def from_blender(self, lookup, armature, object, mesh, loop):
        vertex = mesh.vertices[loop.vertex_index]
        self.coords = vertex.co[0:3]
        self.normal = loop.normal[0:3]

        if mesh.uv_layers:
            self.uvs = mesh.uv_layers.active.data[loop.index].uv[0:2]
        else:
            self.uvs = [0.0, 0.0]

        if armature:
            for group in vertex.groups:
                bone = object.vertex_groups[group.group]
                name = f'{armature.name}.{bone.name}'
                index = lookup[name]

                if index != -1:
                    weight = group.weight
                    self.bones.append([index, weight])

    def to_string(self):
        parent = f'0'
        coords = ' '.join(f'{n:.6f}' for n in self.coords)
        normal = ' '.join(f'{n:.6f}' for n in self.normal)
        uvs = ' '.join(f'{n:.6f}' for n in self.uvs)
        count = f'{len(self.bones)}'
        bones = ' '.join(f'{i} {w:.6f}' for i, w in self.bones)

        if self.bones:
            return f'{parent}  {coords}  {normal}  {uvs}  {count}  {bones}\n'
        else:
            return f'{parent}  {coords}  {normal}  {uvs}\n'


class Triangle:
    def __init__(self):
        self.material = ''
        self.vertices = []

    def from_blender(self, lookup, armature, object, mesh, poly):
        if poly.material_index < len(object.material_slots):
            self.material = object.material_slots[poly.material_index].material
        self.material = getattr(self.material, 'name', 'no_material')

        for loop in [mesh.loops[i] for i in poly.loop_indices]:
            vertex = Vertex()
            vertex.from_blender(lookup, armature, object, mesh, loop)
            self.vertices.append(vertex)

    def to_string(self):
        material = f'{self.material}\n'
        vertices = ''.join(vertex.to_string() for vertex in self.vertices)
        return f'{material}{vertices}'


class Triangles:
    def __init__(self):
        self.triangles = []

    def from_blender(self, lookup, armature, object):
        if object.type not in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}:
            return

        for mod in getattr(object, 'modifiers', []):
            if mod.type == 'ARMATURE':
                mod.show_viewport = False

        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated = object.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()

        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()

        mesh.transform(object.matrix_world)
        mesh.calc_normals_split()

        for poly in mesh.polygons:
            triangle = Triangle()
            triangle.from_blender(lookup, armature, object, mesh, poly)
            self.triangles.append(triangle)

        mesh.free_normals_split()
        evaluated.to_mesh_clear()

        for mod in getattr(object, 'modifiers', []):
            if mod.type == 'ARMATURE':
                mod.show_viewport = True

    def to_string(self):
        header = f'triangles\n'
        triangles = ''.join(triangle.to_string() for triangle in self.triangles)
        footer = f'end\n'
        return f'{header}{triangles}{footer}'


class SMD:
    def __init__(self):
        self.lookup = Lookup()
        self.nodes = Nodes()
        self.skeleton = Skeleton()
        self.triangles = Triangles()

    def link_and_show(self, object):
        in_scene = bpy.context.scene.collection in object.users_collection
        if not in_scene:
            bpy.context.scene.collection.objects.link(object)

        hide_viewport = True if object.hide_viewport else False
        object.hide_viewport = False

        return in_scene, hide_viewport

    def unlink_and_hide(self, object, in_scene, hide_viewport):
        if not in_scene:
            bpy.context.scene.collection.objects.unlink(object)

        object.hide_viewport = hide_viewport

    def from_blender(self, armatures, objects):
        type = 'REFERENCE' if objects else 'ANIMATION'

        for armature in armatures:
            in_scene, hide_viewport = self.link_and_show(armature)

            self.lookup.from_blender(armature)
            self.nodes.from_blender(self.lookup, armature)
            self.skeleton.from_blender(self.lookup, armature, type)

            self.unlink_and_hide(armature, in_scene, hide_viewport)

        for object in objects:
            in_scene, hide_viewport = self.link_and_show(object)

            armature = object.find_armature()
            self.triangles.from_blender(self.lookup, armature, object)

            self.unlink_and_hide(object, in_scene, hide_viewport)

    def to_string(self):
        version = f'version 1\n'
        nodes = self.nodes.to_string()
        skeleton = self.skeleton.to_string()
        triangles = self.triangles.to_string()
        return f'{version}{nodes}{skeleton}{triangles}'
