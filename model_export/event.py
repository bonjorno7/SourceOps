import bpy
from .. import common


class EventProps(bpy.types.PropertyGroup):
    """Holds the variables for an event"""
    bl_idname = "SOURCEOPS_PG_EventProps"

    name: bpy.props.StringProperty(
        name="Name",
        description="Name of the event, just so you can identify it more easily, otherwise unused",
        default="event"
    )

    event: bpy.props.StringProperty(
        name="Event",
        description="The type of the event",
        default="AE_CL_PLAYSOUND",
    )

    frame: bpy.props.IntProperty(
        name="Frame",
        description="The frame of the sequence at which the event should start",
        default=0,
    )

    value: bpy.props.StringProperty(
        name="Value",
        description="The value for the event",
        default="Weapon_Shotgun.Single",
    )


class EventList(bpy.types.UIList):
    """List of events for the sequence"""
    bl_idname = "SOURCEOPS_UL_EventList"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, translate=False)


class AddEvent(bpy.types.Operator):
    """Create an event"""
    bl_idname = "sourceops.add_event"
    bl_label = "Add Event"

    def execute(self, context):
        sequence = common.get_sequence(context)
        sequence.events.add()
        sequence.event_index = len(sequence.events) - 1
        return {'FINISHED'}


class RemoveEvent(bpy.types.Operator):
    """Remove the selected event"""
    bl_idname = "sourceops.remove_event"
    bl_label = "Remove Event"

    @classmethod
    def poll(cls, context):
        sequence = common.get_sequence(context)
        return len(sequence.events) > 0

    def execute(self, context):
        sequence = common.get_sequence(context)
        sequence.events.remove(sequence.event_index)
        sequence.event_index = min(
            max(0, sequence.event_index - 1),
            len(sequence.events) - 1
        )
        return {'FINISHED'}


class MoveEvent(bpy.types.Operator):
    """Move the selected event up or down in the list"""
    bl_idname = "sourceops.move_event"
    bl_label = "Move Event"

    direction: bpy.props.EnumProperty(items=(
        ('UP', "Up", "Move the item up"),
        ('DOWN', "Down", "Move the item down"),
    ))

    @classmethod
    def poll(cls, context):
        sequence = common.get_sequence(context)
        return len(sequence.events) > 1

    def execute(self, context):
        sequence = common.get_sequence(context)
        neighbor = sequence.event_index + (-1 if self.direction == 'UP' else 1)
        sequence.events.move(neighbor, sequence.event_index)
        list_length = len(sequence.events) - 1
        sequence.event_index = max(0, min(neighbor, list_length))
        return {'FINISHED'}


class EventPanel(bpy.types.Panel):
    """The panel for the sequence's events"""
    bl_idname = "SOURCEOPS_PT_EventPanel"
    bl_parent_id = "SOURCEOPS_PT_SequencePanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "SourceOps"
    bl_label = "Events"

    @classmethod
    def poll(cls, context):
        return common.get_sequence(context)

    def draw_header(self, context):
        self.layout.label(icon='ACTION')

    def draw(self, context):
        sequence = common.get_sequence(context)
        row = self.layout.row()
        row.template_list("SOURCEOPS_UL_EventList", "", sequence, "events", sequence, "event_index", rows=4)

        col = row.column(align=True)
        col.operator("sourceops.add_event", text="", icon='ADD')
        col.operator("sourceops.remove_event", text="", icon='REMOVE')
        col.separator()
        col.operator("sourceops.move_event", text="", icon='TRIA_UP').direction = 'UP'
        col.operator("sourceops.move_event", text="", icon='TRIA_DOWN').direction = 'DOWN'

        if sequence.events:
            event = sequence.events[sequence.event_index]
            common.add_prop(self.layout, "Event", event, "event")
            common.add_prop(self.layout, "Frame", event, "frame")
            common.add_prop(self.layout, "Value", event, "value")
