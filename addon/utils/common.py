import bpy
import string
import unicodedata
from pathlib import Path


def get_version():
    from ... import bl_info
    return '.'.join(str(n) for n in bl_info['version'])


def get_globals(context):
    try:
        return context.scene.sourceops
    except:
        return None


def get_game(sourceops):
    try:
        return sourceops.game_items[sourceops.game_index]
    except:
        return None


def get_model(sourceops):
    try:
        return sourceops.model_items[sourceops.model_index]
    except:
        return None


def get_material_folder(model):
    try:
        return model.material_folder_items[model.material_folder_index]
    except:
        return None


def get_skin(model):
    try:
        return model.skin_items[model.skin_index]
    except:
        return None


def get_sequence(model):
    try:
        return model.sequence_items[model.sequence_index]
    except:
        return None


def get_event(sequence):
    try:
        return sequence.event_items[sequence.event_index]
    except:
        return None


def get_map(sourceops):
    try:
        return sourceops.map_items[sourceops.map_index]
    except:
        return None


def verify_game(game):
    gameinfo = Path(bpy.path.abspath(game.gameinfo)).resolve()
    studiomdl = gameinfo.parent.parent / 'bin/studiomdl.exe'

    if gameinfo.is_file() and studiomdl.is_file():
        game.gameinfo = str(gameinfo)

        if game.additional:
            additional = Path(bpy.path.abspath(game.additional)).resolve()
            game.additional = str(additional)

        return True
    return False


def split_column(layout):
    col = layout.column()
    col.use_property_split = True
    col.use_property_decorate = False
    return col


filename_chars_valid = '-_.() %s%s' % (string.ascii_letters, string.digits)
filename_chars_replace = ' '
filename_char_limit = 255


def clean_filename(filename, whitelist=filename_chars_valid, replace=filename_chars_replace, char_limit=filename_char_limit):
    for r in replace:
        filename = filename.replace(r, '_')
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()
    cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
    return cleaned_filename[:char_limit]   


def resolve_path(path):
    return Path(bpy.path.abspath(path)).resolve()


def verify_folder(path):
    if not path.is_dir():
        try:
            path.mkdir(parents=True, exist_ok=True)
        except:
            print(f'Failed to create directory: {path}')
    return path


def remove_duplicates(list_with_duplicates):
    return list(dict.fromkeys(list(list_with_duplicates)))
