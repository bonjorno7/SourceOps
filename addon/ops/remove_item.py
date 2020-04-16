import bpy
from .. utils import common


class SOURCEOPS_OT_RemoveItem(bpy.types.Operator):
    bl_idname = 'sourceops.remove_item'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    bl_label = 'Remove Item'
    bl_description = 'Remove an item from the list'

    item: bpy.props.EnumProperty(
        name='Item Type',
        description='What kind of item to remove',
        items=[
            ('GAMES', 'Game', 'Remove a game'),
            ('MODELS', 'Model', 'Remove a model'),
            ('MATERIAL_FOLDERS', 'Material Folder', 'Remove a material folder'),
            ('SKINS', 'Skins', 'Remove a skin'),
            ('SEQUENCES', 'Sequence', 'Remove a sequence'),
            ('EVENTS', 'Event', 'Remove an event'),
        ],
    )

    def invoke(self, context, event):
        sourceops = common.get_globals(context)
        game = common.get_game(sourceops)
        model = common.get_model(sourceops)
        sequence = common.get_sequence(model)

        if self.item == 'GAMES' and sourceops:
            sourceops.game_items.remove(sourceops.game_index)
            sourceops.game_index = min(
                max(0, sourceops.game_index - 1),
                max(0, len(sourceops.game_items) - 1)
            )

        elif self.item == 'MODELS' and sourceops:
            sourceops.model_items.remove(sourceops.model_index)
            sourceops.model_index = min(
                max(0, sourceops.model_index - 1),
                max(0, len(sourceops.model_items) - 1)
            )

        elif self.item == 'MATERIAL_FOLDERS' and model:
            model.material_folder_items.remove(model.material_folder_index)
            model.material_folder_index = min(
                max(0, model.material_folder_index - 1),
                max(0, len(model.material_folder_items) - 1)
            )

        elif self.item == 'SKINS' and model:
            model.skin_items.remove(model.skin_index)
            model.skin_index = min(
                max(0, model.skin_index - 1),
                max(0, len(model.skin_items) - 1)
            )

        elif self.item == 'SEQUENCES' and model:
            model.sequence_items.remove(model.sequence_index)
            model.sequence_index = min(
                max(0, model.sequence_index - 1),
                max(0, len(model.sequence_items) - 1)
            )

        elif self.item == 'EVENTS' and sequence:
            sequence.event_items.remove(sequence.event_index)
            sequence.event_index = min(
                max(0, sequence.event_index - 1),
                max(0, len(sequence.event_items) - 1)
            )

        return {'FINISHED'}
