import bpy
from pathlib import Path
from .. utils import common
from .. pyvmf import pyvmf
from .. types import displacement


class SOURCEOPS_OT_ExportVMF(bpy.types.Operator):
    bl_idname = 'sourceops.export_vmf'
    bl_options = {'REGISTER'}
    bl_label = 'Export VMF'
    bl_description = 'Test'

    @classmethod
    def poll(cls, context):
        return bpy.data.is_saved and context.active_object and context.active_object.type == 'MESH'

    def invoke(self, context, event):
        displacement_converter = displacement.DispConverter(context.active_object)
        displacement_group = displacement_converter.displacement_group

        #for disp in displacement_group.displacements:
        #    for row in disp:
        #        print(', '.join(str(col.points[0].alpha) for col in row))

        #for face in displacement_group.faces:
        #    print(str(face.index) + ' : ' + ', '.join(f.index for f in face.neighbors if f))

        for vertex in displacement_group.vertices:
            print(str(vertex.index) + ' : ' + ', '.join(str(p.index) for p in vertex.polygons))

        return {'FINISHED'}

#    def invoke(self, context, event):
#        path = Path(bpy.path.abspath('//vmf/test.vmf')).resolve()
#        common.verify_folder(str(path.parent))
#        path = str(path)
#
#        vertex = pyvmf.Vertex(0, 0, 0)
#        solid = pyvmf.SolidGenerator.cube(vertex, 128, 128, 128, True)
#        solid.side[1].dispinfo = pyvmf.DispInfo()
#
#        vmf = pyvmf.new_vmf()
#        vmf.add_solids(solid)
#        vmf.export(path)
#
#        self.report({'INFO'}, 'Exported VMF')
#        return {'FINISHED'}
