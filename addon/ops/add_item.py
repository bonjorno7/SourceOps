import bpy
from .. utils import common


class SOURCEOPS_OT_AddItem(bpy.types.Operator):
    bl_idname = 'sourceops.add_item'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    bl_label = 'Add Item'
    bl_description = 'Add an item to the list'

    item: bpy.props.EnumProperty(
        name='Item Type',
        description='What kind of item to add',
        items=[
            ('GAMES', 'Game', 'Add a game'),
            ('MODELS', 'Model', 'Add a model'),
            ('MATERIAL_FOLDERS', 'Material Folder', 'Add a material folder'),
            ('SEQUENCES', 'Sequence', 'Add a sequence'),
            ('EVENTS', 'Event', 'Add an event'),
        ],
    )

    def invoke(self, context, event):
        sourceops = common.get_globals(context)
        game = common.get_game(sourceops)
        model = common.get_model(sourceops)
        sequence = common.get_sequence(model)
        event = common.get_event(sequence)

        if self.item == 'GAMES' and sourceops:
            sourceops.game_items.add()
            sourceops.game_index = len(sourceops.game_items) - 1

        elif self.item == 'MODELS' and sourceops:
            sourceops.model_items.add()
            sourceops.model_index = len(sourceops.model_items) - 1

        elif self.item == 'MATERIAL_FOLDERS' and model:
            model.material_folder_items.add()
            model.material_folder_index = len(model.material_folder_items) - 1

        elif self.item == 'SEQUENCES' and model:
            model.sequence_items.add()
            model.sequence_index = len(model.sequence_items) - 1

        elif self.item == 'EVENTS' and sequence:
            sequence.event_items.add()
            sequence.event_index = len(sequence.event_items) - 1

        return {'FINISHED'}
