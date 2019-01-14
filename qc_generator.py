# <libraries>
import os
import bpy
import bpy_extras
from . import common
# </libraries>

# <classes>
class BSE_QC_GENERATOR_Panel(bpy.types.Panel):
    bl_idname = "bse.qc_generator_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "Blender Source Extras"
    bl_label = "QC Generator"

    def draw(self, context):
        scope = context.scene.BSE_QC_GENERATOR_properties
        common.add_prop(self, "Model Name", scope, "model_name")
        common.add_prop(self, "Reference", scope, "reference")
        common.add_prop(self, "Collision", scope, "collision")
        common.add_prop(self, "Model Path", scope, "model_path")
        common.add_prop(self, "Material Path", scope, "material_path")
        common.add_prop(self, "Surface Property", scope, "surface_property")
        self.layout.operator("bse.qc_generator_generate_qc")

class BSE_QC_GENERATOR_PropertyGroup(bpy.types.PropertyGroup):
    model_name = bpy.props.StringProperty(
        name = "",
        description = "Your model's name, eg example (you don't need to add the file extension)",
        default = "Model",
    )

    reference = bpy.props.PointerProperty(
        name = "",
        description = "Select your Reference mesh here",
        type = bpy.types.Object,
        poll = common.is_mesh,
    )

    collision = bpy.props.PointerProperty(
        name = "",
        description = "Select your Reference mesh here",
        type = bpy.types.Object,
        poll = common.is_mesh,
    )

    model_path = bpy.props.StringProperty(
        name = "",
        description = "The folder where your compiled model goes, eg props/example",
        default = "props/example",
    )

    material_path = bpy.props.StringProperty(
        name = "",
        description = "The folder with your model's materials, eg models/props/example",
        default = "models/props/example",
    )

    surface_property = bpy.props.EnumProperty(
        name = "",
        description = "Choose the substance your model is made out of, this affects how it sounds in game",
        items = common.surface_properties,
    )

class BSE_QC_GENERATOR_GenerateQC(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Generate a QC file based on your settings"""
    bl_idname = "bse.qc_generator_generate_qc"
    bl_label = "Generate QC"
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = ".qc"

    filter_glob = bpy.props.StringProperty(
        default = "*.qc",
        options = {'HIDDEN'},
        maxlen = 255,
    )

    @classmethod
    def poll(cls, context):
        scope = context.scene.BSE_QC_GENERATOR_properties
        return scope.model_name and scope.reference and scope.collision and scope.model_path and scope.material_path and scope.surface_property

    def execute(self, context):
        scope = context.scene.BSE_QC_GENERATOR_properties
        model_name = scope.model_name
        reference = scope.reference.name
        collision = scope.collision.name
        model_path = common.replace_slashes(scope.model_path)
        material_path = common.replace_slashes(scope.material_path)
        surface_property = scope.surface_property

        f = open(self.filepath, 'w', encoding='utf-8')
        f.write("$modelname \"" + os.path.join(model_path, model_name) + "\"\n")
        f.write("$body shell \"" + reference + "\"\n")
        f.write("$collisionmodel \"" + collision + "\" { $concave $maxconvexpieces 1000 }\n")
        f.write("$sequence idle \"" + reference + "\"\n")
        f.write("$cdmaterials \"" + material_path + "\"\n")
        f.write("$surfaceprop \"" + surface_property + "\"\n")
        f.write("$staticprop")
        f.close()

        return {'FINISHED'}
# </classes>

# <registration>
classes = (
    BSE_QC_GENERATOR_Panel,
    BSE_QC_GENERATOR_PropertyGroup,
    BSE_QC_GENERATOR_GenerateQC,
)

def register():
    for c in classes: bpy.utils.register_class(c)
    bpy.types.Scene.BSE_QC_GENERATOR_properties = bpy.props.PointerProperty(type = BSE_QC_GENERATOR_PropertyGroup)

def unregister():
    for c in classes: bpy.utils.unregister_class(c)
    del bpy.types.Scene.BSE_QC_GENERATOR_properties
# </registration>