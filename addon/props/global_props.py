import bpy
from . game_props import SOURCEOPS_GameProps
from . model_props import SOURCEOPS_ModelProps
from . displacement_props import SOURCEOPS_DisplacementProps


class SOURCEOPS_GlobalProps(bpy.types.PropertyGroup):
    game_items: bpy.props.CollectionProperty(type=SOURCEOPS_GameProps)
    game_index: bpy.props.IntProperty(default=0, name='Ctrl click to rename')

    model_items: bpy.props.CollectionProperty(type=SOURCEOPS_ModelProps)
    model_index: bpy.props.IntProperty(default=0, name='Ctrl click to rename')

    displacement_props: bpy.props.PointerProperty(type=SOURCEOPS_DisplacementProps)

    panel: bpy.props.EnumProperty(
        name='Panel',
        description='Which panel to display',
        items=[
            ('GAMES', 'Games', 'Display the games panel', 'PREFERENCES', 1),
            ('MODELS', 'Models', 'Display the models panel', 'MESH_CUBE', 2),
            ('MODEL_OPTIONS', 'Model Options', 'Display the model options panel', 'MODIFIER', 3),
            ('TEXTURES', 'Textures', 'Display the textures panel', 'TEXTURE', 4),
            ('SEQUENCES', 'Sequences', 'Display the sequences panel', 'SEQUENCE', 5),
            ('EVENTS', 'Events', 'Display the events panel', 'ACTION', 6),
            ('DISPLACEMENTS', 'Displacements', 'Display the displacements panel', 'MONKEY', 7),
        ],
    )
