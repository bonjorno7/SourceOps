import os
import subprocess
import math
import bpy
import mathutils
from .. import common
from . surface_props import surface_props
from . export_smd import export_smd
from . sequence import SequenceProps


class ModelProps(bpy.types.PropertyGroup):
    """Holds the variables and functions for a model"""
    bl_idname = "SOURCEOPS_PG_ModelProps"

    reference: bpy.props.PointerProperty(type=bpy.types.Collection)
    collision: bpy.props.PointerProperty(type=bpy.types.Collection)
    bodygroups: bpy.props.PointerProperty(type=bpy.types.Collection)
    stacking: bpy.props.PointerProperty(type=bpy.types.Collection)

    sequences: bpy.props.CollectionProperty(type=SequenceProps)
    sequence_index: bpy.props.IntProperty(default=0)

    def sequence(self):
        if self.sequences and self.sequence_index >= 0:
            return self.sequences[self.sequence_index]
        return None

    def update_name(self, context):
        name = common.fix_slashes(self["name"])
        if name.lower().endswith(".mdl"):
            name = name[:-4]
        self["name"] = name

    name: bpy.props.StringProperty(
        name="Model Name",
        description="Your model's path, eg example/model",
        default="example/model",
        update=update_name,
    )

    surface_prop: bpy.props.EnumProperty(
        name="Surface Property",
        description="Choose the surface property of your model, this affects decals and how it sounds in game",
        items=surface_props,
    )

    autocenter: bpy.props.BoolProperty(
        name="Auto Center",
        description="$autocenter, aligns the model's $origin to the center of its bounding box",
        default=False,
    )

    mostly_opaque: bpy.props.BoolProperty(
        name="Has Glass",
        description="$mostlyopaque, use this if your model has something transparent like glass",
        default=False,
    )

    def remove_old(self, context):
        """Removing the old model so the model viewer won't load it if you try to view it while it's still compiling"""
        game = common.get_game(context)
        model_path = game.mod + "/" + "models" + "/" + self.name
        common.remove_if_exists(model_path + ".dx90.vtx")
        common.remove_if_exists(model_path + ".dx80.vtx")
        common.remove_if_exists(model_path + ".sw.vtx")
        common.remove_if_exists(model_path + ".vvd")
        common.remove_if_exists(model_path + ".mdl")
        common.remove_if_exists(model_path + ".phy")

    def get_armatures(self, context):
        """Get all armatures affecting this model"""

        # List of all objects of this model
        all_objects = []
        if self.reference:
            all_objects += self.reference.all_objects[:]
        if self.collision:
            all_objects += self.collision.all_objects[:]
        if self.bodygroups:
            all_objects += self.bodygroups.all_objects[:]
        if self.stacking:
            all_objects += self.stacking.all_objects[:]

        # List of armatures affecting this model
        armatures = []
        for armature in [obj.find_armature() for obj in all_objects]:
            if armature and armature not in armatures:
                armatures.append(armature)
        return armatures

    def export_meshes(self, context):
        """Export this model's meshes to SMD files"""
        game = common.get_game(context)
        directory = game.mod + "/" + "modelsrc" + "/" + self.name + "/"
        common.verify_folder(directory)
        armatures = self.get_armatures(context)

        # Even static props need an idle animation
        export_smd(context, directory + "animation.smd", [], armatures, 'ANIMATION')

        if self.reference:
            export_smd(context, directory + "reference.smd", self.reference.all_objects, armatures, 'REFERENCE')

        if self.collision:
            export_smd(context, directory + "collision.smd", self.collision.all_objects, armatures, 'REFERENCE')

        if self.stacking:
            for collection in self.stacking.children:
                name = common.clean_filename(collection.name)
                export_smd(context, directory + name + ".smd", collection.all_objects, armatures, 'REFERENCE')

        if self.bodygroups:
            for bodygroup in self.bodygroups.children:
                bodygroup_name = common.clean_filename(bodygroup.name)
                for collection in bodygroup.children:
                    name = bodygroup_name + "." + common.clean_filename(collection.name)
                    export_smd(context, directory + name  + ".smd", collection.all_objects, armatures, 'REFERENCE')

        return True

    def generate_qc(self, context):
        """Generate the QC for this model"""
        if not self.reference and not self.stacking:
            print("Models need visible meshes")
            return False

        game = common.get_game(context)
        directory = game.mod + "/" + "modelsrc" + "/" + self.name + "/"
        common.verify_folder(directory)
        armatures = self.get_armatures(context)

        qc = open(directory + "compile.qc", "w")
        qc.write("$modelname \"" + self.name + "\"\n")

        if self.reference:
            qc.write("$body \"reference\" \"reference.smd\"\n")

        if self.collision:
            qc.write("$collisionmodel \"collision.smd\"\n")
            qc.write("{ $concave $maxconvexpieces 10000 }\n")

        if self.stacking:
            for collection in self.stacking.children:
                name = common.clean_filename(collection.name)
                qc.write(f'$model "{name}" "{name}.smd"\n')

        if self.bodygroups:
            for bodygroup in self.bodygroups.children:
                bodygroup_name = common.clean_filename(bodygroup.name)
                qc.write("$bodygroup \"" + bodygroup_name + "\"\n{\n")
                for collection in bodygroup.children:
                    name = bodygroup_name + "." + common.clean_filename(collection.name)
                    qc.write("    studio \"" + name + ".smd\"\n")
                qc.write("}\n")

        qc.write("$cdmaterials \"" + "/" + "\"\n")
        qc.write("$surfaceprop \"" + self.surface_prop + "\"\n")

        if self.autocenter:
            qc.write("$autocenter\n")
        if self.mostly_opaque:
            qc.write("$mostlyopaque\n")

        if self.sequences:
            for sequence in self.sequences:
                qc.write("$sequence \"" + sequence.name + "\" {\n")
                qc.write("    \"animation.smd\"\n")
                qc.write("    frames " + str(sequence.start) + " " + str(sequence.end) + "\n")
                qc.write("    fps " + str(context.scene.render.fps) + "\n")
                if sequence.loop:
                    qc.write("    loop\n")
                qc.write("    activity \"" + sequence.activity + "\" " + str(sequence.weight) + "\n")
                for event in sequence.events:
                    qc.write("    { event \"" + event.event + "\" " + str(event.frame) + " \"" + event.value + "\" }\n")
                qc.write("}\n")
        else:
            qc.write("$staticprop\n")
            qc.write("$sequence \"idle\" \"animation.smd\"\n")

        qc.close()
        return True

    def edit_qc(self, context):
        """Open this model's QC in the blender text editor"""
        game = common.get_game(context)
        directory = game.mod + "/" + "modelsrc" + "/" + self.name + "/"
        qc = directory + "compile.qc"

        if not os.path.isfile(qc):
            return False

        for t in bpy.data.texts:
            if t.filepath == qc:
                return True

        bpy.ops.text.open(filepath=qc)

        for t in bpy.data.texts:
            if t.filepath == qc:
                t.name = self.name

        return True

    def compile_qc(self, context):
        """Compile this model using the QC"""
        game = common.get_game(context)
        directory = game.mod + "/" + "modelsrc" + "/" + self.name + "/"
        common.verify_folder(directory)

        if os.path.isfile(directory + "compile.qc"):
            self.remove_old(context)

            args = [game.studiomdl, "-nop4", "-fullcollide", directory + "compile.qc"]
            print(game.studiomdl + "    " + directory + "compile.qc" + "\n")
            pipe = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            while True:
                code = pipe.returncode
                if code is None:
                    with open(directory + "log.txt", "w") as log:
                        log.write(pipe.communicate()[0].decode('utf'))
                else:
                    break

            if code == 0:
                return True

        return False

    def view(self, context):
        game = common.get_game(context)
        model_path = game.mod + "/" + "models" + "/" + self.name
        mdl_path = model_path + ".mdl"
        dx90_path = model_path + ".dx90.vtx"

        args = [game.hlmv, "-game", game.mod, mdl_path]
        print(game.hlmv + "    " + mdl_path + "\n")

        if os.path.isfile(dx90_path):
            subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True

        return False
