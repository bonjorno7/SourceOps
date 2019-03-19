# <import>
import bpy
from mathutils import Vector
from . import common
# </import>

# <functions>
def update_translucent(self, context):
    material = context.scene.BASE.material
    if material.translucent:
        material.alpha_test = False

def update_alpha_test(self, context):
    material = context.scene.BASE.material
    if material.alpha_test:
        material.translucent = False
# </functions>

# <types>
class Material(bpy.types.PropertyGroup):
    """Properties for a material"""

    # <base>
    model: bpy.props.BoolProperty(
        name = "Model",
        description = "Whether this material is for models or brushes",
        default = True,
    )

    shader: bpy.props.EnumProperty(
        name = "Shader",
        description = "Shader for this material",
        items = (
            ('VertexLitGeneric', "VertexLitGeneric", "Calculate lighting per vertex. Supports models but not brushes"),
            ('LightmappedGeneric', "LightmappedGeneric", "Uses lightmaps. Supports brushes but not models"),
            ('UnlitGeneric', "UnlitGeneric", "Don't light the material, keep it full bright. Supports both brushes and models"),
            ('Refract', "Refract", "Refractive material, bends light behind it. Supports both brushes and models"),
            ('Character', "Character", "Same as VertexLitGeneric but looks better on low settings, typically used for character models but can be used on static and dymanic props too in CS:GO"),
        ),
    )

    surface_property: bpy.props.EnumProperty(
        name = "Surface Property",
        description = "Choose the substance your material is made out of, this affects decals and how it sounds in game",
        items = common.surface_properties,
    )
    # </base>

    # <textures>
    diffuse: bpy.props.PointerProperty(
        name = "Diffuse",
        description = "Diffuse texture for this material",
        type = bpy.types.Image,
    )

    normal: bpy.props.PointerProperty(
        name = "Normal",
        description = "Normal texture for this material",
        type = bpy.types.Image,
    )
    # </textures>

    # <transparency>
    opacity: bpy.props.FloatProperty(
        name = "Opacity",
        description = "How opaque the material should be",
        default = 1.0,
        min = 0.0,
        max = 1.0,
    )

    translucent: bpy.props.BoolProperty(
        name = "Translucent",
        description = "Make the material translucent based on the alpha of the diffuse texture",
        update = update_translucent,
        default = False,
    )

    additive: bpy.props.BoolProperty(
        name = "Additive",
        description = "Add the color instead of multiplying",
        default = False,
    )

    alpha_test: bpy.props.BoolProperty(
        name = "Alpha Test",
        description = "Cull pixels whose opacity is less than the threshold",
        update = update_alpha_test,
        default = False,
    )

    threshold: bpy.props.FloatProperty(
        name = "Threshold",
        description = "Threshold for Alpha Test",
        default = 0.7,
        min = 0.0,
        max = 1.0,
    )

    two_sided: bpy.props.BoolProperty(
        name = "Two Sided",
        description = "Make the back of faces with this material visible",
        default = False,
    )

    decal: bpy.props.BoolProperty(
        name = "Decal",
        description = "Prevent decal texture clipping",
        default = False,
    )
    # </transparency>

    # <color>
    color: bpy.props.FloatVectorProperty(
        name = "Color",
        description = "Multiply the base color with this color",
        subtype = 'COLOR',
    )

    tint_mask: bpy.props.PointerProperty(
        name = "Tint",
        description = "Mask texture for tint, which texels should be tinted by Color 2",
        type = bpy.types.Image,
    )
    # </color>

    # <reflection>
    envmap: bpy.props.StringProperty(
        name = "Cubemap",
        description = "Cubemap to use for reflection on this material, leave as env_cubemap to reflect the nearest cubemap, or enter a path to a custom cubemap",
        default = "env_cubemap",
    )

    envmap_mask: bpy.props.StringProperty(
        name = "Specular",
        description = "Specular texture, leave empty for constant reflection",
        default = "",
    )

    envmap_tint: bpy.props.FloatVectorProperty(
        name = "Cubemap Tint",
        description = "Strength and tint of the reflection",
        subtype = 'COLOR',
    )

    envmap_saturation: bpy.props.FloatProperty(
        name = "Cubemap Saturation",
        description = "Saturation of the reflection, 0 is grayscale, 1 is natural",
        default = 1.0,
        min = 0.0,
        max = 1.0,
    )

    envmap_contrast: bpy.props.FloatProperty(
        name = "Cubemap Contrast",
        description = "Contrast of the reflection, 0 is natural, 1 is the original color squared",
        default = 0.0,
        min = 0.0,
        max = 1.0,
    )

    envmap_fresnel: bpy.props.FloatProperty(
        name = "Cubemap Fresnel",
        description = "Adds a Fresnel effect to the reflection, which becomes multiplied with values higher than 1. Only works on VertexlitGeneric",
        default = 0.0,
        min = 0.0,
        max = 10.0,
    )
    # </reflection>

    # <self illumination>
    self_illumination: bpy.props.PointerProperty(
        name = "Self Illumination",
        description = "Mask texture for self illumination, which texels should be full bright",
        type = bpy.types.Image,
    )
    # self_illumination_mask (string)
    # specular_map_alpha (bool)
    # self_illumination_tint (rgb)
    # fresnel (min, max, exp)
    # </self illumination>
# </types>

