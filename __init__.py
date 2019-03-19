# <definition>
bl_info = {
    "blender" : (2, 80, 0),
    "name" : "BASE",
    "description" : "Blender Add-on for Source Engine, a more convenient but less powerful alternative to Blender Source Tools that's mostly focused on surf mapping",
    "author" : "bonjorno7",
    "version" : (0, 2, 6),
    "location" : "3D View > Sidebar",
    "category" : "Import-Export",
    "warning" : "",
}
# </definition>

# <import>
import bpy
from . import settings as se
from . import model_export as me
from . import material_export as ma
from . import surf_tools as st
# </import>

# <classes>
class Properties(bpy.types.PropertyGroup):
    """Global variables for this add-on"""
    settings: bpy.props.PointerProperty(type = se.Settings)

    models: bpy.props.CollectionProperty(type = me.Model)
    model_index: bpy.props.IntProperty(default = 0)

    material: bpy.props.PointerProperty(type = ma.Material)

    collision: bpy.props.PointerProperty(type = st.Collision)
    surf_ramp: bpy.props.PointerProperty(type = st.SurfRamp)
# </classes>

# <variables>
classes = (
    se.Game, se.Settings,
    me.Mesh, me.MatDir, me.Model,
    ma.Material,
    st.Collision, st.SurfRamp,

    se.GameList, se.GameAdd, se.GameRemove, se.GameMove,
    me.ModelList, me.ModelAdd, me.ModelRemove, me.ModelMove,
    me.MeshList, me.MeshAdd, me.MeshRemove, me.MeshMove,
    me.MatDirList, me.MatDirAdd, me.MatDirRemove, me.MatDirMove,

    me.ModelExport, me.ModelView,
    st.SurfToolsAddModifiers, st.GenerateCollision, st.FixHammerRamp,

    se.SettingsPanel, se.OptionsPanel, se.GamesPanel,
    me.ModelExportPanel, me.ModelPanel, me.MeshPanel, me.MatDirPanel,
    st.SurfToolsPanel, st.CollisionPanel, st.CurvedRampPanel,

    Properties,
)

register_classes, unregister_classes = bpy.utils.register_classes_factory(classes)
# </variables>

# <functions>
def register():
    register_classes()
    bpy.types.Scene.BASE = bpy.props.PointerProperty(type = Properties)
    bpy.types.VIEW3D_MT_edit_mesh_specials.append(st.surf_tools_menu)

def unregister():
    unregister_classes()
    del bpy.types.Scene.BASE
    bpy.types.VIEW3D_MT_edit_mesh_specials.remove(st.surf_tools_menu)

if __name__ == "__main__":
    register()
# </functions>