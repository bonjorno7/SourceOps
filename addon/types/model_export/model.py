import bpy
import os
import shutil
import subprocess
from ... utils import common
from . smd import SMD


class Model:
    def __init__(self, game, model):
        self.gameinfo = game.gameinfo
        self.additional = game.additional

        self.name = model.name
        if self.name.lower().endswith('.mdl'):
            self.name = self.name[0:-4]

        self.material_folder_items = model.material_folder_items
        self.skin_items = model.skin_items
        self.sequence_items = model.sequence_items
        self.reference = model.reference
        self.collision = model.collision
        self.bodygroups = model.bodygroups
        self.stacking = model.stacking

        self.surface = model.surface
        self.static = model.static
        self.glass = model.glass

        self.ignore_transforms = model.ignore_transforms
        self.origin_x = model.origin_x
        self.origin_y = model.origin_y
        self.origin_z = model.origin_z
        self.rotation = model.rotation
        self.scale = model.scale

    def export_meshes(self):
        directory = self.get_directory()
        armatures = self.get_armatures()

        name = common.clean_filename(os.path.basename(self.name))
        path = f'{directory}{name}_anims.smd'
        self.export_smd(armatures, [], path)

        if self.reference:
            objects = self.get_all_objects(self.reference)
            path = self.get_body_path(directory, self.reference)
            self.export_smd(armatures, objects, path)

        if self.collision:
            objects = self.get_all_objects(self.collision)
            path = self.get_body_path(directory, self.collision)
            self.export_smd(armatures, objects, path)

        if self.bodygroups:
            for bodygroup in self.bodygroups.children:
                for collection in bodygroup.children:
                    objects = self.get_all_objects(collection)
                    path = self.get_body_path(directory, collection)
                    self.export_smd(armatures, objects, path)

        if self.stacking:
            for collection in self.stacking.children:
                objects = self.get_all_objects(collection)
                path = self.get_body_path(directory, collection)
                self.export_smd(armatures, objects, path)

        return True

    def export_smd(self, armatures, objects, path):
        try:
            smd_file = open(path, 'w')
            print(f'Exporting: {path}')

        except:
            print(f'Failed to export: {path}')
            return

        smd = SMD(self.ignore_transforms)
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

    def get_body_path(self, directory, collection):
        name = common.clean_filename(collection.name)
        return f'{directory}{name}.smd'

    def generate_qc(self):
        if not self.reference and not self.stacking:
            print('Models need visible meshes')
            return False

        directory = self.get_directory()
        name = common.clean_filename(os.path.basename(self.name))
        path = f'{directory}{name}.qc'

        try:
            qc = open(path, 'w')
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
            qc.write(f'$cdmaterials "{material_folder.path}"')
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

        if self.bodygroups:
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

        name = common.clean_filename(os.path.basename(self.name))
        path = f'{name}_anims.smd'

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
        name = common.clean_filename(os.path.basename(self.name))
        directory = self.get_directory()
        studiomdl = self.get_studiomdl()

        qc = f'{directory}{name}.qc'
        if os.path.isfile(qc):
            print(f'Compiling: {qc}')
            self.remove_old()

            args = [studiomdl, '-nop4', '-fullcollide', qc]
            pipe = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            while True:
                code = pipe.returncode
                if code is None:
                    with open(f'{directory}{name}.log', 'w') as log:
                        log.write(pipe.communicate()[0].decode('utf'))
                else:
                    break

            if code == 0:
                self.copy_files()
                return True

        print(f'Failed to compile: {qc}')
        return False

    def open_qc(self):
        directory = self.get_directory()
        name = common.clean_filename(os.path.basename(self.name))

        qc = f'{directory}{name}.qc'.replace('\\', '/')
        if not os.path.isfile(qc):
            print(f'Failed to open: {qc}')
            return False

        for text in bpy.data.texts:
            if text.filepath.replace('\\', '/') == qc:
                bpy.data.texts.remove(text)

        text = bpy.data.texts.load(filepath=qc)
        text.name = f'{self.name} (qc)'

        print(f'Opening: {qc}')
        return True

    def open_log(self):
        directory = self.get_directory()
        name = common.clean_filename(os.path.basename(self.name))

        log = f'{directory}{name}.log'.replace('\\', '/')
        if not os.path.isfile(log):
            print(f'Failed to open: {log}')
            return False

        for text in bpy.data.texts:
            if text.filepath.replace('\\', '/') == log:
                bpy.data.texts.remove(text)

        text = bpy.data.texts.load(filepath=log)
        text.name = f'{self.name} (log)'

        print(f'Opening: {log}')
        return True

    def view_model(self):
        mod = os.path.dirname(self.gameinfo)
        model = f'{mod}/models/{self.name}'
        mdl = f'{model}.mdl'
        dx90 = f'{model}.dx90.vtx'

        hlmv = self.get_hlmv()
        args = [hlmv, '-game', mod, mdl]

        if os.path.isfile(dx90):
            print(f'Viewing: {mdl}')
            subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True

        print(f'Failed to view: {mdl}')
        return False

    def copy_files(self):
        if not self.additional:
            return

        print(f'Copying to: {self.additional}')
        mod = os.path.dirname(self.gameinfo)
        model = f'{mod}/models/{self.name}'
        additional = f'{self.additional}/models/{self.name}'
        common.verify_folder(os.path.dirname(additional))

        for extension in ['.dx90.vtx', '.dx80.vtx', '.sw.vtx', '.vvd', '.mdl', '.phy']:
            src = f'{model}{extension}'
            dst = f'{additional}{extension}'

            try:
                shutil.copyfile(src, dst)
            except:
                pass

    def remove_old(self):
        mod = os.path.dirname(self.gameinfo)
        model = f'{mod}/models/{self.name}'
        additional = f'{self.additional}/{self.name}'

        for extension in ['.dx90.vtx', '.dx80.vtx', '.sw.vtx', '.vvd', '.mdl', '.phy']:
            path = f'{model}{extension}'
            if os.path.isfile(path):
                os.remove(path)

            path = f'{additional}{extension}'
            if os.path.isfile(path):
                os.remove(path)

    def get_directory(self):
        mod = os.path.dirname(self.gameinfo)
        directory = f'{mod}/modelsrc/{self.name}/'
        return common.verify_folder(directory)

    def get_studiomdl(self):
        game = os.path.dirname(os.path.dirname(self.gameinfo))
        studiomdl = f'{game}/bin/studiomdl.exe'
        quickmdl = f'{game}/bin/quickmdl.exe'
        return quickmdl if os.path.isfile(quickmdl) else studiomdl

    def get_hlmv(self):
        game = os.path.dirname(os.path.dirname(self.gameinfo))
        return f'{game}/bin/hlmv.exe'
