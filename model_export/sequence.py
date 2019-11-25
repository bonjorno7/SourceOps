import bpy
from .. import common
from . event import EventProps


class SequenceProps(bpy.types.PropertyGroup):
    """Holds the variables for a sequence"""
    bl_idname = "SOURCEOPS_PG_SequenceProps"

    name: bpy.props.StringProperty(
        name="Sequence Name",
        description="The name of the sequence",
        default="idle",
    )

    start: bpy.props.IntProperty(
        name="Start Frame",
        description="First frame of the sequence",
        default=0,
    )

    end: bpy.props.IntProperty(
        name="End Frame",
        description="Last frame of the sequence",
        default=30,
    )

    activity: bpy.props.StringProperty(
        name="Activity",
        description="The the activity that triggers this sequence to play",
        default="ACT_VM_IDLE",
    )

    weight: bpy.props.IntProperty(
        name="Weight",
        description="Determines the chance this sequence will play compared to other sequences with this activity",
        default=1,
    )

    loop: bpy.props.BoolProperty(
        name="Loop",
        description="Whether the sequence will be looped",
        default=False,
    )

    events: bpy.props.CollectionProperty(type=EventProps)
    event_index: bpy.props.IntProperty(default=0)


class SequenceList(bpy.types.UIList):
    """List of sequences for the model"""
    bl_idname = "SOURCEOPS_UL_SequenceList"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, translate=False)


class AddSequence(bpy.types.Operator):
    """Create a sequence"""
    bl_idname = "sourceops.add_sequence"
    bl_label = "Add Sequence"

    def execute(self, context):
        model = common.get_model(context)
        model.sequences.add()
        model.sequence_index = len(model.sequences) - 1
        return {'FINISHED'}


class RemoveSequence(bpy.types.Operator):
    """Remove the selected sequence"""
    bl_idname = "sourceops.remove_sequence"
    bl_label = "Remove Sequence"

    @classmethod
    def poll(cls, context):
        g = common.get_globals(context)
        return len(g.models) > 0

    def execute(self, context):
        model = common.get_model(context)
        model.sequences.remove(model.sequence_index)
        model.sequence_index = min(
            max(0, model.sequence_index - 1),
            len(model.sequences) - 1
        )
        return {'FINISHED'}


class MoveSequence(bpy.types.Operator):
    """Move the selected sequence up or down in the list"""
    bl_idname = "sourceops.move_sequence"
    bl_label = "Move Sequence"

    direction: bpy.props.EnumProperty(items=(
        ('UP', "Up", "Move the item up"),
        ('DOWN', "Down", "Move the item down"),
    ))

    @classmethod
    def poll(cls, context):
        model = common.get_model(context)
        return len(model.sequences) > 1

    def execute(self, context):
        model = common.get_model(context)
        neighbor = model.sequence_index + (-1 if self.direction == 'UP' else 1)
        model.sequences.move(neighbor, model.sequence_index)
        list_length = len(model.sequences) - 1
        model.sequence_index = max(0, min(neighbor, list_length))
        return {'FINISHED'}


class SequencePanel(bpy.types.Panel):
    """The panel for the model's sequences"""
    bl_idname = "SOURCEOPS_PT_SequencePanel"
    bl_parent_id = "SOURCEOPS_PT_ModelExportPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "SourceOps"
    bl_label = "Sequences"

    @classmethod
    def poll(cls, context):
        return common.get_model(context)

    def draw_header(self, context):
        self.layout.label(icon='SEQUENCE')

    def draw(self, context):
        model = common.get_model(context)
        row = self.layout.row()
        row.template_list("SOURCEOPS_UL_SequenceList", "", model, "sequences", model, "sequence_index", rows=4)
        col = row.column(align=True)
        col.operator("sourceops.add_sequence", text="", icon='ADD')
        col.operator("sourceops.remove_sequence", text="", icon='REMOVE')
        col.separator()
        col.operator("sourceops.move_sequence", text="", icon='TRIA_UP').direction = 'UP'
        col.operator("sourceops.move_sequence", text="", icon='TRIA_DOWN').direction = 'DOWN'

        if model.sequences:
            sequence = model.sequences[model.sequence_index]
            common.add_prop(self.layout, "Start", sequence, "start")
            common.add_prop(self.layout, "End", sequence, "end")
            common.add_prop(self.layout, "Activity", sequence, "activity")
            common.add_prop(self.layout, "Weight", sequence, "weight")
            common.add_prop(self.layout, "Loop", sequence, "loop")
