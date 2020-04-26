import bpy
from . lists import SOURCEOPS_UL_GameList
from . lists import SOURCEOPS_UL_ModelList
from . lists import SOURCEOPS_UL_MaterialFolderList
from . lists import SOURCEOPS_UL_SkinList
from . lists import SOURCEOPS_UL_SequenceList
from . lists import SOURCEOPS_UL_EventList
from . lists import SOURCEOPS_UL_MapList
from . panels import SOURCEOPS_PT_MainPanel


def register():
    bpy.utils.register_class(SOURCEOPS_UL_GameList)
    bpy.utils.register_class(SOURCEOPS_UL_ModelList)
    bpy.utils.register_class(SOURCEOPS_UL_MaterialFolderList)
    bpy.utils.register_class(SOURCEOPS_UL_SkinList)
    bpy.utils.register_class(SOURCEOPS_UL_SequenceList)
    bpy.utils.register_class(SOURCEOPS_UL_EventList)
    bpy.utils.register_class(SOURCEOPS_UL_MapList)
    bpy.utils.register_class(SOURCEOPS_PT_MainPanel)


def unregister():
    bpy.utils.unregister_class(SOURCEOPS_PT_MainPanel)
    bpy.utils.unregister_class(SOURCEOPS_UL_MapList)
    bpy.utils.unregister_class(SOURCEOPS_UL_EventList)
    bpy.utils.unregister_class(SOURCEOPS_UL_SequenceList)
    bpy.utils.unregister_class(SOURCEOPS_UL_SkinList)
    bpy.utils.unregister_class(SOURCEOPS_UL_MaterialFolderList)
    bpy.utils.unregister_class(SOURCEOPS_UL_ModelList)
    bpy.utils.unregister_class(SOURCEOPS_UL_GameList)
