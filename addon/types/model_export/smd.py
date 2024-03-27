import bpy
from typing import List


class Settings:
    def __init__(self, prepend_armature: bool, ignore_transforms: bool):
        self.prepend_armature = prepend_armature
        self.ignore_transforms = ignore_transforms


class Lookup:
    def __init__(self, settings: Settings):
        self.settings = settings

        if self.settings.prepend_armature:
            name = 'Source.Implicit'
        else:
            name = 'Implicit'

        self.bones = [name]

    def __getitem__(self, key: str) -> int:
        if key in self.bones:
            return self.bones.index(key)
        else:
            return -1

    def from_blender(self, armature: bpy.types.Object):
        if armature:
            for bone in armature.data.bones:
                bone: bpy.types.Bone

                if self.settings.prepend_armature:
                    name = f'{armature.name}.{bone.name}'
                else:
                    name = bone.name

                self.bones.append(name)


class Node:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.index = 0

        if self.settings.prepend_armature:
            name = 'Source.Implicit'
        else:
            name = 'Implicit'

        self.name = name
        self.parent = -1

    def from_blender(self, lookup: Lookup, armature: bpy.types.Object, bone: bpy.types.Bone):
        if self.settings.prepend_armature:
            name = f'{armature.name}.{bone.name}'
        else:
            name = bone.name

        if bone.parent:
            if self.settings.prepend_armature:
                parent = lookup[f'{armature.name}.{bone.parent.name}']
            else:
                parent = lookup[bone.parent.name]
        else:
            parent = -1

        self.index = lookup[name]
        self.name = name
        self.parent = parent

    def to_string(self) -> str:
        return f'{self.index} "{self.name}" {self.parent}\n'


class Nodes:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.nodes = [Node(self.settings)]

    def from_blender(self, lookup: Lookup, armature: bpy.types.Object):
        if armature:
            for bone in armature.data.bones:
                bone: bpy.types.Bone

                node = Node(self.settings)
                node.from_blender(lookup, armature, bone)
                self.nodes.append(node)

    def to_string(self) -> str:
        header = f'nodes\n'
        nodes = ''.join(bone.to_string() for bone in self.nodes)
        footer = f'end\n'
        return f'{header}{nodes}{footer}'


class RestBone:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.index = 0
        self.translation = [0, 0, 0]
        self.rotation = [0, 0, 0]

    def from_blender(self, lookup: Lookup, armature: bpy.types.Object, bone: bpy.types.Bone):
        if self.settings.prepend_armature:
            name = f'{armature.name}.{bone.name}'
        else:
            name = bone.name

        if bone.parent:
            parent = bone.parent.matrix_local.inverted_safe()
            matrix = parent @ bone.matrix_local

        elif not self.settings.ignore_transforms:
            transforms = armature.matrix_world
            matrix = transforms @ bone.matrix_local

        else:
            matrix = bone.matrix_local

        self.index = lookup[name]
        self.translation = matrix.to_translation()[0:3]
        self.rotation = matrix.to_euler()[0:3]

    def to_string(self) -> str:
        index = f'{self.index}'
        translation = ' '.join(f'{n:.6f}' for n in self.translation)
        rotation = ' '.join(f'{n:.6f}' for n in self.rotation)
        return f'{index}  {translation}  {rotation}\n'


class RestFrame:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.bones = [RestBone(self.settings)]

    def from_blender(self, lookup: Lookup, armature: bpy.types.Object):
        for bone in armature.data.bones:
            bone: bpy.types.Bone

            rest_bone = RestBone(self.settings)
            rest_bone.from_blender(lookup, armature, bone)
            self.bones.append(rest_bone)

    def to_string(self) -> str:
        time = f'time 0\n'
        bones = ''.join(bone.to_string() for bone in self.bones)
        return f'{time}{bones}'


