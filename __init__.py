# <definition>
bl_info = {
    "blender" : (2, 80, 0),
    "name" : "BASE",
    "description" : "Blender Add-on for Source Engine, a more convenient but less powerful alternative to Blender Source Tools",
    "author" : "bonjorno7",
    "version" : (0, 3, 3),
    "location" : "3D View > Sidebar",
    "category" : "Import-Export",
    "warning" : "",
}
# </definition>

# <import>
import bpy
from . settings import *
from . model_export import *
from . surf_tools import *
from . material_import import *
# </import>

# <classes>
class BASE_PG_Properties(bpy.types.PropertyGroup):
    """Global variables for this add-on"""
    settings: bpy.props.PointerProperty(type = BASE_PG_Settings)

    models: bpy.props.CollectionProperty(type = BASE_PG_Model)
    model_index: bpy.props.IntProperty(default = 0)

    collision: bpy.props.PointerProperty(type = BASE_PG_Collision)
    surf_ramp: bpy.props.PointerProperty(type = BASE_PG_SurfRamp)
# </classes>

# <variables>
classes = (
    BASE_PG_Game, BASE_PG_Settings,
    BASE_PG_Mesh, BASE_PG_Model,
    BASE_PG_Collision, BASE_PG_SurfRamp,

    BASE_UL_Game, BASE_OT_GameAdd, BASE_OT_GameRemove, BASE_OT_GameMove,
    BASE_UL_Model, BASE_OT_ModelAdd, BASE_OT_ModelRemove, BASE_OT_ModelMove,
    BASE_UL_Mesh, BASE_OT_MeshAdd, BASE_OT_MeshRemove, BASE_OT_MeshMove,
    BASE_OT_ModelExport, BASE_OT_ModelView,
    BASE_OT_SurfRampify, BASE_OT_SurfCollision,
    BASE_OT_ImportMaterial,

    BASE_PT_Settings, BASE_PT_Options, BASE_PT_Games,
    BASE_PT_ModelExport, BASE_PT_Model, BASE_PT_Mesh, BASE_PT_Properties,
    BASE_PT_SurfTools, BASE_PT_Collision, BASE_PT_CurvedRamp,
    BASE_PT_MaterialImport,

    BASE_PG_Properties,
)

register_classes, unregister_classes = bpy.utils.register_classes_factory(classes)
# </variables>

# <functions>
def register():
    register_classes()
    bpy.types.Scene.BASE = bpy.props.PointerProperty(type = BASE_PG_Properties)

def unregister():
    unregister_classes()
    del bpy.types.Scene.BASE

if __name__ == "__main__":
    register()
# </functions>