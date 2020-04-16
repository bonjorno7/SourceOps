import bpy
import copy
from .. utils import common


class SOURCEOPS_OT_CopyItem(bpy.types.Operator):
    bl_idname = 'sourceops.copy_item'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    bl_label = 'Copy Item'
    bl_description = 'Duplicate an item in the list'

    item: bpy.props.EnumProperty(
        name='Item Type',
        description='What kind of item to add',
        items=[
            ('GAMES', 'Game', 'Add a game'),
            ('MODELS', 'Model', 'Add a model'),
            ('MATERIAL_FOLDERS', 'Material Folder', 'Add a material folder'),
            ('SKINS', 'Skin', 'Add a skin'),
            ('SEQUENCES', 'Sequence', 'Add a sequence'),
            ('EVENTS', 'Event', 'Add an event'),
        ],
    )

    def invoke(self, context, event):
        sourceops = common.get_globals(context)
        game = common.get_game(sourceops)
        model = common.get_model(sourceops)
        material_folder = common.get_material_folder(model)
        skin = common.get_skin(model)
        sequence = common.get_sequence(model)
        event = common.get_event(sequence)

        if self.item == 'GAMES' and game:
            sourceops.game_items.add()
            sourceops.game_index = len(sourceops.game_items) - 1
            new_game = common.get_game(sourceops)
            for key, value in game.items():
                new_game[key] = value

        elif self.item == 'MODELS' and model:
            sourceops.model_items.add()
            sourceops.model_index = len(sourceops.model_items) - 1
            new_model = common.get_model(sourceops)
            for key, value in model.items():
                new_model[key] = value

        elif self.item == 'MATERIAL_FOLDERS' and material_folder:
            model.material_folder_items.add()
            model.material_folder_index = len(model.material_folder_items) - 1
            new_material_folder = common.get_material_folder(model)
            for key, value in material_folder.items():
                new_material_folder[key] = value

        elif self.item == 'SKINS' and skin:
            model.skin_items.add()
            model.skin_index = len(model.skin_items) - 1
            new_skin = common.get_skin(model)
            for key, value in skin.items():
                new_skin[key] = value

        elif self.item == 'SEQUENCES' and sequence:
            model.sequence_items.add()
            model.sequence_index = len(model.sequence_items) - 1
            new_sequence = common.get_sequence(model)
            for key, value in sequence.items():
                new_sequence[key] = value

        elif self.item == 'EVENTS' and event:
            sequence.event_items.add()
            sequence.event_index = len(sequence.event_items) - 1
            new_event = common.get_event(sequence)
            for key, value in event.items():
                new_event[key] = value

        return {'FINISHED'}