class PoseBone:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.index = 0
        self.translation = [0, 0, 0]
        self.rotation = [0, 0, 0]

    def from_blender(self, lookup: Lookup, armature: bpy.types.Object, bone: bpy.types.PoseBone):
        if self.settings.prepend_armature:
            name = f'{armature.name}.{bone.name}'
        else:
            name = bone.name

        if bone.parent:
            parent = bone.parent.matrix.inverted_safe()
            matrix = parent @ bone.matrix

        elif not self.settings.ignore_transforms:
            transforms = armature.matrix_world
            matrix = transforms @ bone.matrix

        else:
            matrix = bone.matrix

        self.index = lookup[name]
        self.translation = matrix.to_translation()[0:3]
        self.rotation = matrix.to_euler()[0:3]

    def to_string(self) -> str:
        index = f'{self.index}'
        translation = ' '.join(f'{n:.6f}' for n in self.translation)
        rotation = ' '.join(f'{n:.6f}' for n in self.rotation)
        return f'{index}  {translation}  {rotation}\n'


class PoseFrame:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.time = 0
        self.bones = [PoseBone(self.settings)]

    def from_blender(self, lookup: Lookup, armature: bpy.types.Object, time: int):
        self.time = time

        for bone in armature.pose.bones:
            bone: bpy.types.PoseBone

            pose_bone = PoseBone(self.settings)
            pose_bone.from_blender(lookup, armature, bone)
            self.bones.append(pose_bone)

    def to_string(self) -> str:
        time = f'time {self.time}\n'
        bones = ''.join(bone.to_string() for bone in self.bones)
        return f'{time}{bones}'


class Skeleton:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.frames = []

    def from_blender(self, lookup: Lookup, armature: bpy.types.Object, action: bpy.types.Action):
        if not armature:
            frame = RestFrame(self.settings)
            self.frames.append(frame)

        elif not action:
            frame = RestFrame(self.settings)
            frame.from_blender(lookup, armature)
            self.frames.append(frame)

        else:
            if not armature.animation_data:
                new_animation_data = armature.animation_data_create()
            else:
                new_animation_data = None

            original_action = armature.animation_data.action
            armature.animation_data.action = action

            if not original_action:
                pose_backup = {}

                for pose_bone in armature.pose.bones:
                    pose_bone: bpy.types.PoseBone
                    pose_backup[pose_bone] = pose_bone.matrix.copy()

            original_frame = bpy.context.scene.frame_current

            start = int(action.frame_range[0])
            end = int(action.frame_range[1])

            for time in range(start, end + 1):
                bpy.context.scene.frame_set(time)

                frame = PoseFrame(self.settings)
                frame.from_blender(lookup, armature, time)
                self.frames.append(frame)

            bpy.context.scene.frame_set(original_frame)

            if not original_action:
                for pose_bone, matrix in pose_backup.items():
                    pose_bone.matrix = matrix

            if new_animation_data:
                armature.animation_data_clear()
            else:
                armature.animation_data.action = original_action

    def to_string(self) -> str:
        header = f'skeleton\n'
        frames = ''.join(frame.to_string() for frame in self.frames)
        footer = f'end\n'
        return f'{header}{frames}{footer}'


class Vertex:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.coords = [0, 0, 0]
        self.normal = [0, 0, 0]
        self.uvs = [0, 0]
        self.bones = []

    def from_blender(self, lookup: Lookup, armature: bpy.types.Object, object: bpy.types.Object, mesh: bpy.types.Mesh, loop: bpy.types.MeshLoop):
        vertex = mesh.vertices[loop.vertex_index]
        self.coords = vertex.co[0:3]
        self.normal = loop.normal[0:3]

        if mesh.uv_layers:
            self.uvs = mesh.uv_layers.active.data[loop.index].uv[0:2]
        else:
            self.uvs = [0.0, 0.0]

        if armature:
            for group in vertex.groups:
                group: bpy.types.VertexGroupElement

                bone = object.vertex_groups[group.group]

                if self.settings.prepend_armature:
                    name = f'{armature.name}.{bone.name}'
                else:
                    name = bone.name

                index = lookup[name]

                if index != -1:
                    weight = group.weight
                    self.bones.append([index, weight])

    def to_string(self) -> str:
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
    def __init__(self, settings: Settings):
        self.settings = settings
        self.material = ''
        self.vertices = []

    def from_blender(self, lookup: Lookup, armature: bpy.types.Object, object: bpy.types.Object, mesh: bpy.types.Mesh, poly: bpy.types.MeshPolygon):
        if poly.material_index < len(mesh.materials):
            self.material = mesh.materials[poly.material_index]
        self.material = getattr(self.material, 'name', 'no_material')

        for loop in [mesh.loops[i] for i in poly.loop_indices]:
            vertex = Vertex(self.settings)
            vertex.from_blender(lookup, armature, object, mesh, loop)
            self.vertices.append(vertex)

    def to_string(self) -> str:
        material = f'{self.material}\n'
        vertices = ''.join(vertex.to_string() for vertex in self.vertices)
        return f'{material}{vertices}'


