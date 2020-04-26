import bpy


class SOURCEOPS_MapProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name='Map Name',
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

    uv_scale: bpy.props.IntProperty(
        name='UV Scale',
        description='How much the generated brushes will be scaled, necessary to get around floating point inprecision',
        default=128,
        min=1,
        max=16384,
    )

    geometry_scale: bpy.props.IntProperty(
        name='Geometry Scale',
        description='How much the geometry will be scaled, just to allow more convenient modeling',
        default=64,
        min=1,
        max=16384,
    )

    lightmap_scale: bpy.props.IntProperty(
        name='Lightmap Scale',
        description='Hammer units per lightmap luxel on the generated brushes',
        default=32,
        min=1,
        max=16384,
    )

    align_to_grid: bpy.props.BoolProperty(
        name='Align to Grid',
        description='Round the scaled UVs to whole numbers so the brushes sit on the hammer grid',
        default=True,
    )
