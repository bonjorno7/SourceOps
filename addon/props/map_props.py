import bpy


class SOURCEOPS_MapProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name='Name',
        description='The name of the VMF to overwrite with your displacements',
        default='example',
    )

    brush_collection: bpy.props.PointerProperty(
        name='Brushes',
        description='The collection containing your brush objects',
        type=bpy.types.Collection,
    )

    disp_collection: bpy.props.PointerProperty(
        name='Displacements',
        description='The collection containing your displacement objects',
        type=bpy.types.Collection,
    )

    geometry_scale: bpy.props.IntProperty(
        name='Geometry Scale',
        description='How much the geometry will be scaled, just to allow more convenient modeling',
        default=64,
        min=1,
        max=16384,
    )

    texture_scale: bpy.props.FloatProperty(
        name='Texture Scale',
        description='Size of one texel in hammer units',
        default=1.0,
        min=0,
        max=64,
        step=1,
        precision=3,
    )

    lightmap_scale: bpy.props.IntProperty(
        name='Lightmap Scale',
        description='Hammer units per lightmap luxel on the generated brushes',
        default=32,
        min=1,
        max=16384,
    )

    allow_skewed_textures: bpy.props.BoolProperty(
        name='Allow Skewed Textures',
        description='Allow non-perpendicular UV axes. Works in Hammer as long as faces are not skewed themselves',
        default=False,
    )

    align_to_grid: bpy.props.BoolProperty(
        name='Align to Grid',
        description='Round the scaled UVs to whole numbers so the brushes sit on the hammer grid',
        default=True,
    )
