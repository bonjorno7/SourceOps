import bpy
from . lists import SOURCEOPS_UL_GameList
from . lists import SOURCEOPS_UL_ModelList
from . lists import SOURCEOPS_UL_MaterialFolderList
from . lists import SOURCEOPS_UL_SkinList
from . lists import SOURCEOPS_UL_SequenceList
from . lists import SOURCEOPS_UL_EventList
from . lists import SOURCEOPS_UL_AttachmentList
from . lists import SOURCEOPS_UL_ParticleList
from . lists import SOURCEOPS_UL_MapList
from . panels import SOURCEOPS_PT_MainPanel

classes = (
    SOURCEOPS_UL_GameList,
    SOURCEOPS_UL_ModelList,
    SOURCEOPS_UL_MaterialFolderList,
    SOURCEOPS_UL_SkinList,
    SOURCEOPS_UL_SequenceList,
    SOURCEOPS_UL_EventList,
    SOURCEOPS_UL_AttachmentList,
    SOURCEOPS_UL_ParticleList,
    SOURCEOPS_UL_MapList,
    SOURCEOPS_PT_MainPanel,
)

class_register, class_unregister = bpy.utils.register_classes_factory(classes)


def register():
    class_register()


def unregister():
    class_unregister()