class Triangles:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.triangles = []

    def from_blender(self, lookup: Lookup, armature: bpy.types.Object, object: bpy.types.Object):
        if object.type not in {'MESH', 'CURVE', 'SURFACE', 'FONT'}:
            return

        collection = bpy.data.collections.new('SourceOps')
        bpy.context.scene.collection.children.link(collection)
        object = object.copy()
        collection.objects.link(object)

        mod: bpy.types.TriangulateModifier = object.modifiers.new('Triangulate', 'TRIANGULATE')
        mod.min_vertices = 4
        mod.quad_method = 'FIXED'
        mod.ngon_method = 'CLIP'
        mod.keep_custom_normals = True

        for mod in getattr(object, 'modifiers', []):
            if mod.type == 'ARMATURE':
                mod.show_viewport = False

        bpy.context.view_layer.update()
        depsgraph: bpy.types.Depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated: bpy.types.Object = object.evaluated_get(depsgraph)
        mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)

        if not self.settings.ignore_transforms:
            mesh.transform(object.matrix_world)

        if hasattr(mesh, 'calc_normals_split'):
            mesh.calc_normals_split()

        for poly in mesh.polygons:
            triangle = Triangle(self.settings)
            triangle.from_blender(lookup, armature, object, mesh, poly)
            self.triangles.append(triangle)

        if hasattr(mesh, 'free_normals_split'):
            mesh.free_normals_split()

        bpy.data.meshes.remove(mesh)
        bpy.data.objects.remove(object)
        bpy.data.collections.remove(collection)

    def to_string(self) -> str:
        header = f'triangles\n'
        triangles = ''.join(triangle.to_string() for triangle in self.triangles)
        footer = f'end\n'
        return f'{header}{triangles}{footer}'


class SMD:
    def __init__(self, prepend_armature: bool, ignore_transforms: bool):
        self.settings = Settings(prepend_armature, ignore_transforms)
        self.lookup = Lookup(self.settings)
        self.nodes = Nodes(self.settings)
        self.skeleton = Skeleton(self.settings)
        self.triangles = Triangles(self.settings)

    def configure_scene(self, objects: List[bpy.types.Object]) -> dict:
        scene_settings = {'mode': 'OBJECT', 'objects': {o: {} for o in objects}}

        if bpy.context.active_object:
            scene_settings['mode'] = bpy.context.active_object.mode
            bpy.ops.object.mode_set(mode='OBJECT')

        for object in objects:
            scene_settings['objects'][object]['hide_viewport'] = True if object.hide_viewport else False
            object.hide_viewport = False

        return scene_settings

    def restore_scene(self, scene_settings: dict):
        for object in scene_settings['objects'].keys():
            object.hide_viewport = scene_settings['objects'][object]['hide_viewport']

        if scene_settings['mode'] != 'OBJECT':
            bpy.ops.object.mode_set(mode=scene_settings['mode'])

    def from_blender(self, armature: bpy.types.Object, objects: List[bpy.types.Object], action: bpy.types.Action):
        if armature:
            all_objects = set([armature] + objects)
        else:
            all_objects = set(objects)

        scene_settings = self.configure_scene(all_objects)

        self.lookup.from_blender(armature)
        self.nodes.from_blender(self.lookup, armature)
        self.skeleton.from_blender(self.lookup, armature, action)

        for object in objects:
            self.triangles.from_blender(self.lookup, armature, object)

        self.restore_scene(scene_settings)

    def to_string(self) -> str:
        version = f'version 1\n'
        nodes = self.nodes.to_string()
        skeleton = self.skeleton.to_string()
        triangles = self.triangles.to_string()
        return f'{version}{nodes}{skeleton}{triangles}'
