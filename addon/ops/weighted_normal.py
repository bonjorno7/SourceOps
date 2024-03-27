import bpy


class SOURCEOPS_OT_weighted_normal(bpy.types.Operator):
    bl_idname = 'sourceops.weighted_normal'
    bl_label = 'Add Weighted Normal Modifier'
    bl_description = 'Add a weighted normal modifier to the selected objects and remove existing weighted normal modifiers'
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        name='Weighting Mode',
        description='Weighted vertex normal mode to use',
        items=[
            ('FACE_AREA', 'Face Area', 'Generate face area weighted normals'),
            ('CORNER_ANGLE', 'Corner Angle', 'Generate corner angle weighted normals'),
            ('FACE_AREA_WITH_ANGLE', 'Face Area And Angle', 'Generated normals weighted by both face area and angle'),
        ],
        default='FACE_AREA',
    )

    weight: bpy.props.IntProperty(
        name='Weight',
        description='Corrective factor applied to faces’ weights, 50 is neutral, lower values increase weight of weak faces, higher values increase weight of strong faces',
        min=1,
        max=100,
        default=50,
    )

    thresh: bpy.props.FloatProperty(
        name='Threshold',
        description='Threshold value for different weights to be considered equal',
        min=0,
        max=10,
        default=0.01,
    )

    keep_sharp: bpy.props.BoolProperty(
        name='Keep Sharp',
        description='Keep sharp edges as computed for default split normals, instead of setting a single weighted normal for each vertex',
        default=True,
    )

    use_face_influence: bpy.props.BoolProperty(
        name='Face Influence',
        description='Use influence of face for weighting',
        default=False,
    )

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        bpy.ops.object.shade_smooth()

        for obj in context.selected_objects:
            if obj.type == 'MESH':
                if hasattr(obj.data, 'use_auto_smooth'):
                    obj.data.use_auto_smooth = True

                for mod in obj.modifiers[:]:
                    if mod.type == 'WEIGHTED_NORMAL':
                        obj.modifiers.remove(mod)

                mod = obj.modifiers.new('WeightedNormal', 'WEIGHTED_NORMAL')
                mod.mode = self.mode
                mod.weight = self.weight
                mod.thresh = self.thresh
                mod.keep_sharp = self.keep_sharp
                mod.use_face_influence = self.use_face_influence

        return {'FINISHED'}
