import bpy

from . settings . settings import SettingsProps
from . settings . game import GameProps, GameList, AddGame, RemoveGame, MoveGame
from . settings . panels import SettingsPanel, OptionsPanel, GamesPanel

from . model_export . model import ModelProps, ModelList, AddModel, RemoveModel, MoveModel
from . model_export . mesh import MeshProps, MeshList, AddMesh, RemoveMesh, MoveMesh
from . model_export . export_model import ExportModel
from . model_export . view_model import ViewModel
from . model_export . panels import ModelExportPanel, ModelPanel, MeshPanel, PropertiesPanel

# from . material_import_export . material_import import ImportMaterial, MaterialImportPanel

from . surf_tools . surf_collision import CollisionProps, SurfCollision
from . surf_tools . curved_ramp import SurfRampProps, SurfRampify
from . surf_tools . panels import SurfToolsPanel, CollisionPanel, CurvedRampPanel


bl_info = {
    "blender": (2, 80, 0),
    "name": "BASE",
    "description": "Blender Add-on for Source Engine",
    "author": "bonjorno7 & REDxEYE",
    "version": (0, 3, 8),
    "location": "3D View > Sidebar",
    "category": "Import-Export",
    "warning": "",
}


class Props(bpy.types.PropertyGroup):
    """Global variables for this add-on"""
    settings: bpy.props.PointerProperty(type=SettingsProps)

    models: bpy.props.CollectionProperty(type=ModelProps)
    model_index: bpy.props.IntProperty(default=0)

    collision: bpy.props.PointerProperty(type=CollisionProps)
    surf_ramp: bpy.props.PointerProperty(type=SurfRampProps)


classes = (
    GameProps, SettingsProps,
    GameList, AddGame, RemoveGame, MoveGame,
    SettingsPanel, OptionsPanel, GamesPanel,

    MeshProps, ModelProps,
    ModelList, MeshList,
    AddModel, RemoveModel, MoveModel,
    AddMesh, RemoveMesh, MoveMesh,
    ExportModel, ViewModel,
    ModelExportPanel, ModelPanel, MeshPanel, PropertiesPanel,

    CollisionProps, SurfRampProps,
    SurfCollision, SurfRampify,
    SurfToolsPanel, CollisionPanel, CurvedRampPanel,

    # ImportMaterial, MaterialImportPanel,

    Props,
)


register_classes, unregister_classes = bpy.utils.register_classes_factory(
    classes)


def register():
    register_classes()
    bpy.types.Scene.BASE = bpy.props.PointerProperty(type=Props)


def unregister():
    # from . utils.vtf_wrapper.VTFLib import VTFLib
    # del VTFLib.vtflib_cdll
    unregister_classes()
    del bpy.types.Scene.BASE


if __name__ == "__main__":
    register()
