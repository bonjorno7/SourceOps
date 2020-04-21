import bpy
from .. utils import common


class SOURCEOPS_OT_MoveItem(bpy.types.Operator):
    bl_idname = 'sourceops.move_item'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    bl_label = 'Move Item'
    bl_description = 'Move an item in the list'

    item: bpy.props.EnumProperty(
        name='Item Type',
        description='What kind of item to move',
        items=[
            ('GAMES', 'Game', 'Move a game'),
            ('MODELS', 'Model', 'Move a model'),
            ('MATERIAL_FOLDERS', 'Material Folder', 'Move a material folder'),
            ('SKINS', 'Skin', 'Move a skin'),
            ('SEQUENCES', 'Sequence', 'Move a sequence'),
            ('EVENTS', 'Event', 'Move an event'),
        ],
    )

    direction: bpy.props.EnumProperty(
        name='Direction',
        description='What direction to move the item',
        items=[
            ('UP', 'Up', 'Move the item up'),
            ('DOWN', 'Down', 'Move the item down'),
        ],
    )

    def invoke(self, context, event):
        sourceops = common.get_globals(context)
        game = common.get_game(sourceops)
        model = common.get_model(sourceops)
        sequence = common.get_sequence(model)

        if self.item == 'GAMES' and sourceops:
            direction = 1 if self.direction == 'DOWN' else -1
            neighbor = max(0, sourceops.game_index + direction)
            sourceops.game_items.move(neighbor, sourceops.game_index)
            length = max(0, len(sourceops.game_items) - 1)
            sourceops.game_index = max(0, min(neighbor, length))

        elif self.item == 'MODELS' and sourceops:
            direction = 1 if self.direction == 'DOWN' else -1
            neighbor = max(0, sourceops.model_index + direction)
            sourceops.model_items.move(neighbor, sourceops.model_index)
            length = max(0, len(sourceops.model_items) - 1)
            sourceops.model_index = max(0, min(neighbor, length))

        elif self.item == 'MATERIAL_FOLDERS' and model:
            direction = 1 if self.direction == 'DOWN' else -1
            neighbor = max(0, model.material_folder_index + direction)
            model.material_folder_items.move(neighbor, model.material_folder_index)
            length = max(0, len(model.material_folder_items) - 1)
            model.material_folder_index = max(0, min(neighbor, length))

        elif self.item == 'SKINS' and model:
            direction = 1 if self.direction == 'DOWN' else -1
            neighbor = max(0, model.skin_index + direction)
            model.skin_items.move(neighbor, model.skin_index)
            length = max(0, len(model.skin_items) - 1)
            model.skin_index = max(0, min(neighbor, length))

        elif self.item == 'SEQUENCES' and model:
            direction = 1 if self.direction == 'DOWN' else -1
            neighbor = max(0, model.sequence_index + direction)
            model.sequence_items.move(neighbor, model.sequence_index)
            length = max(0, len(model.sequence_items) - 1)
            model.sequence_index = max(0, min(neighbor, length))

        elif self.item == 'EVENTS' and sequence:
            direction = 1 if self.direction == 'DOWN' else -1
            neighbor = max(0, sequence.event_index + direction)
            sequence.event_items.move(neighbor, sequence.event_index)
            length = max(0, len(sequence.event_items) - 1)
            sequence.event_index = max(0, min(neighbor, length))

        return {'FINISHED'}
