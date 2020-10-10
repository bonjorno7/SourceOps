import bpy
import bpy_extras
from .. import utils


class SOURCEOPS_OT_BackupPreferences(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = 'sourceops.backup_preferences'
    bl_label = 'Backup Preferences'
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_description = '.\n'.join((
        'Save addon preferences to a file',
        'Made possible by PowerBackup'))

    filter_glob: bpy.props.StringProperty(default='*.json', options={'HIDDEN'})
    filename_ext: bpy.props.StringProperty(default='.json', options={'HIDDEN'})

    def invoke(self, context, event):
        self.filepath = utils.backup.filepath()
        return super().invoke(context, event)

    def execute(self, context):
        result = utils.backup.backup(self.filepath)
        self.report(result[0], result[1])
        return result[2]


class SOURCEOPS_OT_RestorePreferences(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = 'sourceops.restore_preferences'
    bl_label = 'Restore Preferences'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    bl_description = '.\n'.join((
        'Load addon preferences from a file',
        'Made possible by PowerBackup'))

    filter_glob: bpy.props.StringProperty(default='*.json', options={'HIDDEN'})
    filename_ext: bpy.props.StringProperty(default='.json', options={'HIDDEN'})

    def invoke(self, context, event):
        self.filepath = utils.backup.filepath()
        return super().invoke(context, event)

    def execute(self, context):
        result = utils.backup.restore(self.filepath)
        self.report(result[0], result[1])
        return result[2]
