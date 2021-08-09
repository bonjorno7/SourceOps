import bpy
import subprocess
import os
from math import degrees
from pathlib import Path
from traceback import print_exc
from ... utils import common
from . smd import SMD
from . fbx import export_fbx


class Model:
    def __init__(self, game, model):
        self.prefs = common.get_prefs(bpy.context)
        self.wine = Path(self.prefs.wine)

        self.game = Path(game.game)
        self.bin = Path(game.bin)
        if model.static and model.static_prop_combine:
            self.modelsrc = self.game.parent.parent.joinpath('content', self.game.name, 'models')
        else:
            self.modelsrc = Path(game.modelsrc)
        self.models = Path(game.models)
        self.mapsrc = Path(game.mapsrc)
        self.mesh_type = game.mesh_type

        self.name = Path(model.name).with_suffix('').as_posix()
        self.stem = common.clean_filename(Path(self.name).stem)
        if model.static and model.static_prop_combine:
            directory = self.modelsrc.joinpath(self.name).parent
        else:
            directory = self.modelsrc.joinpath(self.name)
        self.directory = common.verify_folder(directory)

        studiomdl = self.bin.joinpath('studiomdl.exe')
        quickmdl = self.bin.joinpath('quickmdl.exe')
        self.studiomdl = quickmdl if quickmdl.is_file() else studiomdl
        self.hlmv = self.bin.joinpath('hlmv.exe')

        self.material_folder_items = model.material_folder_items
        self.skin_items = model.skin_items
        self.sequence_items = model.sequence_items
        self.attachment_items = model.attachment_items

        self.armature = model.armature
        self.reference = model.reference
        self.collision = model.collision
        self.bodygroups = model.bodygroups
        self.stacking = model.stacking

        self.surface = model.surface
        self.glass = model.glass
        self.static = model.static
        self.joints = model.joints

        self.prepend_armature = model.prepend_armature
        self.ignore_transforms = model.ignore_transforms

        self.origin_source = model.origin_source
        self.origin_object = model.origin_object

        self.origin_x = model.origin_x
        self.origin_y = model.origin_y
        self.origin_z = model.origin_z
        self.rotation = model.rotation
        self.scale = model.scale

    def export_meshes(self):
        self.ensure_modelsrc_folder()
        # self.remove_modelsrc_old()  # Commented out because it might be annoying.

        if not self.sequence_items:
            self.export_anim(self.armature, None, self.directory.joinpath('anims', 'idle.SMD'))

        for sequence in self.sequence_items:
            path = self.directory.joinpath('anims', f'{common.clean_filename(sequence.name)}.SMD')
            self.export_anim(self.armature, sequence.action, path)

        if self.reference:
            objects = self.get_all_objects(self.reference)
            path = self.get_body_path(self.reference)
            self.export_mesh(self.armature, objects, path)

        if self.collision:
            objects = self.get_all_objects(self.collision)
            path = self.get_body_path(self.collision)
            self.export_mesh(self.armature, objects, path)

        if self.bodygroups:
            for bodygroup in self.bodygroups.children:
                for collection in bodygroup.children:
                    objects = self.get_all_objects(collection)
                    path = self.get_body_path(collection)
                    self.export_mesh(self.armature, objects, path)

        if self.stacking:
            for collection in self.stacking.children:
                objects = self.get_all_objects(collection)
                path = self.get_body_path(collection)
                self.export_mesh(self.armature, objects, path)

    def export_anim(self, armature, action, path):
        self.export_smd(armature, [], action, path)

    def export_mesh(self, armature, objects, path):
        if self.mesh_type == 'SMD':
            self.export_smd(armature, objects, None, path)
        elif self.mesh_type == 'FBX':
            self.export_fbx(armature, objects, path)

    def export_smd(self, armature, objects, action, path):
        try:
            smd_file = path.open('w')
            print(f'Exporting: {path}')

        except:
            print(f'Failed to export: {path}')
            print_exc()

        else:
            smd = SMD(self.prepend_armature, self.ignore_transforms)
            smd.from_blender(armature, objects, action)

            smd_file.write(smd.to_string())
            smd_file.close()

    def export_fbx(self, armature, objects, path):
        try:
            print(f'Exporting: {path}')
            export_fbx(path, armature, objects, self.prepend_armature, self.ignore_transforms)

        except:
            print(f'Failed to export {path}')
            print_exc()

    def get_all_objects(self, collection):
        return common.remove_duplicates(collection.all_objects) if collection else []

    def get_body_path(self, collection):
        name = common.clean_filename(collection.name)
        return self.directory.joinpath(f'{name}.{self.mesh_type}')

    def generate_qc(self):
        if not self.reference and not self.stacking:
            return self.report(f'Unable to generate QC for: {self.name} (reference and stacking both not set)')

        if not self.armature and not self.static:
            return self.report(f'Unable to generate QC for: {self.name} (armature not set and static not enabled)')

        self.ensure_modelsrc_folder()
        path = self.directory.joinpath(f'{self.stem}.qc')

        try:
            qc = path.open('w')
            print(f'Generating: {path}')
        except:
            return self.report(f'Failed to open: {path}')

        qc.write(f'$modelname "{self.name}"')
        qc.write('\n')

        if not self.material_folder_items:
            qc.write('\n')
            qc.write('$cdmaterials "/"')
            qc.write('\n')

        for material_folder in self.material_folder_items:
            qc.write('\n')
            qc.write(f'$cdmaterials "{material_folder.name}"')
            qc.write('\n')

        qc.write('\n')
        qc.write(f'$surfaceprop "{self.surface}"')
        qc.write('\n')

        if self.glass:
            qc.write('\n')
            qc.write('$mostlyopaque')
            qc.write('\n')

        if self.static:
            qc.write('\n')
            qc.write('$staticprop')
            qc.write('\n')

        if self.origin_source == 'MANUAL':
            origin_x = self.origin_x
            origin_y = self.origin_y
            origin_z = self.origin_z
            rotation = -self.rotation
        elif self.origin_source == 'OBJECT' and self.origin_object:
            loc, rot, _ = self.origin_object.matrix_world.decompose()
            origin_x = loc.x
            origin_y = loc.y
            origin_z = loc.z
            rotation = -degrees(rot.to_euler().z)
        else:
            origin_x = 0
            origin_y = 0
            origin_z = 0
            rotation = 0

        if self.static and self.mesh_type == 'FBX':
            origin_x, origin_y = -origin_y, origin_x
            rotation -= 180
        else:
            rotation -= 90

        qc.write('\n')
        qc.write(f'$origin {origin_x:.6f} {origin_y:.6f} {origin_z:.6f} {rotation:.6f}')
        qc.write('\n')

        qc.write('\n')
        qc.write(f'$scale {self.scale:.6f}')
        qc.write('\n')

        if self.reference:
            qc.write('\n')
            name = common.clean_filename(self.reference.name)
            qc.write(f'$body "{name}" "{name}.{self.mesh_type}"')
            qc.write('\n')

        if self.collision:
            qc.write('\n')
            name = common.clean_filename(self.collision.name)
            command = 'collisionjoints' if self.joints else 'collisionmodel'
            qc.write(f'${command} "{name}.{self.mesh_type}"' + ' {\n')
            command = 'concaveperjoint' if self.joints else 'concave'
            qc.write(f'    ${command}\n')
            qc.write('    $maxconvexpieces 10000\n')
            qc.write('}')
            qc.write('\n')

        if self.bodygroups and not self.static:
            for bodygroup in self.bodygroups.children:
                qc.write('\n')
                bodygroup_name = common.clean_filename(bodygroup.name)
                qc.write(f'$bodygroup "{bodygroup_name}"' + ' {\n')
                for collection in bodygroup.children:
                    name = common.clean_filename(collection.name)
                    qc.write(f'    studio "{name}.{self.mesh_type}"\n')
                qc.write('}')
                qc.write('\n')

        if self.stacking:
            for collection in self.stacking.children:
                qc.write('\n')
                name = common.clean_filename(collection.name)
                qc.write(f'$model "{name}" "{name}.{self.mesh_type}"')
                qc.write('\n')

        if not self.sequence_items:
            qc.write('\n')
            qc.write(f'$sequence "idle" "anims/idle.SMD"')
            qc.write('\n')

        for sequence in self.sequence_items:
            qc.write('\n')
            qc.write(f'$sequence "{sequence.name}"' + ' {\n')
            qc.write(f'    "anims/{common.clean_filename(sequence.name)}.SMD"\n')
            if sequence.use_framerate:
                qc.write(f'    fps {sequence.framerate}\n')
            else:
                qc.write(f'    fps {bpy.context.scene.render.fps}\n')
            if sequence.use_range:
                qc.write(f'    frames {sequence.start} {sequence.end}\n')
            if sequence.snap:
                qc.write('    snap\n')
            if sequence.loop:
                qc.write('    loop\n')
            qc.write(f'    activity "{sequence.activity}" {sequence.weight}\n')
            for event in sequence.event_items:
                qc.write('    { ' + f'event "{event.event}" {event.frame} "{event.value}"' + ' }\n')
            qc.write('}')
            qc.write('\n')

        for attachment in self.attachment_items:
            if self.armature and attachment.bone:
                qc.write('\n')
                qc.write(f'$attachment "{attachment.name}"')
                if self.prepend_armature:
                    qc.write(f' "{self.armature.name}.{attachment.bone}"')
                else:
                    qc.write(f' "{attachment.bone}"')
                qc.write(f' {attachment.offset[0]} {attachment.offset[1]} {attachment.offset[2]}')
                if attachment.absolute:
                    qc.write(' absolute')
                if attachment.rigid:
                    qc.write(' rigid')
                qc.write(f' rotate {attachment.rotation[0]} {attachment.rotation[1]} {attachment.rotation[2]}')
                qc.write('\n')

        if self.skin_items:
            qc.write('\n')
            qc.write('$texturegroup "skinfamilies"')
            qc.write('\n')
            qc.write('{')

            for skin in self.skin_items:
                qc.write('\n')
                qc.write(f'    {{ {skin.name} }}')

            qc.write('\n')
            qc.write('}')
            qc.write('\n')

        qc.close()

    def compile_qc(self):
        qc = self.directory.joinpath(f'{self.stem}.qc')
        if qc.is_file():
            print(f'Compiling: {qc}')
            self.ensure_models_folder()
            self.remove_models_old()

            # Use wine to run StudioMDL on Linux.
            # Wine tends to complain about the paths we feed StudioMDL.
            # So we use relatve paths working from the base directory of the game.
            if (os.name == 'posix') and (self.studiomdl.suffix == '.exe'):
                cwd = self.game.parent
                args = [str(self.wine), str(self.studiomdl.relative_to(cwd)), '-nop4', '-fullcollide',
                        '-game', str(self.game.relative_to(cwd)), str(qc.relative_to(cwd))]
            else:
                cwd = None
                args = [str(self.studiomdl), '-nop4', '-fullcollide', '-game', str(self.game), str(qc)]

            pipe = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)

            while True:
                code = pipe.returncode
                if code is None:
                    log = self.directory.joinpath(f'{self.stem}.log')
                    log.write_bytes(b'\n\n\n'.join(pipe.communicate()))
                else:
                    break

            if code == 0:
                self.move_files()
            else:
                return self.report(f'Failed to compile: {qc}')
        else:
            return self.report(f'Unable to find: {qc}')

    def open_folder(self):
        try:
            print(f'Opening: {self.directory}')
            bpy.ops.wm.path_open(filepath=str(self.directory))
        except:
            return self.report(f'Failed to open: {self.directory}')

    def view_model(self):
        model = self.models.joinpath(self.name)
        mdl = model.with_suffix('.mdl')
        dx90 = model.with_suffix('.dx90.vtx')

        # Use wine to run HLMV on Linux.
        # Wine tends to complain about the paths we feed HLMV.
        # So we use relatve paths working from the base directory of the game.
        if (os.name == 'posix') and (self.studiomdl.suffix == '.exe'):
            cwd = self.game.parent
            args = [str(self.wine), str(self.hlmv.relative_to(cwd)), '-game',
                    str(self.game.relative_to(cwd)), str(mdl.relative_to(cwd))]
        else:
            cwd = None
            args = [str(self.hlmv), '-game', str(self.game), str(mdl)]

        if dx90.is_file():
            print(f'Viewing: {mdl}')
            subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        else:
            return self.report(f'Failed to view: {mdl}')

    def move_files(self):
        path_src = self.game.joinpath('models', self.name)
        path_dst = self.models.joinpath(self.name)

        if path_src == path_dst:
            return

        print(f'Moving to: {self.models}')
        common.verify_folder(path_dst.parent)

        for suffix in ('.dx90.vtx', '.dx80.vtx', '.sw.vtx', '.vvd', '.mdl', '.phy'):
            src = path_src.with_suffix(suffix)
            dst = path_dst.with_suffix(suffix)

            try:
                src.rename(dst)
            except:
                print(f'Failed to move {src} to {dst}')

    def ensure_modelsrc_folder(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        self.directory.joinpath('anims').mkdir(parents=True, exist_ok=True)

    def remove_modelsrc_old(self):
        for file in self.directory.rglob('*'):
            if file.suffix in ('.SMD', '.FBX'):
                if file.is_file():
                    file.unlink()

    def ensure_models_folder(self):
        destination = self.models.joinpath(self.name).parent
        destination.mkdir(parents=True, exist_ok=True)

    def remove_models_old(self):
        model = self.models.joinpath(self.name)
        for suffix in ('.dx90.vtx', '.dx80.vtx', '.sw.vtx', '.vvd', '.mdl', '.phy'):
            path = model.with_suffix(suffix)
            if path.is_file():
                path.unlink()

    def report(self, error):
        print(error)
        return error
