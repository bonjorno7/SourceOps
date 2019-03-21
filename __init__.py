# <definition>
bl_info = {
    "blender" : (2, 80, 0),
    "name" : "BASE",
    "description" : "Blender Add-on for Source Engine, a more convenient but less powerful alternative to Blender Source Tools",
    "author" : "bonjorno7",
    "version" : (0, 2, 8),
    "location" : "3D View > Sidebar",
    "category" : "Import-Export",
    "warning" : "",
}
# </definition>

# <import>
import bpy
from .settings import *
from .model_export import *
from .surf_tools import *
# </import>

# <classes>
class Properties(bpy.types.PropertyGroup):
    """Global variables for this add-on"""
    settings: bpy.props.PointerProperty(type = Settings)

    models: bpy.props.CollectionProperty(type = Model)
    model_index: bpy.props.IntProperty(default = 0)

    collision: bpy.props.PointerProperty(type = Collision)
    surf_ramp: bpy.props.PointerProperty(type = SurfRamp)
# </classes>

# <variables>
classes = (
    Game, Settings,
    Mesh, MatDir, Model,
    Collision, SurfRamp,

    GameList, GameAdd, GameRemove, GameMove,
    ModelList, ModelAdd, ModelCopy, ModelRemove, ModelMove,
    MeshList, MeshAdd, MeshRemove, MeshMove,
    MatDirList, MatDirAdd, MatDirRemove, MatDirMove,

    ModelExport, ModelView,
    SurfRampify, SurfCollision,

    SettingsPanel, OptionsPanel, GamesPanel,
    ModelExportPanel, ModelPanel, MeshPanel, MatDirPanel,
    SurfToolsPanel, CollisionPanel, CurvedRampPanel,

    Properties,
)

register_classes, unregister_classes = bpy.utils.register_classes_factory(classes)
# </variables>

# <functions>
def register():
    register_classes()
    bpy.types.Scene.BASE = bpy.props.PointerProperty(type = Properties)

def unregister():
    unregister_classes()
    del bpy.types.Scene.BASE

if __name__ == "__main__":
    register()
# </functions>