import bpy
from . material_folder_props import SOURCEOPS_MaterialFolderProps
from . skin_props import SOURCEOPS_SkinProps
from . sequence_props import SOURCEOPS_SequenceProps
from . surface_props import SOURCEOPS_SurfaceProps


class SOURCEOPS_ModelProps(bpy.types.PropertyGroup):
    material_folder_items: bpy.props.CollectionProperty(type=SOURCEOPS_MaterialFolderProps)
    material_folder_index: bpy.props.IntProperty(default=0, name='Ctrl click to rename')

    skin_items: bpy.props.CollectionProperty(type=SOURCEOPS_SkinProps)
    skin_index: bpy.props.IntProperty(default=0, name='Ctrl click to rename')

    sequence_items: bpy.props.CollectionProperty(type=SOURCEOPS_SequenceProps)
    sequence_index: bpy.props.IntProperty(default=0, name='Ctrl click to rename')

    name: bpy.props.StringProperty(
        name='Name',
        description='Your model\'s path, eg example/model',
        default='example/model',
    )

    reference: bpy.props.PointerProperty(
        name='Reference',
        description='Visible meshes combined into one body',
        type=bpy.types.Collection,
    )

    collision: bpy.props.PointerProperty(
        name='Collision',
        description='Tangible meshes combined into one body',
        type=bpy.types.Collection,
    )

    bodygroups: bpy.props.PointerProperty(
        name='Bodygroups',
        description='Groups of visible meshes, the game can choose one body per group',
        type=bpy.types.Collection,
    )

    stacking: bpy.props.PointerProperty(
        name='Stacking',
        description='Visible meshes drawn in the specified order',
        type=bpy.types.Collection,
    )

    surface: bpy.props.EnumProperty(
        name='Surface Property',
        description='$surfaceprop, this affects decals and how it sounds in game',
        items=SOURCEOPS_SurfaceProps,
        default='default',
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

    prepend_armature: bpy.props.BoolProperty(
        name='Prepend Armature',
        description='Prepend the name of the armature to every bone name in your SMD files. Necessary for multi-armature models',
        default=True,
    )

    ignore_transforms: bpy.props.BoolProperty(
        name='Ignore Transforms',
        description='Ignores all transforms of all objects, this includes parenting',
        default=False,
    )

    origin_x: bpy.props.FloatProperty(
        name='Origin +X',
        description='Translation on the positive X axis for $origin in the QC file',
        default=0.0,
    )

    origin_y: bpy.props.FloatProperty(
        name='Origin +Y',
        description='Translation on the positive Y axis for $origin in the QC file',
        default=0.0,
    )

    origin_z: bpy.props.FloatProperty(
        name='Origin -Z',
        description='Translation on the negative Z axis for $origin in the QC file, because Source is weird like that',
        default=0.0,
    )

    rotation: bpy.props.FloatProperty(
        name='Rotation',
        description='Rotation around the up axis for $origin in the QC file, this is applied after the location',
        default=0.0,
    )

    scale: bpy.props.FloatProperty(
        name='Scale',
        description='$scale to put at the top of your QC files, this does not affect $origin',
        default=1.0,
    )
