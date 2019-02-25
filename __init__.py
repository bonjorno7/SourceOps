# <definition>
bl_info = {
    "blender" : (2, 80, 0),
    "name" : "BASE",
    "description" : "Blender Add-on for Source Engine, Alternative to Blender Source Tools",
    "author" : "bonjorno7",
    "version" : (0, 2, 4),
    "location" : "3D View > Sidebar",
    "category" : "Import-Export",
    "warning" : "",
}
# </definition>

# <import>
import bpy
from . import settings as se
from . import model_export as me
from . import modeling as mo
# </import>

# <classes>
class Properties(bpy.types.PropertyGroup):
    """Global variables for this add-on"""
    settings: bpy.props.PointerProperty(type = se.Settings)

    models: bpy.props.CollectionProperty(type = me.Model)
    model_index: bpy.props.IntProperty(default = 0)

    collision_settings: bpy.props.PointerProperty(type = mo.CollisionSettings)
    surf_ramp: bpy.props.PointerProperty(type = mo.SurfRamp)
# </classes>

# <variables>
classes = (
    se.Game, se.Settings, me.Mesh, me.MatDir, me.Model, mo.CollisionSettings, mo.SurfRamp,
    se.GameList, se.GameAdd, se.GameRemove,
    me.ModelList, me.ModelAdd, me.ModelRemove,
    me.MeshList, me.MeshAdd, me.MeshRemove,
    me.MatDirList, me.MatDirAdd, me.MatDirRemove,
    me.ModelExport, me.ModelView,
    mo.SurfRampModify, mo.GenerateCollision,
    se.SettingsPanel, me.ModelExportPanel, mo.ModelingPanel,
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