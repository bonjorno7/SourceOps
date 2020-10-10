import bpy
import json
import pathlib
from .. import utils


def valid_keys(group):
    '''Yield valid keys for this property group, meaning everything except rna_type and bl_idname.'''
    for key in group.bl_rna.properties.keys():
        if key not in {'rna_type', 'bl_idname'}:
            yield key


def pref_prop(group, name):
    '''Call pref_prop_stored but without stored. Used for saving.'''
    pref, prop, stored = pref_prop_stored(group, None, name)
    return pref, prop


def pref_prop_stored(group, storage, name):
    '''Get the the value and property of group[name], as well as the value from storage. Report the reason if it failed.'''
    pref = getattr(group, name, None)
    prop = group.bl_rna.properties.get(name)
    stored = storage.get(name) if storage else None

    if pref is None:
        print(f'SKIPPING {group}["{name}"] because it is NONE')

    elif prop.is_skip_save:
        print(f'SKIPPING {group}["{name}"] because it is SKIP SAVE')

    elif prop.is_readonly and prop.type not in {'POINTER', 'COLLECTION'}:
        print(f'SKIPPING {group}["{name}"] because it is READ ONLY')

    elif invalid_enum_item(group, storage, name, pref, prop, stored):
        print(f'SKIPPING {group}["{name}"] because it is INVALID ENUM ITEM')

    elif storage and stored is None:
        print(f'SKIPPING {group}["{name}"] because it is NOT STORED')

    else:
        return pref, prop, stored

    return None, None, None


def invalid_enum_item(group, storage, name, pref, prop, stored):
    '''Check whether a value is valid for an enum by trying it and catching the exception.'''
    if prop.type == 'ENUM' and storage and stored not in {x.identifier for x in prop.enum_items}:
        try:
            if stored:
                setattr(group, name, stored)

        except:
            return True

        finally:
            if pref:
                setattr(group, name, pref)

    return False


def save_recursive_group(group):
    '''Recursively save a property group.'''
    if group is not None:
        keys = valid_keys(group)
        storage = {k: save_recursive_by_name(group, k) for k in keys}
        return {k: v for k, v in storage.items() if v is not None}


def save_recursive_by_name(group, name):
    '''Save an item from a property group.'''
    pref, prop = pref_prop(group, name)

    if pref is None:
        return None

    elif prop.type == 'POINTER':
        return save_recursive_group(pref)

    elif prop.type == 'COLLECTION':
        return [save_recursive_group(x) for x in pref]

    elif getattr(prop, 'is_array', None):
        return [x for x in pref]

    elif isinstance(pref, (bool, int, float, str)):
        return pref


def load_recursive_group(group, storage):
    '''Recursively load a property group.'''
    for key in valid_keys(group):
        load_recursive_by_name(group, storage, key)


def load_recursive_by_name(group, storage, name):
    '''Load an item from a property group.'''
    pref, prop, stored = pref_prop_stored(group, storage, name)

    if pref is None or stored is None:
        return

    elif prop.type == 'POINTER':
        load_recursive_group(pref, stored)

    elif prop.type == 'COLLECTION':
        try:
            while len(pref) < len(stored):
                pref.add()
            while len(pref) > len(stored):
                pref.remove(0)
            for a, b in zip(pref, stored):
                load_recursive_group(a, b)

        except Exception as exception:
            print(f'SKIPPING {group}["{name}"] because of EXCEPTION: {exception}')

    elif getattr(prop, 'is_array', None):
        try:
            indices = range(len(pref))
            for index, value in zip(indices, stored):
                if pref[index] != value:
                    pref[index] = value

        except Exception as exception:
            print(f'SKIPPING {group}["{name}"] because of EXCEPTION: {exception}')

    elif pref != stored:
        try:
            setattr(group, name, stored)

        except Exception as exception:
            print(f'SKIPPING {group}["{name}"] because of EXCEPTION: {exception}')


def backup(path):
    '''Backup addon preferences to a file.'''
    prefs = utils.common.get_prefs(bpy.context)

    path = bpy.path.abspath(path)
    path = pathlib.Path(path).resolve()

    data = save_recursive_group(prefs)
    datastr = json.dumps(data, indent=1, sort_keys=False)

    try:
        path.write_text(datastr)
    except:
        return {'ERROR'}, f'Failed to open {path}', {'CANCELLED'}

    return {'INFO'}, f'Saved "{path}"', {'FINISHED'}


def restore(path):
    '''Restore addon preferences from a file.'''
    prefs = utils.common.get_prefs(bpy.context)

    path = bpy.path.abspath(path)
    path = pathlib.Path(path).resolve()

    try:
        datastr = path.read_text()
    except:
        return {'ERROR'}, f'Failed to open {path}', {'CANCELLED'}

    data = json.loads(datastr)
    load_recursive_group(prefs, data)

    return {'INFO'}, f'Loaded "{path}"', {'FINISHED'}


def filepath():
    '''Get the default path to the preference backup file.'''
    user = bpy.utils.resource_path('USER')
    path = pathlib.Path(user).resolve()

    path = path.joinpath('scripts', 'presets', 'sourceops', 'prefs.json')
    path.parent.mkdir(parents=True, exist_ok=True)

    return str(path)
