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

#    def invoke(self, context, event):
#        path = Path(bpy.path.abspath('//vmf/test.vmf')).resolve()
#        common.verify_folder(str(path.parent))
#        path = str(path)
#
#        v1 = pyvmf.Vertex(0, 0, 0)
#        v2 = pyvmf.Vertex(0, 96, 0)
#        v3 = pyvmf.Vertex(64, 128, 0)
#        v4 = pyvmf.Vertex(96, 0, 0)
#
#        v5 = pyvmf.Vertex(v1.x, v1.y, v1.z - 8)
#        v6 = pyvmf.Vertex(v2.x, v2.y, v2.z - 8)
#        v7 = pyvmf.Vertex(v3.x, v3.y, v3.z - 8)
#        v8 = pyvmf.Vertex(v4.x, v4.y, v4.z - 8)
#
#        f1 = pyvmf.Side(dic={'plane': f'({v1.x} {v1.y} {v1.z}) ({v2.x} {v2.y} {v2.z}) ({v3.x} {v3.y} {v3.z})'}) # top
#        f2 = pyvmf.Side(dic={'plane': f'({v7.x} {v7.y} {v7.z}) ({v6.x} {v6.y} {v6.z}) ({v5.x} {v5.y} {v5.z})'}) # bottom
#        f3 = pyvmf.Side(dic={'plane': f'({v4.x} {v4.y} {v4.z}) ({v3.x} {v3.y} {v3.z}) ({v7.x} {v7.y} {v7.z})'}) # front
#        f4 = pyvmf.Side(dic={'plane': f'({v6.x} {v6.y} {v6.z}) ({v2.x} {v2.y} {v2.z}) ({v1.x} {v1.y} {v1.z})'}) # back
#        f5 = pyvmf.Side(dic={'plane': f'({v3.x} {v3.y} {v3.z}) ({v2.x} {v2.y} {v2.z}) ({v6.x} {v6.y} {v6.z})'}) # right
#        f6 = pyvmf.Side(dic={'plane': f'({v1.x} {v1.y} {v1.z}) ({v4.x} {v4.y} {v4.z}) ({v8.x} {v8.y} {v8.z})'}) # left
#
#        solid = pyvmf.Solid()
#        solid.add_sides(f1, f2, f3, f4, f5, f6)
#        solid.editor = pyvmf.Editor()
#
#        vmf = pyvmf.new_vmf()
#        vmf.add_solids(solid)
#        vmf.export(path)
#
#        self.report({'INFO'}, 'Exported VMF')
#        return {'FINISHED'}

    def invoke(self, context, event):
        displacement_converter = displacement.DispConverter(context.active_object)
        ##displacement_group = displacement_converter.displacement_group

        #print('-----')
        #for disp in displacement_group.displacements:
        #    for row in disp:
        #        print(', '.join(str(len([p for p in col.neighbors if p])) for col in row))
        #    print('-----')

        ##print('----------')
        ##for disp in displacement_group.displacements:
        ##    for row in disp.grid:
        ##        print(' '.join('@' if loop.alpha < 0.5 else '*' for loop in row))
        ##    print('----------')

        #for face in displacement_group.faces:
        #    print(str(face.index) + ' : ' + ', '.join(f.index for f in face.neighbors if f))

        #for vertex in displacement_group.vertices:
        #    print(str(vertex.index) + ' : ' + ', '.join(str(p.index) for p in vertex.polygons))
        #    print(str(vertex.index) + ' : ' + ', '.join(str(v.index) for v in vertex.connected))
        #    print(str(vertex.index) + ' : ' + str(vertex.boundary) + ' ' + str(vertex.corner))

        #for polygon in displacement_group.polygons:
        #    print(str(polygon.index) + ' : ' + ', '.join(str(p.index) if p else 'x' for p in polygon.neighbors))

        self.report({'INFO'}, 'Exported VMF')
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
