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
        displacement_props = common.get_displacement_props(sourceops)
        return sourceops and displacement_props

    def invoke(self, context, event):
        sourceops = common.get_globals(context)
        displacement_props = common.get_displacement_props(sourceops)

        if not displacement_props.map_path:
            self.report({'INFO'}, 'Please enter a file path')
            return {'CANCELLED'}

        if not displacement_props.collection:
            self.report({'INFO'}, 'Please choose a collection')
            return {'CANCELLED'}

        objects = [o for o in displacement_props.collection.all_objects if o.type == 'MESH']
        displacement.DispExporter(displacement_props, objects)

        self.report({'INFO'}, 'Exported VMF')
        return {'FINISHED'}
