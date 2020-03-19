bl_info = {
    'name': 'SourceOps',
    'author': 'bonjorno7, RED_EYE, SethTooQuick, Cabbage McGravel',
    'description': 'A more convenient alternative to Blender Source Tools',
    'blender': (2, 80, 0),
    'version': (0, 5, 0, 7),
    'location': '3D View > Sidebar',
    'category': 'Import-Export'
}


from . import addon


def register():
    addon.register()


def unregister():
    addon.unregister()
