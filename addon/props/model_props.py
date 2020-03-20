import bpy
from . material_folder_props import SOURCEOPS_MaterialFolderProps
from . sequence_props import SOURCEOPS_SequenceProps
from . surface_props import SOURCEOPS_SurfaceProps


class SOURCEOPS_ModelProps(bpy.types.PropertyGroup):
    material_folder_items: bpy.props.CollectionProperty(type=SOURCEOPS_MaterialFolderProps)
    material_folder_index: bpy.props.IntProperty(default=0, name='Ctrl click to rename')

    sequence_items: bpy.props.CollectionProperty(type=SOURCEOPS_SequenceProps)
    sequence_index: bpy.props.IntProperty(default=0, name='Ctrl click to rename')

    display: bpy.props.StringProperty(
        name='Display Name',
        description='The name this model has in the list',
        default='Model Name',
    )

    name: bpy.props.StringProperty(
        name='Model Name',
        description='Your model\'s path, eg example/model',
        default='example/model',
    )

    reference: bpy.props.PointerProperty(
        name='Reference',
        description='Visible meshes combined into one body',
        type=bpy.types.Collection,
    )

    collision: bpy.props.PointerProperty(
        name='Reference',
        description='Tangible meshes combined into one body',
        type=bpy.types.Collection,
    )

    bodygroups: bpy.props.PointerProperty(
        name='Reference',
        description='Groups of visible meshes, the game can choose one body per group',
        type=bpy.types.Collection,
    )

    stacking: bpy.props.PointerProperty(
        name='Reference',
        description='Visible meshes drawn in the specified order',
        type=bpy.types.Collection,
    )

    surface: bpy.props.EnumProperty(
        name='Surface Property',
        description='$surfaceprop, this affects decals and how it sounds in game',
        items=SOURCEOPS_SurfaceProps,
    )

    scale: bpy.props.FloatProperty(
        name='Scale',
        description='$scale to put at the top of your QC files',
        default=1.0,
    )

    static: bpy.props.BoolProperty(
        name='Static Prop',
        description='$staticprop, removes animations, does some optimization. Warning: can cause issues such as blank for bodygroups not working',
        default=False,
    )

    glass: bpy.props.BoolProperty(
        name='Has Glass',
        description='$mostlyopaque, use this if your model has something transparent like glass',
        default=False,
    )

    ignore_transforms: bpy.props.BoolProperty(
        name='Ignore Transforms',
        description='Ignores all transforms of all objects, this includes parenting',
        default=False,
    )
