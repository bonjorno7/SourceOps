# <definition>
bl_info = {
    "blender" : (2, 80, 0),
    "name" : "Blender Add-on for Source Engine",
    "description" : "Alternative to Blender Source Tools",
    "author" : "bonjorno7",
    "version" : (0, 1, 9),
    "location" : "3D View > Sidebar",
    "category" : "Import / Export",
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
    settings = bpy.props.PointerProperty(type = se.Settings)

    models = bpy.props.CollectionProperty(type = me.Model)
    model_index = bpy.props.IntProperty(name = "", default = 0)

    surf_ramp = bpy.props.PointerProperty(type = mo.SurfRamp)
# </classes>

# <variables>
classes = (
    se.Game, se.Settings, me.Mesh, me.MatDir, me.Model, mo.SurfRamp,
    se.GameList, se.GameAdd, se.GameRemove, se.SettingsPanel,
    me.ModelList, me.ModelAdd, me.ModelRemove, me.MeshList, me.MeshAdd, me.MeshRemove, me.MatDirList, me.MatDirAdd, me.MatDirRemove, me.ModelExport, me.ModelView, me.ModelExportPanel,
    mo.SurfRampModify, mo.GenerateCollision, mo.ModelingPanel,
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