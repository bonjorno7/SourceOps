bl_info = {
    'name': 'SourceOps',
    'author': 'bonjorno7, Almaas, Cabbage McGravel, CryptAlchemy, Gorange, Krystian, RED_EYE, SethTooQuick, Yonder',
    'description': 'A more convenient alternative to Blender Source Tools',
    'blender': (2, 83, 0),
    'version': (0, 7, 6),
    'location': '3D View > Sidebar',
    'category': 'Import-Export',
}


from . import addon


def register():
    addon.register()


def unregister():
    addon.unregister()
