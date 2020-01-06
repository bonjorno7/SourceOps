import os
import bmesh
import mathutils


def export_smd(context, path, objects, armatures, kind):
    '''Export objects to an SMD file'''

    # Try to open the file
    try:

        # Make sure the folder exists
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        # Open the SMD file
        smd = open(path, 'w')
        print(f'Exporting to {path}')

    # Except the error
    except:

        # Inform the user it failed and exit
        print(f'Failed to export {path}')
        return

    # Filter objects so only meshes remain
    objects = [obj for obj in objects if obj.type == 'MESH']

    # Filter armatures just in case
    armatures = [arm for arm in armatures if arm.type == 'ARMATURE']

    # Dictionary for finding bone indices by name
    bones = {'ImplicitRoot':0}
    for armature in armatures:
        for bone in armature.data.bones:
            bones[f'{armature.name}.{bone.name}'] = len(bones)

    # Hardcode the version number for now
    smd.write('version 1\n')

    # Open the nodes block
    smd.write('nodes\n')

    # Write the root bone
    smd.write('0 "ImplicitRoot" -1\n')

    # Iterate through the armatures and bones
    for armature in armatures:
        for bone in armature.data.bones:

            # Get the index and write it
            index = bones[f'{armature.name}.{bone.name}']
            smd.write(f'{index} ')

            # Get the name and write it
            name = bone.name
            smd.write(f'"{name}" ')

            # Get the parent
            if bone.parent:
                parent = bones[f'{armature.name}.{bone.parent.name}']
            else:
                parent = -1

            # Write the parent
            smd.write(f'{parent}\n')

    # Close the nodes block
    smd.write('end\n')

    # Save the scene's current frame
    current = context.scene.frame_current

    # Open the skeleton block
    smd.write('skeleton\n')

    # Rest pose
    if kind == 'REFERENCE':

        # Go to frame 0 and write it
        context.scene.frame_set(0)
        smd.write('time 0\n')

        # Write the root bone
        smd.write(f'{0}    {0.0:.6f} {0.0:.6f} {0.0:.6f}    {0.0:.6f} {0.0:.6f} {0.0:.6f}\n')

        # Iterate through the armatures and bones
        for armature in armatures:
            for bone in armature.data.bones:

                # Get the index and write it
                index = bones[f'{armature.name}.{bone.name}']
                smd.write(f'{index}    ')

                # Get the matrix
                if bone.parent:
                    matrix = bone.parent.matrix_local.inverted_safe() @ bone.matrix_local
                else:
                    matrix = armature.matrix_world @ bone.matrix_local

                # Get the translation and write it
                t = matrix.to_translation()
                smd.write(f'{t.x:.6f} {t.y:.6f} {t.z:.6f}    ')

                # Get the rotation and write it
                r = matrix.to_euler()
                smd.write(f'{r.x:.6f} {r.y:.6f} {r.z:.6f}\n')

    # Animation
    if kind == 'ANIMATION':

        # Save the scene's start and end frames
        start = context.scene.frame_start
        end = context.scene.frame_end + 1

        for frame in range(start, end):

            # Set the frame in the scene and write it
            context.scene.frame_set(frame)
            smd.write(f'time {frame}\n')

            # Write the root bone
            smd.write(f'{0}    {0.0:.6f} {0.0:.6f} {0.0:.6f}    {0.0:.6f} {0.0:.6f} {0.0:.6f}\n')

            # Iterate through the armatures and bones
            for armature in armatures:
                for bone in armature.pose.bones:

                    # Get the index and write it
                    index = bones[f'{armature.name}.{bone.name}']
                    smd.write(f'{index}    ')

                    # Get the matrix
                    if bone.parent:
                        matrix = bone.parent.matrix.inverted_safe() @ bone.matrix
                    else:
                        matrix = armature.matrix_world @ bone.matrix

                    # Get the translation and write it
                    t = matrix.to_translation()
                    smd.write(f'{t.x:.6f} {t.y:.6f} {t.z:.6f}    ')

                    # Get the rotation and write it
                    r = matrix.to_euler()
                    smd.write(f'{r.x:.6f} {r.y:.6f} {r.z:.6f}\n')

    # Close the skeleton block
    smd.write('end\n')

    # Triangles
    if kind == 'REFERENCE':

        # Open the triangles block
        smd.write('triangles\n')

        # Iterate through the objects
        for obj in objects:

            # Temporarily disable armature modifiers
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE':
                    modifier.show_viewport = False

            # Duplicate the object
            eva = obj.evaluated_get(context.view_layer.depsgraph)

            # Create a mesh with modifiers applied
            mesh = eva.to_mesh()

            # And apply the object's world space transformation
            mesh.transform(obj.matrix_world)

            # Triangulate the mesh
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            bm.to_mesh(mesh)
            bm.free()

            # Calculate split normals
            mesh.calc_normals_split()

            # Iterate through the polygons
            for poly in mesh.polygons:

                # Get the blender material
                if poly.material_index < len(obj.material_slots):
                    material = obj.material_slots[poly.material_index].material
                else:
                    material = None

                # Get the material's name
                if material:
                    material = material.name.replace('\\', '/')
                else:
                    material = 'no_material'

                # Write the material
                smd.write(f'{material}\n')

                # Iterate through the loops
                for loop in [mesh.loops[i] for i in poly.loop_indices]:

                    # Vertex for convenient access
                    vertex = mesh.vertices[loop.vertex_index]

                    # Hardcode the parent bone to 0 for now and write it
                    parent = 0
                    smd.write(f'{parent}    ')

                    # Get the coords from the vertex
                    coords = vertex.co
                    smd.write(f'{coords.x:.6f} {coords.y:.6f} {coords.z:.6f}    ')

                    # Get the normal from the loop
                    normal = loop.normal
                    smd.write(f'{normal.x:.6f} {normal.y:.6f} {normal.z:.6f}    ')

                    # Get the UV coordinates of the loop from the mesh UV layers
                    if mesh.uv_layers:
                        uv_layers = [layer for layer in mesh.uv_layers if layer.active_render]
                        uv = uv_layers[0].data[loop.index].uv
                    else:
                        uv = [0.0, 0.0]

                    # Write the UV coordinates
                    smd.write(f'{uv[0]:.6f} {uv[1]:.6f}')

                    # Get this object's armature
                    armature = obj.find_armature()
                    if armature:

                        # Write the amount of vertex groups
                        smd.write(f'    {len(vertex.groups)}  ')

                        # Iterate through the groups this vertex is in
                        for group in vertex.groups:

                            # Get the index and weight
                            index = bones[f'{armature.name}.{obj.vertex_groups[group.group].name}']
                            weight = group.weight

                            # Write the index and weight
                            smd.write(f'  {index} {weight:.6f}')

                    # End the vertex with a newline
                    smd.write('\n')

            # Don't bother clearing the split normals, just remove the temporary mesh
            obj.to_mesh_clear()

            # Restore armature modifiers
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE':
                    modifier.show_viewport = True

        # Close the triangles block
        smd.write('end\n')

    # Restore the frame to the scene
    context.scene.frame_set(current)

    # Close the SMD file
    smd.close()
