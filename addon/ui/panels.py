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
        layout = self.layout

        prefs = common.get_prefs(context)
        game = common.get_game(prefs)
        sourceops = common.get_globals(context)
        model = common.get_model(sourceops)
        material_folder = common.get_material_folder(model)
        skin = common.get_skin(model)
        sequence = common.get_sequence(model)
        event = common.get_event(sequence)
        map_props = common.get_map(sourceops)

        if sourceops:
            box = layout.box()
            row = box.row()
            row.scale_x = row.scale_y = 1.5
            row.label(text='Panel')
            row = row.row(align=True)
            row.alignment = 'RIGHT'
            row.prop(sourceops, 'panel', expand=True, icon_only=True)

        if sourceops.panel == 'GAMES' and prefs:
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Games')

            row = box.row()
            row.template_list('SOURCEOPS_UL_GameList', '', prefs, 'game_items', prefs, 'game_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'GAMES')

            if game:
                col = common.split_column(box)
                col.prop(game, 'name')
                col.prop(game, 'game')
                col.prop(game, 'bin')
                col.prop(game, 'modelsrc')
                col.prop(game, 'models')
                col.prop(game, 'maps')

        elif sourceops.panel == 'MODELS' and sourceops:
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Models')

            row = box.row()
            row.template_list('SOURCEOPS_UL_ModelList', '', sourceops, 'model_items', sourceops, 'model_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'MODELS')

            if model:
                col = common.split_column(box)
                col.prop(model, 'name')
                col.prop(model, 'reference')
                col.prop(model, 'collision')
                col.prop(model, 'bodygroups')
                col.prop(model, 'stacking')

        elif sourceops.panel == 'MODEL_OPTIONS' and model:
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Model Options')

            col = common.split_column(box)
            col.prop(model, 'surface')
            col.prop(model, 'static')
            col.prop(model, 'glass')

            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Transform Options')

            col = common.split_column(box)
            col.prop(model, 'ignore_transforms')

            align = col.column(align=True)
            align.prop(model, 'origin_x', text='Origin X')
            align.prop(model, 'origin_y', text='Y')
            align.prop(model, 'origin_z', text='-Z')

            col.prop(model, 'rotation')
            col.prop(model, 'scale')

        elif sourceops.panel == 'TEXTURES' and model:
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Material Folders')

            row = box.row()
            row.template_list('SOURCEOPS_UL_MaterialFolderList', '', model, 'material_folder_items', model, 'material_folder_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'MATERIAL_FOLDERS')

            if material_folder:
                col = common.split_column(box)
                col.prop(material_folder, 'name')

            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Skins')

            row = box.row()
            row.template_list('SOURCEOPS_UL_SkinList', '', model, 'skin_items', model, 'skin_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'SKINS')

            if skin:
                col = common.split_column(box)
                col.prop(skin, 'name')

        elif sourceops.panel == 'SEQUENCES' and model:
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Sequences')

            row = box.row()
            row.template_list('SOURCEOPS_UL_SequenceList', '', model, 'sequence_items', model, 'sequence_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'SEQUENCES')

            if sequence:
                col = common.split_column(box)
                col.prop(sequence, 'name')

                row = col.row()
                row.prop(sequence, 'framerate')
                row.prop(sequence, 'override', text='')
                
                col.prop(sequence, 'start')
                col.prop(sequence, 'end')
                col.prop(sequence, 'activity')
                col.prop(sequence, 'weight')
                col.prop(sequence, 'snap')
                col.prop(sequence, 'loop')

        elif sourceops.panel == 'EVENTS' and sequence:
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Events')

            row = box.row()
            row.template_list('SOURCEOPS_UL_EventList', '', sequence, 'event_items', sequence, 'event_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'EVENTS')

            if event:
                col = common.split_column(box)
                col.prop(event, 'name')
                col.prop(event, 'event')
                col.prop(event, 'frame')
                col.prop(event, 'value')

        if sourceops.panel in {'GAMES', 'MODELS', 'MODEL_OPTIONS', 'TEXTURES', 'SEQUENCES', 'EVENTS'}:
            box = layout.box()
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
            row.operator('sourceops.export_auto', text='', icon='AUTO')

        if sourceops.panel == 'MAPS' and sourceops:
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Maps')

            row = box.row()
            row.template_list('SOURCEOPS_UL_MapList', '', sourceops, 'map_items', sourceops, 'map_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'MAPS')

            if map_props:
                col = common.split_column(box)
                col.prop(map_props, 'name')
                col.prop(map_props, 'brush_collection')
                col.prop(map_props, 'disp_collection')
                col.prop(map_props, 'uv_scale')
                col.prop(map_props, 'geometry_scale')
                col.prop(map_props, 'texture_scale')
                col.prop(map_props, 'lightmap_scale')
                col.prop(map_props, 'align_to_grid')

            box = layout.box()
            row = box.row()
            row.scale_x = row.scale_y = 1.5
            row.label(text='Export')
            row = row.row(align=True)
            row.alignment = 'RIGHT'

            row.operator('sourceops.export_vmf', text='', icon_value=icons.id('vmf'))

        if sourceops.panel == 'SIMULATION' and sourceops:
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Simulation')

            col = common.split_column(box)
            col.prop(sourceops, 'simulation_input')
            col.prop(sourceops, 'simulation_output')
            box.operator('sourceops.rig_simulation', text='Rig Simulation')

    def draw_list_buttons(self, layout, item):
        op = layout.operator('sourceops.list_operator', text='', icon='ADD')
        op.mode, op.item = 'ADD', item
        op = layout.operator('sourceops.list_operator', text='', icon='REMOVE')
        op.mode, op.item = 'REMOVE', item

        layout.separator()
        op = layout.operator('sourceops.list_operator', text='', icon='DUPLICATE')
        op.mode, op.item = 'COPY', item
        layout.separator()

        op = layout.operator('sourceops.list_operator', text='', icon='TRIA_UP')
        op.mode, op.item = 'MOVE_UP', item
        op = layout.operator('sourceops.list_operator', text='', icon='TRIA_DOWN')
        op.mode, op.item = 'MOVE_DOWN', item
