import bpy
from pathlib import Path
from .. import utils
from .. types . map_export . vmf import VMF, Settings


class SOURCEOPS_OT_ExportVMF(bpy.types.Operator):
    bl_idname = 'sourceops.export_vmf'
    bl_options = {'REGISTER'}
    bl_label = 'Export VMF'
    bl_description = 'Turn meshes into brushes or displacements and export them to a VMF file'

    @classmethod
    def poll(cls, context):
        prefs = utils.common.get_prefs(context)
        game = utils.common.get_game(prefs)
        sourceops = utils.common.get_globals(context)
        props = utils.common.get_map(sourceops)
        return prefs and game and sourceops and props

    def invoke(self, context, event):
        prefs = utils.common.get_prefs(context)
        game = utils.common.get_game(prefs)
        sourceops = utils.common.get_globals(context)
        props = utils.common.get_map(sourceops)

        if not game.mapsrc:
            self.report({'INFO'}, 'Please enter a mapsrc folder')
            return {'CANCELLED'}

        if not props.name:
            self.report({'INFO'}, 'Please enter a map name')
            return {'CANCELLED'}

        if not (props.brush_collection or props.disp_collection):
            self.report({'INFO'}, 'Please choose a collection')
            return {'CANCELLED'}

        mapsrc = bpy.path.abspath(game.mapsrc)
        path = str(Path(mapsrc) / props.name)

        if props.brush_collection:
            brush_objects = [o for o in props.brush_collection.all_objects if o.type == 'MESH']
        else:
            brush_objects = []

        if props.disp_collection:
            disp_objects = [o for o in props.disp_collection.all_objects if o.type == 'MESH']
        else:
            disp_objects = []

        geometry_scale = props.geometry_scale
        texture_scale = props.texture_scale
        lightmap_scale = props.lightmap_scale
        allow_skewed_textures = props.allow_skewed_textures
        align_to_grid = props.align_to_grid

        settings = Settings(
            brush_objects, disp_objects,
            geometry_scale, texture_scale, lightmap_scale,
            allow_skewed_textures, align_to_grid
        )
        vmf = VMF(settings)
        vmf.export(path)

        self.report({'INFO'}, 'Exported VMF')
        return {'FINISHED'}
