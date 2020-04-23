import bpy


class SOURCEOPS_DisplacementProps(bpy.types.PropertyGroup):
    display: bpy.props.StringProperty(
        name='Display Name',
        description='The name this map has in the list',
        default='Map Name',
    )

    name: bpy.props.StringProperty(
        name='Map Name',
        description='The of the VMF to overwrite with your displacements',
        default='example',
    )

    collection: bpy.props.PointerProperty(
        name='Collection',
        description='The collection containing your displacement objects',
        type=bpy.types.Collection,
    )

    brush_scale: bpy.props.IntProperty(
        name='Brush Scale',
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
