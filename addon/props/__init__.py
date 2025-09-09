import bpy
from . map_props import SOURCEOPS_MapProps
from . attachment_props import SOURCEOPS_AttachmentProps
from . particle_props import SOURCEOPS_ParticleProps
from . event_props import SOURCEOPS_EventProps
from . sequence_props import SOURCEOPS_SequenceProps
from . skin_props import SOURCEOPS_SkinProps
from . material_folder_props import SOURCEOPS_MaterialFolderProps
from . lods_props import SOURCEOPS_LodItemProps, SOURCEOPS_ModelLodProps 
from . model_props import SOURCEOPS_ModelProps
from . game_props import SOURCEOPS_GameProps
from . global_props import SOURCEOPS_GlobalProps
from . addon_prefs import SOURCEOPS_AddonPrefs

classes = (
    SOURCEOPS_MapProps,
    SOURCEOPS_AttachmentProps,
    SOURCEOPS_ParticleProps,
    SOURCEOPS_EventProps,
    SOURCEOPS_SequenceProps,
    SOURCEOPS_SkinProps,
    SOURCEOPS_MaterialFolderProps,
    SOURCEOPS_LodItemProps,
    SOURCEOPS_ModelLodProps,
    SOURCEOPS_ModelProps,
    SOURCEOPS_GameProps,
    SOURCEOPS_GlobalProps,
    SOURCEOPS_AddonPrefs
)

class_register, class_unregister = bpy.utils.register_classes_factory(classes)

def register():
    class_register()

    bpy.types.Scene.sourceops = bpy.props.PointerProperty(type=SOURCEOPS_GlobalProps)


def unregister():
    del bpy.types.Scene.sourceops

    class_unregister()
