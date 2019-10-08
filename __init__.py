import bpy

from . settings . game import GameProps
from . settings . settings import SettingsProps
from . settings . operators import AddGame, RemoveGame, MoveGame
from . settings . interface import GameList,  SettingsPanel, OptionsPanel, GamesPanel

from . model_export . model import ModelProps
from . model_export . operators import AddModel, RemoveModel, MoveModel, ExportMeshes, GenerateQC, EditQC, CompileQC, ViewModel
from . model_export . interface import ModelList, ModelExportPanel, ModelPanel, PropertiesPanel

from . material_import_export . material_import import ImportMaterial, MaterialImportPanel

from . surf_tools . surf_collision import CollisionProps, SurfCollision
from . surf_tools . curved_ramp import SurfRampProps, SurfRampify
from . surf_tools . panels import SurfToolsPanel, CollisionPanel, CurvedRampPanel


bl_info = {
    "blender": (2, 80, 0),
    "name": "SourceOps",
    "description": "A more convenient alternative to Blender Source Tools",
    "author": "bonjorno7 & REDxEYE",
    "version": (0, 4, 6),
    "location": "3D View > Sidebar",
    "category": "Import-Export",
}


class Globals(bpy.types.PropertyGroup):
    """Global variables for this add-on"""
    bl_idname = "SOURCEOPS_PG_Props"
    settings: bpy.props.PointerProperty(type=SettingsProps)

    models: bpy.props.CollectionProperty(type=ModelProps)
    model_index: bpy.props.IntProperty(default=0)

    def model(self):
        if self.models and self.model_index >= 0:
            return self.models[self.model_index]
        return None

    collision: bpy.props.PointerProperty(type=CollisionProps)
    surf_ramp: bpy.props.PointerProperty(type=SurfRampProps)


classes = (
    GameProps, SettingsProps,
    GameList, AddGame, RemoveGame, MoveGame,
    SettingsPanel, OptionsPanel, GamesPanel,

    ModelProps, ModelList,
    AddModel, RemoveModel, MoveModel,
    ExportMeshes, GenerateQC, EditQC, CompileQC, ViewModel,
    ModelExportPanel, ModelPanel, PropertiesPanel,

    CollisionProps, SurfRampProps,
    SurfCollision, SurfRampify,
    SurfToolsPanel, CollisionPanel, CurvedRampPanel,

    ImportMaterial, MaterialImportPanel,

    Globals,
)


register_classes, unregister_classes = bpy.utils.register_classes_factory(classes)


def register():
    register_classes()
    bpy.types.Scene.SOURCEOPS = bpy.props.PointerProperty(type=Globals)


def unregister():
    from . utils.vtf_wrapper.VTFLib import VTFLib
    del VTFLib.vtflib_cdll
    unregister_classes()
    del bpy.types.Scene.SOURCEOPS


if __name__ == "__main__":
    register()
