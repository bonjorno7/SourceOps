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
    bones = {'Root':0}
    for armature in armatures:
        for bone in armature.data.bones:
            bones[f'{armature.name}.{bone.name}'] = len(bones)

    # Hardcode the version number for now
    smd.write('version 1\n')

    # Open the nodes block
    smd.write('nodes\n')

    # Write the root bone
    smd.write('0 "Root" -1\n')

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

    # Open the skeleton block
    smd.write('skeleton\n')

    # Rest pose
    if kind == 'REFERENCE':

        # Write frame 0
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
                    matrix = bone.parent.matrix_local.inverted() @ bone.matrix_local
                else:
                    matrix = bone.matrix_local

                # Get the location and write it
                l = matrix.to_translation()
                smd.write(f'{l.x:.6f} {l.y:.6f} {l.z:.6f}    ')

                # Get the rotation and write it
                r = matrix.to_euler()
                smd.write(f'{r.x:.6f} {r.y:.6f} {r.z:.6f}\n')

    # Animation
    if kind == 'ANIMATION':

        # Save the scene's current frame
        current = context.scene.frame_current

        # Save the scene's start and end frames
        start = context.scene.frame_start
        end = context.scene.frame_end + 1

        for frame in range(start, end):

            # Set the frame in the scene write it
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
                        matrix = bone.parent.matrix.inverted() @ bone.matrix
                    else:
                        matrix = bone.matrix

                    # Get the location and write it
                    l = matrix.to_translation()
                    smd.write(f'{l.x:.6f} {l.y:.6f} {l.z:.6f}    ')

                    # Get the rotation and write it
                    r = matrix.to_euler()
                    smd.write(f'{r.x:.6f} {r.y:.6f} {r.z:.6f}\n')

        # Restore the frame to the scene
        context.scene.frame_set(current)

    # Close the skeleton block
    smd.write('end\n')

    # Triangles
    if kind == 'REFERENCE':

        # Open the triangles block
        smd.write('triangles\n')

        # Iterate through the objects
        for obj in objects:
            
            # Duplicate the object
            eva = obj.evaluated_get(context.view_layer.depsgraph)

            # Remove armature modifiers
            for modifier in eva.modifiers:
                if modifier.type == 'ARMATURE':
                    eva.modifiers.remove(modifier)

            # Create a mesh with modifiers applied
            mesh = eva.to_mesh()

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

                    # Get the coords from the vertex and apply the object's transformation
                    coords = obj.matrix_local @ mathutils.Vector(vertex.co)
                    smd.write(f'{coords.x} {coords.y} {coords.z}    ')

                    # Get the normal from the loop and apply the object's transformation
                    normal = obj.matrix_local @ mathutils.Vector(loop.normal)
                    smd.write(f'{normal.x} {normal.y} {normal.z}    ')

                    # Get the UV coordinates of the loop from the mesh UV layers
                    if mesh.uv_layers:
                        uv_layers = [layer for layer in mesh.uv_layers if layer.active_render]
                        uv = uv_layers[0].data[loop.index].uv
                    else:
                        uv = [0.0, 0.0]

                    # Write the UV coordinates
                    smd.write(f'{uv[0]} {uv[1]}')

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
                            smd.write(f'  {index} {weight}')

                    # End the vertex with a newline
                    smd.write('\n')

            # Clear split normals
            mesh.free_normals_split()

            # Remove the temporary mesh
            obj.to_mesh_clear()

            # Fix armature modifiers on the object
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE':
                    modifier.show_viewport = False
                    modifier.show_viewport = True

        # Close the triangles block
        smd.write('end\n')

    # Close the SMD file
    smd.close()
