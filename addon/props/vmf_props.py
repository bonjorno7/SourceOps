import bpy


class SOURCEOPS_VMFProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name='Map Name',
        description='The name of the VMF to import',
        default='example',
        subtype='FILE_PATH',
    )
    
    scale: bpy.props.FloatProperty(
        name='Map Scale',
        description='The size of 1 hammer unit in blender units',
        default=0.01,
    )
    
    epsilon: bpy.props.FloatProperty(
        name='Epsilon',
        description='May help with glitchy geometry',
        default=0.01,
    )