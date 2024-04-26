import bpy
from . map_props import SOURCEOPS_MapProps
from . attachment_props import SOURCEOPS_AttachmentProps
from . particle_props import SOURCEOPS_ParticleProps
from . event_props import SOURCEOPS_EventProps
from . sequence_props import SOURCEOPS_SequenceProps
from . skin_props import SOURCEOPS_SkinProps
from . material_folder_props import SOURCEOPS_MaterialFolderProps
from . model_props import SOURCEOPS_ModelProps
from . game_props import SOURCEOPS_GameProps
from . global_props import SOURCEOPS_GlobalProps
from . addon_prefs import SOURCEOPS_AddonPrefs


def register():
    bpy.utils.register_class(SOURCEOPS_MapProps)
    bpy.utils.register_class(SOURCEOPS_AttachmentProps)
    bpy.utils.register_class(SOURCEOPS_ParticleProps)
    bpy.utils.register_class(SOURCEOPS_EventProps)
    bpy.utils.register_class(SOURCEOPS_SequenceProps)
    bpy.utils.register_class(SOURCEOPS_SkinProps)
    bpy.utils.register_class(SOURCEOPS_MaterialFolderProps)
    bpy.utils.register_class(SOURCEOPS_ModelProps)
    bpy.utils.register_class(SOURCEOPS_GameProps)
    bpy.utils.register_class(SOURCEOPS_GlobalProps)
    bpy.utils.register_class(SOURCEOPS_AddonPrefs)
    bpy.types.Scene.sourceops = bpy.props.PointerProperty(type=SOURCEOPS_GlobalProps)


def unregister():
    del bpy.types.Scene.sourceops
    bpy.utils.unregister_class(SOURCEOPS_AddonPrefs)
    bpy.utils.unregister_class(SOURCEOPS_GlobalProps)
    bpy.utils.unregister_class(SOURCEOPS_GameProps)
    bpy.utils.unregister_class(SOURCEOPS_ModelProps)
    bpy.utils.unregister_class(SOURCEOPS_MaterialFolderProps)
    bpy.utils.unregister_class(SOURCEOPS_SkinProps)
    bpy.utils.unregister_class(SOURCEOPS_SequenceProps)
    bpy.utils.unregister_class(SOURCEOPS_EventProps)
    bpy.utils.unregister_class(SOURCEOPS_AttachmentProps)
    bpy.utils.unregister_class(SOURCEOPS_ParticleProps)
    bpy.utils.unregister_class(SOURCEOPS_MapProps)
