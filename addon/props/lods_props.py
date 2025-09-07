import bpy

class SOURCEOPS_LodItemProps(bpy.types.PropertyGroup):

    source: bpy.props.PointerProperty(
        name='Source',
        description='Replace source',
        type=bpy.types.Collection,
    )

    def poll_target(self, object):
        return object not in (self.source)

    target: bpy.props.PointerProperty(
        name='Replace target',
        description='Replacment for',
        type=bpy.types.Collection,
    )


class SOURCEOPS_ModelLodProps(bpy.types.PropertyGroup):

    distance: bpy.props.IntProperty(
        name='Distance',
        description='Distance to switch to this LOD',
        min=0,
    )
 
    replacemodel_items: bpy.props.CollectionProperty(type=SOURCEOPS_LodItemProps)
    replacemodel_index: bpy.props.IntProperty(default=0, name='Ctrl click to rename')
