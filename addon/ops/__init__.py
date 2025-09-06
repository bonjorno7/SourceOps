import bpy
from . import open_folder
from . import export_meshes
from . import generate_qc
from . import compile_qc
from . import view_model
from . import export_auto
from . import list_operator
from . import export_vmf
from . import rig_simulation
from . import pose_bone_transforms
from . import weighted_normal
from . import triangulate
from . import backup

classes = (
    open_folder.SOURCEOPS_OT_OpenFolder,
    export_meshes.SOURCEOPS_OT_ExportMeshes,
    generate_qc.SOURCEOPS_OT_GenerateQC,
    compile_qc.SOURCEOPS_OT_CompileQC,
    view_model.SOURCEOPS_OT_ViewModel,
    export_auto.SOURCEOPS_OT_ExportAuto,
    list_operator.SOURCEOPS_OT_ListOperator,
    export_vmf.SOURCEOPS_OT_ExportVMF,
    rig_simulation.SOURCEOPS_OT_RigSimulation,
    pose_bone_transforms.SOURCEOPS_OT_PoseBoneTransforms,
    weighted_normal.SOURCEOPS_OT_weighted_normal,
    triangulate.SOURCEOPS_OT_triangulate,
    backup.SOURCEOPS_OT_BackupPreferences,
    backup.SOURCEOPS_OT_RestorePreferences,
)

class_register, class_unregister = bpy.utils.register_classes_factory(classes)

def register():
    class_register()

    bpy.types.VIEW3D_MT_pose_context_menu.append(pose_bone_transforms.menu_func)

def unregister():
    bpy.types.VIEW3D_MT_pose_context_menu.remove(pose_bone_transforms.menu_func)

    class_unregister()
