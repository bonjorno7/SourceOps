import bpy
from . export_meshes import SOURCEOPS_OT_ExportMeshes
from . generate_qc import SOURCEOPS_OT_GenerateQC
from . open_qc import SOURCEOPS_OT_OpenQC
from . compile_qc import SOURCEOPS_OT_CompileQC
from . view_model import SOURCEOPS_OT_ViewModel
from . open_log import SOURCEOPS_OT_OpenLog
from . add_item import SOURCEOPS_OT_AddItem
from . remove_item import SOURCEOPS_OT_RemoveItem
from . copy_item import SOURCEOPS_OT_CopyItem
from . move_item import SOURCEOPS_OT_MoveItem
from . export_displacements import SOURCEOPS_OT_ExportDisplacements


def register():
    bpy.utils.register_class(SOURCEOPS_OT_ExportMeshes)
    bpy.utils.register_class(SOURCEOPS_OT_GenerateQC)
    bpy.utils.register_class(SOURCEOPS_OT_OpenQC)
    bpy.utils.register_class(SOURCEOPS_OT_CompileQC)
    bpy.utils.register_class(SOURCEOPS_OT_ViewModel)
    bpy.utils.register_class(SOURCEOPS_OT_OpenLog)
    bpy.utils.register_class(SOURCEOPS_OT_AddItem)
    bpy.utils.register_class(SOURCEOPS_OT_RemoveItem)
    bpy.utils.register_class(SOURCEOPS_OT_CopyItem)
    bpy.utils.register_class(SOURCEOPS_OT_MoveItem)
    bpy.utils.register_class(SOURCEOPS_OT_ExportDisplacements)


def unregister():
    bpy.utils.unregister_class(SOURCEOPS_OT_ExportDisplacements)
    bpy.utils.unregister_class(SOURCEOPS_OT_MoveItem)
    bpy.utils.unregister_class(SOURCEOPS_OT_RemoveItem)
    bpy.utils.unregister_class(SOURCEOPS_OT_CopyItem)
    bpy.utils.unregister_class(SOURCEOPS_OT_AddItem)
    bpy.utils.unregister_class(SOURCEOPS_OT_OpenLog)
    bpy.utils.unregister_class(SOURCEOPS_OT_ViewModel)
    bpy.utils.unregister_class(SOURCEOPS_OT_CompileQC)
    bpy.utils.unregister_class(SOURCEOPS_OT_OpenQC)
    bpy.utils.unregister_class(SOURCEOPS_OT_GenerateQC)
    bpy.utils.unregister_class(SOURCEOPS_OT_ExportMeshes)
