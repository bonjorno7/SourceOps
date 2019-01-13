# <libraries>
import bpy
# </libraries>

# <functions>
def change_grid_subdivisions(self, context):
    if self["grid_subdivisions"]:
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].overlay.grid_subdivisions = 8
    else:
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].overlay.grid_subdivisions = 10

def change_clip_distances(self, context):
    if self["clip_distances"]:
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].clip_start = 1.0
                area.spaces[0].clip_end = 100000.0
    else:
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].clip_start = 0.1
                area.spaces[0].clip_end = 1000.0
# </functions>

# <classes>
class BSE_OPTIONS_Panel(bpy.types.Panel):
    bl_idname = "bse.options_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "Blender Source Extras"
    bl_label = "Options"

    def draw(self, context):
        scope = context.scene.BSE_OPTIONS_properties
        self.layout.prop(scope, "grid_subdivisions")
        self.layout.prop(scope, "clip_distances")

class BSE_OPTIONS_PropertyGroup(bpy.types.PropertyGroup):
    grid_subdivisions = bpy.props.BoolProperty(
        name = "Grid Settings",
        description = "Change Grid Subdivisions from 10 to 8",
        update = change_grid_subdivisions,
        default = False,
    )

    clip_distances = bpy.props.BoolProperty(
        name = "Clip Distances",
        description = "Change Clip Start from 0.1 to 1.0 and Clip End from 1000 to 100000",
        update = change_clip_distances,
        default = False,
    )
# </classes>

# <registration>
classes = (
    BSE_OPTIONS_Panel,
    BSE_OPTIONS_PropertyGroup,
)

def register():
    for c in classes: bpy.utils.register_class(c)
    bpy.types.Scene.BSE_OPTIONS_properties = bpy.props.PointerProperty(type = BSE_OPTIONS_PropertyGroup)

def unregister():
    for c in classes: bpy.utils.unregister_class(c)
    del bpy.types.Scene.BSE_OPTIONS_properties
# </registration>