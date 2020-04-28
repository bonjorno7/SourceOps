import bpy
from . export_meshes import SOURCEOPS_OT_ExportMeshes
from . generate_qc import SOURCEOPS_OT_GenerateQC
from . open_qc import SOURCEOPS_OT_OpenQC
from . compile_qc import SOURCEOPS_OT_CompileQC
from . view_model import SOURCEOPS_OT_ViewModel
from . open_log import SOURCEOPS_OT_OpenLog
from . list_operator import SOURCEOPS_OT_ListOperator
from . export_vmf import SOURCEOPS_OT_ExportVMF
from . rig_simulation import SOURCEOPS_OT_RigSimulation


def register():
    bpy.utils.register_class(SOURCEOPS_OT_ExportMeshes)
    bpy.utils.register_class(SOURCEOPS_OT_GenerateQC)
    bpy.utils.register_class(SOURCEOPS_OT_OpenQC)
    bpy.utils.register_class(SOURCEOPS_OT_CompileQC)
    bpy.utils.register_class(SOURCEOPS_OT_ViewModel)
    bpy.utils.register_class(SOURCEOPS_OT_OpenLog)
    bpy.utils.register_class(SOURCEOPS_OT_ListOperator)
    bpy.utils.register_class(SOURCEOPS_OT_ExportVMF)
    bpy.utils.register_class(SOURCEOPS_OT_RigSimulation)


def unregister():
    bpy.utils.unregister_class(SOURCEOPS_OT_RigSimulation)
    bpy.utils.unregister_class(SOURCEOPS_OT_ExportVMF)
    bpy.utils.unregister_class(SOURCEOPS_OT_ListOperator)
    bpy.utils.unregister_class(SOURCEOPS_OT_OpenLog)
    bpy.utils.unregister_class(SOURCEOPS_OT_ViewModel)
    bpy.utils.unregister_class(SOURCEOPS_OT_CompileQC)
    bpy.utils.unregister_class(SOURCEOPS_OT_OpenQC)
    bpy.utils.unregister_class(SOURCEOPS_OT_GenerateQC)
    bpy.utils.unregister_class(SOURCEOPS_OT_ExportMeshes)
