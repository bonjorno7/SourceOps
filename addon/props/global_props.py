import bpy
from . model_props import SOURCEOPS_ModelProps
from . map_props import SOURCEOPS_MapProps


class SOURCEOPS_GlobalProps(bpy.types.PropertyGroup):
    model_items: bpy.props.CollectionProperty(type=SOURCEOPS_ModelProps)
    model_index: bpy.props.IntProperty(default=0, name='Ctrl click to rename')

    map_items: bpy.props.CollectionProperty(type=SOURCEOPS_MapProps)
    map_index: bpy.props.IntProperty(default=0, name='Ctrl click to rename')

    simulation_input: bpy.props.PointerProperty(
        name='Simulation Input',
        description='The collection containing your rigid body objects',
        type=bpy.types.Collection,
    )

    simulation_output: bpy.props.PointerProperty(
        name='Simulation Output',
        description='The collection your rigged objects will go',
        type=bpy.types.Collection,
    )

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
            ('ATTACHMENTS', 'Attachments', 'Display the attachments panel', 'BONE_DATA', 7),
            ('MAPS', 'Maps', 'Display the maps panel', 'MOD_BUILD', 8),
            ('SIMULATION', 'Simulation', 'Display the simulation panel', 'PHYSICS', 9),
            ('MISC', 'Misc', 'Display the misc panel', 'MONKEY', 10),
        ],
    )
