import bpy


class SOURCEOPS_DisplacementProps(bpy.types.PropertyGroup):
    map_path: bpy.props.StringProperty(
        name='Map Path',
        description='The path to the VMF to integrate these displacements into',
        default='mapsrc/example.vmf',
        subtype='FILE_PATH',
    )

    visgroup: bpy.props.StringProperty(
        name='Visgroup Name',
        description='The name of the visgroup these displacements will be put into',
        default='displacements',
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
