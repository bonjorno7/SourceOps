import bpy
from pathlib import Path
from .. utils import common
from .. pyvmf import pyvmf
from .. types import displacement


class SOURCEOPS_OT_ExportDisplacements(bpy.types.Operator):
    bl_idname = 'sourceops.export_displacements'
    bl_options = {'REGISTER'}
    bl_label = 'Export Displacements'
    bl_description = 'Turn meshes into displacements and export them to a VMF file'

    @classmethod
    def poll(cls, context):
        sourceops = common.get_globals(context)
        game = common.get_game(sourceops)
        displacement_props = common.get_displacement_props(sourceops)
        return sourceops and game and displacement_props

    def invoke(self, context, event):
        sourceops = common.get_globals(context)
        game = common.get_game(sourceops)
        displacement_props = common.get_displacement_props(sourceops)

        if not game.maps:
            self.report({'INFO'}, 'Please enter a maps folder')
            return {'CANCELLED'}

        if not displacement_props.name:
            self.report({'INFO'}, 'Please enter a map name')
            return {'CANCELLED'}

        if not displacement_props.collection:
            self.report({'INFO'}, 'Please choose a collection')
            return {'CANCELLED'}

        path = str(Path(game.maps).joinpath(displacement_props.name))
        objects = [o for o in displacement_props.collection.all_objects if o.type == 'MESH']

        brush_scale = displacement_props.brush_scale
        geometry_scale = displacement_props.geometry_scale
        lightmap_scale = displacement_props.lightmap_scale

        settings = displacement.DispSettings(path, objects, brush_scale, geometry_scale, lightmap_scale)
        displacement.DispExporter(settings)

        self.report({'INFO'}, 'Exported VMF')
        return {'FINISHED'}
