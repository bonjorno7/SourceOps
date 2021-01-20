import bpy
from .. utils import common


class SOURCEOPS_OT_ListOperator(bpy.types.Operator):
    bl_idname = 'sourceops.list_operator'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    bl_label = 'List Operator'

    @classmethod
    def description(cls, context, properties):
        action = properties.mode.split('_')
        item = properties.item.replace('_', ' ')

        text = f'{action[0]} {item[:-1]}'
        if len(action) > 1:
            text = f'{text} {action[1]}'

        return text.capitalize()

    mode: bpy.props.EnumProperty(
        name='Mode',
        description='What to do to the item',
        items=[
            ('ADD', 'Add', 'Add an item'),
            ('REMOVE', 'Remove', 'Remove an item'),
            ('COPY', 'Copy', 'Copy an item'),
            ('MOVE_UP', 'Move Up', 'Move an item up'),
            ('MOVE_DOWN', 'Move Down', 'Move an item down'),
        ],
    )

    item: bpy.props.EnumProperty(
        name='Type',
        description='Which list to deal with',
        items=[
            ('GAMES', 'Games', 'Operate on games'),
            ('MODELS', 'Models', 'Operate on models'),
            ('MATERIAL_FOLDERS', 'Material Folders', 'Operate on material folders'),
            ('SKINS', 'Skins', 'Operate on skins'),
            ('SEQUENCES', 'Sequences', 'Operate on sequences'),
            ('EVENTS', 'Events', 'Operate on events'),
            ('ATTACHMENTS', 'Attachments', 'Operate on attachments'),
            ('MAPS', 'Maps', 'Operate on maps'),
        ],
    )

    def add(self, parent, items, index):
        items.add()
        index = len(items) - 1
        return index

    def remove(self, parent, items, index):
        items.remove(index)
        index = min(
            max(0, index - 1),
            max(0, len(items) - 1),
        )
        return index

    def copy(self, parent, items, index):
        items.add()
        old, new = items[index], items[-1]
        for key, value in old.items():
            new[key] = value
        index = len(items) - 1
        return index

    def move(self, parent, items, index, direction):
        neighbor = max(0, index + direction)
        items.move(neighbor, index)
        length = max(0, len(items) - 1)
        index = max(0, min(neighbor, length))
        return index

    def move_up(self, parent, items, index):
        return self.move(parent, items, index, -1)

    def move_down(self, parent, items, index):
        return self.move(parent, items, index, 1)

    def invoke(self, context, event):
        prefs = common.get_prefs(context)
        game = common.get_game(prefs)
        sourceops = common.get_globals(context)
        model = common.get_model(sourceops)
        sequence = common.get_sequence(model)

        mode_dict = {
            'ADD': self.add,
            'REMOVE': self.remove,
            'COPY': self.copy,
            'MOVE_UP': self.move_up,
            'MOVE_DOWN': self.move_down,
        }

        item_dict = {
            'GAMES': (prefs, 'game_items', 'game_index'),
            'MODELS': (sourceops, 'model_items', 'model_index'),
            'MATERIAL_FOLDERS': (model, 'material_folder_items', 'material_folder_index'),
            'SKINS': (model, 'skin_items', 'skin_index'),
            'SEQUENCES': (model, 'sequence_items', 'sequence_index'),
            'EVENTS': (sequence, 'event_items', 'event_index'),
            'ATTACHMENTS': (model, 'attachment_items', 'attachment_index'),
            'MAPS': (sourceops, 'map_items', 'map_index'),
        }

        function = mode_dict[self.mode]
        parent, items_name, index_name = item_dict[self.item]

        if self.mode == 'ADD' and not parent:
            return {'CANCELLED'}

        if self.mode != 'ADD' and (not parent or not getattr(parent, items_name)):
            return {'CANCELLED'}

        items = getattr(parent, items_name)
        index = getattr(parent, index_name)

        index = function(parent, items, index)
        setattr(parent, index_name, index)

        return {'FINISHED'}
