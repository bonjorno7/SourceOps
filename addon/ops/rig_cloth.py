import bpy
from .. import utils


class SOURCEOPS_OT_RigCloth(bpy.types.Operator):
    '''Add a bone for each vertex, and an object skinned to those bones'''
    bl_options = {'REGISTER', 'UNDO'}
    bl_idname = 'sourceops.rig_cloth'
    bl_label = 'Rig Cloth'

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:

        # Make sure input and output collections are set
        sourceops = utils.common.get_globals(context)
        input_collection = sourceops.simulation_input
        output_collection = sourceops.simulation_output
        return input_collection and output_collection

    def execute(self, context: bpy.types.Context) -> set:

        # Get input and output collections
        sourceops = utils.common.get_globals(context)
        input_collection = sourceops.simulation_input
        output_collection = sourceops.simulation_output

        # Iterate through input objects
        for input_obj in input_collection.all_objects:
            if input_obj.type != 'MESH':
                continue

            # Switch to object mode
            context.view_layer.objects.active = input_obj
            bpy.ops.object.mode_set(mode='OBJECT')

            # Duplicate to output collection
            output_obj = input_obj.copy()
            output_obj.data = input_obj.data.copy()
            output_obj.name = f'Rigged {input_obj.name}'
            output_obj.data.name = output_obj.name
            output_collection.objects.link(output_obj)

            # Remove cloth modifiers
            for mod in output_obj.modifiers[:]:
                if mod.type == 'CLOTH':
                    output_obj.modifiers.remove(mod)

            # Clear any existing vertex groups
            output_obj.vertex_groups.clear()

            # Add vertex group for each vertex
            for vertex in output_obj.data.vertices:
                group = output_obj.vertex_groups.new(name=str(vertex.index))
                group.add(index=[vertex.index], weight=1.0, type='REPLACE')

            # Create armature
            name = f'{input_obj.name} Armature'
            arm_data = bpy.data.armatures.new(name=name)
            arm_obj = bpy.data.objects.new(name=name, object_data=arm_data)
            output_collection.objects.link(arm_obj)
            arm_obj.show_in_front = True

            # Add armature modifier
            mod = output_obj.modifiers.new('Armature', 'ARMATURE')
            mod.use_vertex_groups = True
            mod.object = arm_obj

            # Switch to armature edit mode
            context.view_layer.objects.active = arm_obj
            bpy.ops.object.mode_set(mode='EDIT')

            # Add bone for each vertex
            for vertex in output_obj.data.vertices:
                bone = arm_data.edit_bones.new(str(vertex.index))

            # Switch to armature pose mode
            context.view_layer.objects.active = arm_obj
            bpy.ops.object.mode_set(mode='POSE')

            # Add constraint for each bone vertex pair
            for group, bone in zip(output_obj.vertex_groups, arm_obj.pose.bones):
                constraint = bone.constraints.new('COPY_LOCATION')
                constraint.target = input_obj
                constraint.subtarget = group

            # Switch to object mode
            context.view_layer.objects.active = output_obj
            bpy.ops.object.mode_set(mode='OBJECT')

        # Report to user and finish
        self.report({'INFO'}, f'Rigged Cloth')
        return {'FINISHED'}
