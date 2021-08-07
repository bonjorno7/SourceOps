import bpy
import math


class SOURCEOPS_OT_PoseBoneTransforms(bpy.types.Operator):
    bl_idname = 'sourceops.pose_bone_transforms'
    bl_label = 'Pose Bone Transforms'
    bl_description = 'Copy parent space transforms of the active pose bone to clipboard'
    bl_options = {'REGISTER', 'INTERNAL'}

    type: bpy.props.EnumProperty(
        name='Transform Type',
        items=[
            ('TRANSLATION', 'Translation', ''),
            ('ROTATION', 'Rotation', ''),
        ],
    )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'POSE'

    def execute(self, context: bpy.types.Context) -> set:
        bone = context.active_pose_bone

        if bone is None:
            self.report({'INFO'}, 'No active bone')
            return {'CANCELLED'}

        if bone.parent:
            parent = bone.parent.matrix.inverted_safe()
            matrix = parent @ bone.matrix
        else:
            matrix = bone.matrix

        if self.type == 'ROTATION':
            vector = matrix.to_euler()
            vector = [math.degrees(n) for n in vector]
        else:
            vector = matrix.to_translation().xyz

        string = ' '.join(str(round(n, 6)) for n in vector)
        context.window_manager.clipboard = string

        self.report({'INFO'}, f'{self.type.capitalize()}: {string}')
        return {'FINISHED'}


def menu_func(self, context: bpy.types.Context):
    layout = self.layout
    layout.separator()

    layout.operator('sourceops.pose_bone_transforms', text='Copy Translation for Source').type = 'TRANSLATION'
    layout.operator('sourceops.pose_bone_transforms', text='Copy Rotation for Source').type = 'ROTATION'
