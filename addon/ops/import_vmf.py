import bpy
from pathlib import Path
from .. utils import common
from .. types.pyvmf import pyvmf
from .. types import map


class SOURCEOPS_OT_ImportVMF(bpy.types.Operator):
    bl_idname = 'sourceops.import_vmf'
    bl_options = {'REGISTER'}
    bl_label = 'Import VMF'
    bl_description = 'Import maps from the Valve Map Format to blender'

    @classmethod
    def poll(cls, context):
        sourceops = common.get_globals(context)
        game = common.get_game(sourceops)
        props = common.get_vmf(sourceops)
        return sourceops and game and props

    def invoke(self, context, event):
        sourceops = common.get_globals(context)
        game = common.get_game(sourceops)
        props = common.get_vmf(sourceops)
        
        if not game.maps:
            self.report({'INFO'}, 'Please enter a maps folder')
            return {'CANCELLED'}

        if not props.name:
            self.report({'INFO'}, 'Please enter a map name')
            return {'CANCELLED'}
            
        if not props.scale:
            self.report({'INFO'}, 'Please enter a map scale')
            return {'CANCELLED'}
            
        if not props.epsilon:
            self.report({'INFO'}, 'Please enter an epsilon')
            return {'CANCELLED'}

        path = str(Path(game.maps).joinpath(props.name))
        
        iMap = map.Map(pyvmf.load_vmf(path), props.epsilon)
        map.MapToMesh(iMap, props.scale).import_meshes()
        
        
        #objects = [o for o in props.collection.all_objects if o.type == 'MESH']

        #align_to_grid = props.align_to_grid
        #brush_scale = props.brush_scale
        #geometry_scale = props.geometry_scale
        #lightmap_scale = props.lightmap_scale

        #settings = displacement.DispSettings(path, objects, align_to_grid, brush_scale, geometry_scale, lightmap_scale)
        #displacement.DispExporter(settings)

        self.report({'INFO'}, 'Imported VMF')
        return {'FINISHED'}
