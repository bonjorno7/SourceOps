import bpy
from pathlib import Path
from .. utils import common
from ..types.map_export.vmf import VMF, Settings


class SOURCEOPS_OT_ExportVMF(bpy.types.Operator):
    bl_idname = 'sourceops.export_vmf'
    bl_options = {'REGISTER'}
    bl_label = 'Export VMF'
    bl_description = 'Turn meshes into brushes or displacements and export them to a VMF file'

    @classmethod
    def poll(cls, context):
        sourceops = common.get_globals(context)
        game = common.get_game(sourceops)
        props = common.get_map(sourceops)
        return sourceops and game and props

    def invoke(self, context, event):
        sourceops = common.get_globals(context)
        game = common.get_game(sourceops)
        props = common.get_map(sourceops)

        if not game.maps:
            self.report({'INFO'}, 'Please enter a maps folder')
            return {'CANCELLED'}

        if not props.name:
            self.report({'INFO'}, 'Please enter a map name')
            return {'CANCELLED'}

        if not (props.brush_collection or props.disp_collection):
            self.report({'INFO'}, 'Please choose a collection')
            return {'CANCELLED'}

        path = str(Path(game.maps).joinpath(props.name))

        if props.brush_collection:
            brush_objects = [o for o in props.brush_collection.all_objects if o.type == 'MESH']
        else:
            brush_objects = []

        if props.disp_collection:
            disp_objects = [o for o in props.disp_collection.all_objects if o.type == 'MESH']
        else:
            disp_objects = []

        uv_scale = props.uv_scale
        geometry_scale = props.geometry_scale
        texture_scale = props.texture_scale
        lightmap_scale = props.lightmap_scale
        align_to_grid = props.align_to_grid

        settings = Settings(brush_objects, disp_objects, uv_scale, geometry_scale, texture_scale, lightmap_scale, align_to_grid)
        vmf = VMF(settings)
        vmf.export(path)

        self.report({'INFO'}, 'Exported VMF')
        return {'FINISHED'}
