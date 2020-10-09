import bpy
import bmesh
import mathutils
import typing
from .. pyvmf import pyvmf


def get_levels_and_width(obj: bpy.types.Object):
    '''Get the subdivision levels of an object.'''

    # Declare levels
    levels = -1

    # Find appropriate modifier and get levels
    for mod in obj.modifiers:

        # Multires is supported
        if mod.type == 'MULTIRES':
            levels = mod.total_levels
            break

        # Subsurf is supported
        elif mod.type == 'SUBSURF':
            levels = mod.levels
            break

    # Calculate width from levels
    width = 2 ** levels

    # Return levels and width
    return levels, width


def setup_face_maps(obj: bpy.types.Object):
    '''Make a face map for every face of an object.'''

    # Removing existing face maps
    obj.face_maps.clear()

    # Declare face maps
    face_maps = []

    # Create face map for every face
    for polygon in obj.data.polygons:
        face_map = obj.face_maps.new()
        face_map.add([polygon.index])
        face_maps.append(face_map)

    # Return face maps
    return face_maps


def setup_subd_mod(obj: bpy.types.Object, levels: int):
    '''Add a subdivision surface modifier to an object.'''

    # Remove existing modifiers
    obj.modifiers.clear()

    # Create subsurf modifier
    mod = obj.modifiers.new('Subdivision', 'SUBSURF')

    # Set type and levels
    mod.subdivision_type = 'SIMPLE'
    mod.levels = levels

    # Return subsurf modifier
    return mod


def setup_uv_layer(obj: bpy.types.Object):
    '''Add a reset UV layer to an object.'''

    # Remove existing UV layers
    for uv_layer in obj.data.uv_layers[:]:
        obj.data.uv_layers.remove(uv_layer)

    # Create new UV layer
    uv_layer = obj.data.uv_layers.new()

    # Return UV layer
    return uv_layer


