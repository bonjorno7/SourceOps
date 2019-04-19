# <definition>
bl_info = {
    "blender" : (2, 80, 0),
    "name" : "BASE",
    "description" : "Blender Add-on for Source Engine, a more convenient but less powerful alternative to Blender Source Tools",
    "author" : "bonjorno7",
    "version" : (0, 3, 6),
    "location" : "3D View > Sidebar",
    "category" : "Import-Export",
    "warning" : "",
}
# </definition>

# <import>
import os, subprocess, math
import bpy, bmesh, mathutils

# SETTINGS
from . settings . settings import BASE_PG_SettingsProps
from . settings . game import BASE_PG_GameProps, BASE_UL_GameList, BASE_OT_AddGame, BASE_OT_RemoveGame, BASE_OT_MoveGame
from . settings . panels import BASE_PT_SettingsPanel, BASE_PT_OptionsPanel, BASE_PT_GamesPanel

# EXPORT
from . model_export . model import BASE_PG_ModelProps, BASE_UL_ModelList, BASE_OT_AddModel, BASE_OT_RemoveModel, BASE_OT_MoveModel
from . model_export . mesh import BASE_PG_MeshProps, BASE_UL_MeshList, BASE_OT_AddMesh, BASE_OT_RemoveMesh, BASE_OT_MoveMesh
from . model_export . export_model import BASE_OT_ExportModel
from . model_export . view_model import BASE_OT_ViewModel
from . model_export . panels import BASE_PT_ModelExportPanel, BASE_PT_ModelPanel, BASE_PT_MeshPanel, BASE_PT_PropertiesPanel
from . material_import_export .material_import import BASE_OT_ImportMaterial,BASE_PT_MaterialImportPanel

# SURF TOOLS
from . surf_tools . surf_collision import BASE_PG_CollisionProps, BASE_OT_SurfCollision
from . surf_tools . curved_ramp import BASE_PG_SurfRampProps, BASE_OT_SurfRampify
from . surf_tools . panels import BASE_PT_SurfToolsPanel, BASE_PT_CollisionPanel, BASE_PT_CurvedRampPanel
# </import>


# <props>
class BASE_PG_Props(bpy.types.PropertyGroup):
    """Global variables for this add-on"""
    settings: bpy.props.PointerProperty(type = BASE_PG_SettingsProps)

    models: bpy.props.CollectionProperty(type = BASE_PG_ModelProps)
    model_index: bpy.props.IntProperty(default = 0)

    collision: bpy.props.PointerProperty(type = BASE_PG_CollisionProps)
    surf_ramp: bpy.props.PointerProperty(type = BASE_PG_SurfRampProps)
# </props>


# <variables>
classes = (
    BASE_PG_GameProps, BASE_PG_SettingsProps,
    BASE_UL_GameList, BASE_OT_AddGame, BASE_OT_RemoveGame, BASE_OT_MoveGame,
    BASE_PT_SettingsPanel, BASE_PT_OptionsPanel, BASE_PT_GamesPanel,

    BASE_PG_MeshProps, BASE_PG_ModelProps,
    BASE_UL_ModelList, BASE_UL_MeshList,
    BASE_OT_AddModel, BASE_OT_RemoveModel, BASE_OT_MoveModel,
    BASE_OT_AddMesh, BASE_OT_RemoveMesh, BASE_OT_MoveMesh,
    BASE_OT_ExportModel, BASE_OT_ViewModel,
    BASE_PT_ModelExportPanel, BASE_PT_ModelPanel, BASE_PT_MeshPanel, BASE_PT_PropertiesPanel,

    BASE_PG_CollisionProps, BASE_PG_SurfRampProps,
    BASE_OT_SurfCollision, BASE_OT_SurfRampify,
    BASE_PT_SurfToolsPanel, BASE_PT_CollisionPanel, BASE_PT_CurvedRampPanel,

    BASE_OT_ImportMaterial,BASE_PT_MaterialImportPanel,

    BASE_PG_Props,
)

register_classes, unregister_classes = bpy.utils.register_classes_factory(classes)
# </variables>


# <functions>
def register():
    register_classes()
    bpy.types.Scene.BASE = bpy.props.PointerProperty(type = BASE_PG_Props)


def unregister():
    from . utils.vtf_wrapper.VTFLib import VTFLib
    del VTFLib.vtflib_cdll
    unregister_classes()
    del bpy.types.Scene.BASE


if __name__ == "__main__":
    register()
# </functions>
