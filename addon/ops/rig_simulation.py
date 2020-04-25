import bpy
from .. import utils


class SOURCEOPS_OT_RigSimulation(bpy.types.Operator):
    '''Duplicate rigid body objects from a collection and rig the copies, then make the bones follow the rigid bodies'''
    bl_options = {'REGISTER', 'UNDO'}
    bl_idname = 'sourceops.rig_simulation'
    bl_label = 'Rig Simulation'

    @classmethod
    def poll(cls, context):

        # Make sure input and output collections are set
        sourceops = utils.common.get_globals(context)
        input_collection = sourceops.simulation_input
        output_collection = sourceops.simulation_output
        return input_collection and output_collection

    def execute(self, context):

        # Switch to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Get input and output collections
        sourceops = utils.common.get_globals(context)
        input_collection = sourceops.simulation_input
        output_collection = sourceops.simulation_output

        # Iterate through output objects
        for output_obj in output_collection.all_objects:
            if output_obj.type not in {'MESH', 'ARMATURE'}:
                continue

            # Store object type and data
            obj_type = output_obj.type
            obj_data = output_obj.data

            # Remove object
            bpy.data.objects.remove(output_obj)

            # Remove data
            if obj_type == 'MESH':
                bpy.data.meshes.remove(obj_data)
            elif obj_type == 'ARMATURE':
                bpy.data.armatures.remove(obj_data)

        # Create armature
        name = f'{output_collection.name} Armature'
        arm_data = bpy.data.armatures.new(name=name)
        arm_obj = bpy.data.objects.new(name=name, object_data=arm_data)
        output_collection.objects.link(arm_obj)
        arm_obj.show_in_front = True

        # Iterate through input objects
        for input_obj in input_collection.all_objects:
            if input_obj.type != 'MESH':
                continue

            # Duplicate to output collection
            output_obj = input_obj.copy()
            output_obj.data = input_obj.data.copy()
            output_obj.name = f'Rigged {input_obj.name}'
            output_obj.data.name = output_obj.name
            output_collection.objects.link(output_obj)

            # Reset transforms
            output_obj.location = (0, 0, 0)
            output_obj.rotation_euler = (0, 0, 0)
            output_obj.scale = (1, 1, 1)

            # Remove rigid body properties
            if output_obj.rigid_body:
                context.view_layer.objects.active = output_obj
                bpy.ops.rigidbody.object_remove()

            # Add vertex group
            output_obj.vertex_groups.clear()
            group = output_obj.vertex_groups.new(name=output_obj.name)
            indices = list(range(len(output_obj.data.vertices)))
            group.add(index=indices, weight=1.0, type='REPLACE')

            # Add armature modifier
            mod = output_obj.modifiers.new('Armature', 'ARMATURE')
            mod.use_vertex_groups = True
            mod.object = arm_obj

        # Switch to armature edit mode
        context.view_layer.objects.active = arm_obj
        bpy.ops.object.mode_set(mode='EDIT')

        # Iterate through output objects
        for output_obj in output_collection.all_objects:
            if output_obj.type != 'MESH':
                continue

            # Add bone
            bone = arm_data.edit_bones.new(output_obj.name)
            bone.tail.z = output_obj.dimensions[2]

        # Switch to armature pose mode
        context.view_layer.objects.active = arm_obj
        bpy.ops.object.mode_set(mode='POSE')

        # Iterate through bones
        for bone in arm_obj.pose.bones:

            # Add bone constraint
            constraint = bone.constraints.new('CHILD_OF')
            name = bone.name.replace('Rigged ', '', 1)
            constraint.target = bpy.data.objects[name]

        # Switch to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Report to user and finish
        self.report({'INFO'}, f'Rigged Simulation')
        return {'FINISHED'}
