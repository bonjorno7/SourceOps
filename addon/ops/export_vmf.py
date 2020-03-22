import bpy
from pathlib import Path
from .. utils import common
from .. pyvmf import pyvmf


class SOURCEOPS_OT_ExportVMF(bpy.types.Operator):
    bl_idname = 'sourceops.export_vmf'
    bl_options = {'REGISTER'}
    bl_label = 'Export VMF'
    bl_description = 'Test'

    @classmethod
    def poll(cls, context):
        return bpy.data.is_saved()

    def invoke(self, context, event):
        path = Path(bpy.path.abspath('//vmf/test.vmf')).resolve()
        common.verify_folder(str(path.parent))
        path = str(path)

        vertex = pyvmf.Vertex(0, 0, 0)
        solid = pyvmf.SolidGenerator.cube(vertex, 256, 256, 256, True)

        vmf = pyvmf.new_vmf()
        vmf.add_solids(solid)
        vmf.export(path)

        self.report({'INFO'}, 'Exported VMF')
        return {'FINISHED'}
