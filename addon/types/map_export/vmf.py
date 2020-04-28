import bpy
import bmesh
import mathutils
import pathlib
from .. pyvmf import pyvmf
from . import brush
from . import disp


class Settings:
    def __init__(self, brush_objects, disp_objects, uv_scale, geometry_scale, texture_scale, lightmap_scale, align_to_grid):
        self.brush_objects = brush_objects
        self.disp_objects = disp_objects
        self.uv_scale = uv_scale
        self.geometry_scale = geometry_scale
        self.texture_scale = texture_scale
        self.lightmap_scale = lightmap_scale
        self.align_to_grid = align_to_grid


class VMF:
    def __init__(self, settings: Settings):
        scene_settings = self.configure_scene(settings.brush_objects + settings.disp_objects)
        brush_objects, brush_meshes = self.evaluated_get(settings.brush_objects)
        disp_objects, disp_meshes = self.evaluated_get(settings.disp_objects)

        brush_converter = brush.Converter(settings, brush_meshes)
        disp_converter = disp.Converter(settings, disp_meshes)
        self.solids = brush_converter.solids + disp_converter.solids

        self.to_mesh_clear(brush_objects + disp_objects)
        self.restore_scene(scene_settings)


    def export(self, path):
        path = pathlib.Path(path).resolve()
        path = path.with_suffix('.vmf')
        path.parent.mkdir(parents=True, exist_ok=True)

        vmf = pyvmf.new_vmf()
        vmf.add_solids(*self.solids)
        vmf.export(str(path))


    def configure_scene(self, objects):
        scene_settings = {o: {} for o in objects}
        scene_settings['objects'] = objects

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


    def restore_scene(self, scene_settings):
        for object in scene_settings['objects']:
            if not scene_settings[object]['in_scene']:
                bpy.context.scene.collection.objects.unlink(object)

            object.hide_viewport = scene_settings[object]['hide_viewport']

        if scene_settings['mode'] != 'OBJECT':
            bpy.ops.object.mode_set(mode=scene_settings['mode'])


    def evaluated_get(self, objects):
        evaluated_objects = []
        evaluated_meshes = []

        for object in objects:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            evaluated_object = object.evaluated_get(depsgraph)
            evaluated_objects.append(evaluated_object)

            evaluated_mesh = evaluated_object.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
            evaluated_mesh.transform(object.matrix_world)
            evaluated_meshes.append(evaluated_mesh)

        return evaluated_objects, evaluated_meshes


    def to_mesh_clear(self, evaluated_objects):
        for object in evaluated_objects:
            object.to_mesh_clear()
