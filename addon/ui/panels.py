import bpy
from .. utils import common
from .. import icons


class SOURCEOPS_PT_MainPanel(bpy.types.Panel):
    bl_idname = 'SOURCEOPS_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SourceOps'
    bl_label = f'SourceOps    -    {common.get_version()}'

    def draw(self, context):
        sourceops = common.get_globals(context)
        game = common.get_game(sourceops)
        model = common.get_model(sourceops)
        material_folder = common.get_material_folder(model)
        skin = common.get_skin(model)
        sequence = common.get_sequence(model)
        event = common.get_event(sequence)
        displacement_props = common.get_displacement_props(sourceops)

        if sourceops:
            box = self.layout.box()
            row = box.row()
            row.scale_x = row.scale_y = 1.5
            row.label(text='Panel')
            row = row.row(align=True)
            row.alignment = 'RIGHT'
            row.prop(sourceops, 'panel', expand=True, icon_only=True)

        if sourceops.panel == 'GAMES' and sourceops:
            box = self.layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Games')

            row = box.row()
            row.template_list('SOURCEOPS_UL_GameList', '', sourceops, 'game_items', sourceops, 'game_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'GAMES')

            if game:
                common.add_prop(box, 'Display Name', game, 'display')
                common.add_prop(box, 'Gameinfo Path', game, 'gameinfo')
                common.add_prop(box, 'Additional Path', game, 'additional')

        elif sourceops.panel == 'MODELS' and sourceops:
            box = self.layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Models')

            row = box.row()
            row.template_list('SOURCEOPS_UL_ModelList', '', sourceops, 'model_items', sourceops, 'model_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'MODELS')

            if model:
                common.add_prop(box, 'Display Name', model, 'display')
                common.add_prop(box, 'Model Name', model, 'name')
                common.add_prop(box, 'Reference', model, 'reference')
                common.add_prop(box, 'Collision', model, 'collision')
                common.add_prop(box, 'Bodygroups', model, 'bodygroups')
                common.add_prop(box, 'Stacking', model, 'stacking')

        elif sourceops.panel == 'MODEL_OPTIONS' and model:
            box = self.layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Model Options')

            common.add_prop(box, 'Surface Property', model, 'surface')
            common.add_prop(box, 'Static Prop', model, 'static')
            common.add_prop(box, 'Has Glass', model, 'glass')

            box = self.layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Transform Options')

            common.add_prop(box, 'Ignore Transforms', model, 'ignore_transforms')
            common.add_prop(box, 'Origin +X', model, 'origin_x')
            common.add_prop(box, 'Origin +Y', model, 'origin_y')
            common.add_prop(box, 'Origin -Z', model, 'origin_z')
            common.add_prop(box, 'Rotation', model, 'rotation')
            common.add_prop(box, 'Scale', model, 'scale')

        elif sourceops.panel == 'TEXTURES' and model:
            box = self.layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Material Folders')

            row = box.row()
            row.template_list('SOURCEOPS_UL_MaterialFolderList', '', model, 'material_folder_items', model, 'material_folder_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'MATERIAL_FOLDERS')

            if material_folder:
                common.add_prop(box, 'Display Name', material_folder, 'display')
                common.add_prop(box, 'Folder Path', material_folder, 'path')

            box = self.layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Skins')

            row = box.row()
            row.template_list('SOURCEOPS_UL_SkinList', '', model, 'skin_items', model, 'skin_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'SKINS')

            if skin:
                common.add_prop(box, 'Display Name', skin, 'display')
                common.add_prop(box, 'VMT Name', skin, 'name')

        elif sourceops.panel == 'SEQUENCES' and model:
            box = self.layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Sequences')

            row = box.row()
            row.template_list('SOURCEOPS_UL_SequenceList', '', model, 'sequence_items', model, 'sequence_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'SEQUENCES')

            if sequence:
                common.add_prop(box, 'Display Name', sequence, 'display')
                common.add_prop(box, 'Sequence Name', sequence, 'name')
                common.add_props(box, 'Framerate Override', sequence, ('override', 'framerate'))
                common.add_prop(box, 'Start Frame', sequence, 'start')
                common.add_prop(box, 'End Frame', sequence, 'end')
                common.add_prop(box, 'Activity', sequence, 'activity')
                common.add_prop(box, 'Weight', sequence, 'weight')
                common.add_prop(box, 'Snap', sequence, 'snap')
                common.add_prop(box, 'Loop', sequence, 'loop')

        elif sourceops.panel == 'EVENTS' and sequence:
            box = self.layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Events')

            row = box.row()
            row.template_list('SOURCEOPS_UL_EventList', '', sequence, 'event_items', sequence, 'event_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'EVENTS')

            if event:
                common.add_prop(box, 'Display Name', event, 'display')
                common.add_prop(box, 'Event Type', event, 'event')
                common.add_prop(box, 'Frame', event, 'frame')
                common.add_prop(box, 'Value', event, 'value')

        if sourceops.panel in {'GAMES', 'MODELS', 'MODEL_OPTIONS', 'TEXTURES', 'SEQUENCES', 'EVENTS'}:
            box = self.layout.box()
            row = box.row()
            row.scale_x = row.scale_y = 1.5
            row.label(text='Export')
            row = row.row(align=True)
            row.alignment = 'RIGHT'

            row.operator('sourceops.export_meshes', text='', icon_value=icons.id('smd'))
            row.operator('sourceops.generate_qc', text='', icon_value=icons.id('qc'))
            row.operator('sourceops.open_qc', text='', icon='TEXT')
            row.operator('sourceops.compile_qc', text='', icon_value=icons.id('mdl'))
            row.operator('sourceops.view_model', text='', icon_value=icons.id('hlmv'))
            row.operator('sourceops.open_log', text='', icon='HELP')

        if sourceops.panel == 'DISPLACEMENTS' and displacement_props:
            box = self.layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Displacements')

            common.add_prop(box, 'Map Path', displacement_props, 'map_path')
            common.add_prop(box, 'Visgroup', displacement_props, 'visgroup')
            common.add_prop(box, 'Collection', displacement_props, 'collection')
            common.add_prop(box, 'Brush Scale', displacement_props, 'brush_scale')
            common.add_prop(box, 'Geometry Scale', displacement_props, 'geometry_scale')
            common.add_prop(box, 'Lightmap Scale', displacement_props, 'lightmap_scale')

            box = self.layout.box()
            row = box.row()
            row.scale_x = row.scale_y = 1.5
            row.label(text='Export')
            row = row.row(align=True)
            row.alignment = 'RIGHT'

            row.operator('sourceops.export_displacements', text='', icon_value=icons.id('smd')) # TODO: Make VMF icon

    def draw_list_buttons(self, layout, item):
        op = layout.operator('sourceops.add_item', text='', icon='ADD')
        op.item = item
        op = layout.operator('sourceops.remove_item', text='', icon='REMOVE')
        op.item = item

        layout.separator()
        op = layout.operator('sourceops.copy_item', text='', icon='DUPLICATE')
        op.item = item
        layout.separator()

        op = layout.operator('sourceops.move_item', text='', icon='TRIA_UP')
        op.item, op.direction = item, 'UP'
        op = layout.operator('sourceops.move_item', text='', icon='TRIA_DOWN')
        op.item, op.direction = item, 'DOWN'