def convert_object(settings: typing.Any, obj: bpy.types.Object):
    '''Convert single object to solids for VMF export.'''

    # Make sure object is mesh
    if obj.type != 'MESH':
        print(f'Skipping {obj.name} because it is not a mesh')
        return []

    # Get levels and width
    levels, width = get_levels_and_width(obj)

    # Make sure multires or subsurf mod is setup correctly
    if levels == -1:
        print('No multires or subsurf modifier found')
        return []
    elif not (2 <= levels <= 4):
        print('Subdivision levels must be 2, 3, or 4')
        return []

    # Duplicate object and mesh
    obj_subd = obj.copy()
    obj_subd.data = obj.data.copy()

    # Setup new UV layer, face maps, and subsurf modifier
    uv_layer = setup_uv_layer(obj_subd)
    face_maps = setup_face_maps(obj_subd)
    mod_subd = setup_subd_mod(obj_subd, levels)

    # Get evaluated dependency graph
    depsgraph = bpy.context.evaluated_depsgraph_get()

    # Create bmesh from subdivided object
    bm_subd = bmesh.new()
    bm_subd.from_object(obj_subd, depsgraph)

    # Get uv layer and face map layer from subd bmesh
    uv_subd = bm_subd.loops.layers.uv.verify()
    fm_subd = bm_subd.faces.layers.face_map.verify()

    # Create bmesh from sculpted object
    bm_mres = bmesh.new()
    bm_mres.from_object(obj, depsgraph)

    # Setup displacements list
    displacements = [{
        'levels': levels,
        'corners': [None for i in range(8)],
        'normals': [[None for x in range(width + 1)] for y in range(width + 1)],
        'lengths': [[None for x in range(width + 1)] for y in range(width + 1)],
    } for face_map in face_maps]

    # Iterate through subd and mres faces
    for face_subd, face_mres in zip(bm_subd.faces, bm_mres.faces):

        # Get index for this displacement
        z = face_subd[fm_subd]

        # Iterate through loops of each subd and mres face
        for loop_subd, loop_mres in zip(face_subd.loops, face_mres.loops):

            # Get row and column for this point
            uv = loop_subd[uv_subd].uv
            y = round(uv[1] * width)
            x = round(uv[0] * width)

            # Get verts for these loops
            vert_subd = loop_subd.vert
            vert_mres = loop_mres.vert

            # Calculate and write data for this point
            vector = vert_mres.co - vert_subd.co
            data = displacements[z]['normals'][y][x] = vector.normalized()
            data = displacements[z]['lengths'][y][x] = vector.length

            # If this is a corner, store its position
            if x == 0 and y == 0:
                displacements[z]['corners'][0] = vert_subd.co.copy()
                displacements[z]['corners'][4] = vert_subd.co - face_subd.normal * 8
            elif x == width and y == 0:
                displacements[z]['corners'][1] = vert_subd.co.copy()
                displacements[z]['corners'][5] = vert_subd.co - face_subd.normal * 8
            elif x == width and y == width:
                displacements[z]['corners'][2] = vert_subd.co.copy()
                displacements[z]['corners'][6] = vert_subd.co - face_subd.normal * 8
            elif x == 0 and y == width:
                displacements[z]['corners'][3] = vert_subd.co.copy()
                displacements[z]['corners'][7] = vert_subd.co - face_subd.normal * 8

    # Setup solids list
    solids = []

    # Iterate through displacements
    for displacement in displacements:

        # Get brush corners
        v1, v2, v3, v4, v5, v6, v7, v8 = displacement['corners']

        # Create brush sides
        f1 = pyvmf.Side(dic={'plane': f'({v1.x} {v1.y} {v1.z}) ({v3.x} {v3.y} {v3.z}) ({v2.x} {v2.y} {v2.z})'}) # Top
        f2 = pyvmf.Side(dic={'plane': f'({v7.x} {v7.y} {v7.z}) ({v5.x} {v5.y} {v5.z}) ({v6.x} {v6.y} {v6.z})'}) # Bottom
        f3 = pyvmf.Side(dic={'plane': f'({v4.x} {v4.y} {v4.z}) ({v7.x} {v7.y} {v7.z}) ({v3.x} {v3.y} {v3.z})'}) # Front
        f4 = pyvmf.Side(dic={'plane': f'({v6.x} {v6.y} {v6.z}) ({v1.x} {v1.y} {v1.z}) ({v2.x} {v2.y} {v2.z})'}) # Back
        f5 = pyvmf.Side(dic={'plane': f'({v3.x} {v3.y} {v3.z}) ({v6.x} {v6.y} {v6.z}) ({v2.x} {v2.y} {v2.z})'}) # Right
        f6 = pyvmf.Side(dic={'plane': f'({v1.x} {v1.y} {v1.z}) ({v8.x} {v8.y} {v8.z}) ({v4.x} {v4.y} {v4.z})'}) # Left

        # Set texture, lightmap scale, and material for top face
        f1.uaxis.scale = settings.texture_scale
        f1.vaxis.scale = settings.texture_scale
        f1.lightmapscale = settings.lightmap_scale
        f1.material = 'DEV/DEV_BLENDMEASURE' # displacement.material

        # Prepare dispinfo dictionary
        power = displacement['levels']
        startposition = f'[{v1.x} {v1.y} {v1.z}]'
        dic = {'power': power, 'startposition': startposition}

        # Prepare dispinfo children
        normals = pyvmf.Child('normals', {})
        distances = pyvmf.Child('distances', {})
        children = [normals, distances]

        # Populate dispinfo normals
        for index, row in enumerate(displacement['normals']):
            normals.dic[f'row{index}'] = ' '.join(f'{x} {y} {z}' for x, y, z in row)

        # Populate dispinfo distances
        for index, row in enumerate(displacement['lengths']):
            distances.dic[f'row{index}'] = ' '.join(f'{length}' for length in row)

        # Create dispinfo for top face
        f1.dispinfo = pyvmf.DispInfo(dic=dic, children=children)

        # Create solid with sides and append it
        solid = pyvmf.Solid()
        solid.add_sides(f1, f2, f3, f4, f5, f6)
        solid.editor = pyvmf.Editor()
        solids.append(solid)

    # Free bmeshes
    bm_mres.free()
    bm_subd.free()

    # Remove temporary object and mesh, in that order
    mesh_subd = obj_subd.data
    bpy.data.objects.remove(obj_subd)
    bpy.data.meshes.remove(mesh_subd)

    # Return generated solids
    return solids


def convert_objects(settings: typing.Any, objects: typing.List[bpy.types.Object]):
    '''Convert multiple objects to solids for VMF export.'''

    # Setup solid list
    solids = []

    # Iterate through objects
    for obj in objects:
        result = convert_object(settings, obj)
        solids.extend(result)

    # Return generated solids
    return solids
