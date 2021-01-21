import bpy
import shutil
import subprocess
from pathlib import Path
from ... utils import common
from . smd import SMD


class Model:
    def __init__(self, game, model):
        self.game = Path(game.game)
        self.bin = Path(game.bin)
        if model.static and model.static_prop_combine:
            self.modelsrc = self.game.parent.parent.joinpath('content', self.game.name, 'models')
        else:
            self.modelsrc = Path(game.modelsrc)
        self.models = Path(game.models)
        self.mapsrc = Path(game.mapsrc)

        self.name = str(Path(model.name).with_suffix(''))
        self.basename = common.clean_filename(Path(self.name).stem)
        if model.static and model.static_prop_combine:
            directory = self.modelsrc.joinpath(Path(self.name).parent)
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

        self.reference = model.reference
        self.collision = model.collision
        self.bodygroups = model.bodygroups
        self.stacking = model.stacking

        self.surface = model.surface
        self.static = model.static
        self.glass = model.glass

        self.prepend_armature = model.prepend_armature
        self.ignore_transforms = model.ignore_transforms
        self.origin_x = model.origin_x
        self.origin_y = model.origin_y
        self.origin_z = model.origin_z
        self.rotation = model.rotation
        self.scale = model.scale

    def export_meshes(self):
        armatures = self.get_armatures()
        path = self.directory.joinpath(f'{self.basename}_anims.smd')
        self.export_smd(armatures, [], path)

        if self.reference:
            objects = self.get_all_objects(self.reference)
            path = self.get_body_path(self.reference)
            self.export_smd(armatures, objects, path)

        if self.collision:
            objects = self.get_all_objects(self.collision)
            path = self.get_body_path(self.collision)
            self.export_smd(armatures, objects, path)

        if self.bodygroups:
            for bodygroup in self.bodygroups.children:
                for collection in bodygroup.children:
                    objects = self.get_all_objects(collection)
                    path = self.get_body_path(collection)
                    self.export_smd(armatures, objects, path)

        if self.stacking:
            for collection in self.stacking.children:
                objects = self.get_all_objects(collection)
                path = self.get_body_path(collection)
                self.export_smd(armatures, objects, path)

        return True

    def export_smd(self, armatures, objects, path):
        try:
            smd_file = path.open('w')
            print(f'Exporting: {path}')

        except:
            print(f'Failed to export: {path}')
            return

        smd = SMD(self.prepend_armature, self.ignore_transforms)
        smd.from_blender(armatures, objects)

        smd_file.write(smd.to_string())
        smd_file.close()

    def get_armatures(self):
        objects = self.get_all_objects(self.reference)
        objects += self.get_all_objects(self.collision)
        objects += self.get_all_objects(self.bodygroups)
        objects += self.get_all_objects(self.stacking)
        armatures = [obj.find_armature() for obj in objects]
        return common.remove_duplicates(arm for arm in armatures if arm)

    def get_all_objects(self, collection):
        return common.remove_duplicates(collection.all_objects) if collection else []

    def get_body_path(self, collection):
        name = common.clean_filename(collection.name)
        return self.directory.joinpath(f'{name}.smd')

    def generate_qc(self):
        if not self.reference and not self.stacking:
            print('Models need visible meshes')
            return False

        path = self.directory.joinpath(f'{self.basename}.qc')

        try:
            qc = path.open('w')
            print(f'Generating: {path}')
        except:
            print(f'Failed to generate: {path}')
            return

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

        if self.static:
            qc.write('\n')
            qc.write('$staticprop')
            qc.write('\n')

        if self.glass:
            qc.write('\n')
            qc.write('$mostlyopaque')
            qc.write('\n')

        qc.write('\n')
        qc.write(f'$origin {self.origin_x} {self.origin_y} {self.origin_z} {self.rotation}')
        qc.write('\n')

        qc.write('\n')
        qc.write(f'$scale {self.scale}')
        qc.write('\n')

        if self.reference:
            qc.write('\n')
            name = common.clean_filename(self.reference.name)
            qc.write(f'$body "{name}" "{name}.smd"')
            qc.write('\n')

        if self.collision:
            qc.write('\n')
            name = common.clean_filename(self.collision.name)
            qc.write(f'$collisionmodel "{name}.smd"' + ' {\n')
            qc.write('    $concave\n')
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
                    qc.write(f'    studio "{name}.smd"\n')
                qc.write('}')
                qc.write('\n')

        if self.stacking:
            for collection in self.stacking.children:
                qc.write('\n')
                name = common.clean_filename(collection.name)
                qc.write(f'$model "{name}" "{name}.smd"')
                qc.write('\n')

        path = f'{self.basename}_anims.smd'

        if not self.sequence_items:
            qc.write('\n')
            qc.write(f'$sequence "idle" "{path}"')
            qc.write('\n')

        for sequence in self.sequence_items:
            qc.write('\n')
            qc.write(f'$sequence "{sequence.name}"' + ' {\n')
            qc.write(f'    "{path}"\n')
            qc.write(f'    frames {sequence.start} {sequence.end}\n')
            if sequence.override:
                qc.write(f'    fps {sequence.framerate}\n')
            else:
                qc.write(f'    fps {bpy.context.scene.render.fps}\n')
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
            if attachment.armature and attachment.bone:
                qc.write('\n')
                qc.write(f'$attachment "{attachment.name}"')
                if self.prepend_armature:
                    qc.write(f' "{attachment.armature}.{attachment.bone}"')
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
                qc.write(f'    {{ "{skin.name}" }}')

            qc.write('\n')
            qc.write('}')
            qc.write('\n')

        qc.close()
        return True

    def compile_qc(self):
        qc = self.directory.joinpath(f'{self.basename}.qc')
        if qc.is_file():
            print(f'Compiling: {qc}')
            self.remove_old()

            args = [str(self.studiomdl), '-nop4', '-fullcollide', '-game', str(self.game), str(qc)]
            pipe = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            while True:
                code = pipe.returncode
                if code is None:
                    log = self.directory.joinpath(f'{self.basename}.log')
                    log.write_text(pipe.communicate()[0].decode('utf'))
                else:
                    break

            if code == 0:
                self.move_files()
                return True

        print(f'Failed to compile: {qc}')
        return False

    def open_folder(self):
        bpy.ops.wm.path_open(filepath=str(self.directory))
        print(f'Opening: {self.directory}')
        return True

    def view_model(self):
        model = self.models.joinpath(self.name)
        mdl = model.with_suffix('.mdl')
        dx90 = model.with_suffix('.dx90.vtx')

        args = [str(self.hlmv), '-game', str(self.game), str(mdl)]

        if dx90.is_file():
            print(f'Viewing: {mdl}')
            subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True

        print(f'Failed to view: {mdl}')
        return False

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
                shutil.copyfile(src, dst)
                src.unlink()
            except:
                print(f'Failed to move {src} to {dst}')

    def remove_old(self):
        model = self.models.joinpath(self.name)
        for suffix in ('.dx90.vtx', '.dx80.vtx', '.sw.vtx', '.vvd', '.mdl', '.phy'):
            path = model.with_suffix(suffix)
            if path.is_file():
                path.unlink()
