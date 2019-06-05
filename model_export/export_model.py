import os
import subprocess
import math
import bpy
import mathutils
from .. import common


class ExportModel(bpy.types.Operator):
    """Export this model's meshes, generate a QC and compile it"""
    bl_idname = "base.export_model"
    bl_label = "Export Model"

    def delete_old(self, model, game_path):
        """deleting the old model so the model viewer won't load it if you try to view it while it's still compiling"""
        model_path = game_path + os.sep + "models" + os.sep + model.name
        if os.path.isfile(model_path + ".dx90.vtx"):
            os.remove(model_path + ".dx90.vtx")
        if os.path.isfile(model_path + ".dx80.vtx"):
            os.remove(model_path + ".dx80.vtx")
        if os.path.isfile(model_path + ".sw.vtx"):
            os.remove(model_path + ".sw.vtx")
        if os.path.isfile(model_path + ".vvd"):
            os.remove(model_path + ".vvd")
        if os.path.isfile(model_path + ".mdl"):
            os.remove(model_path + ".mdl")
        if os.path.isfile(model_path + ".phy"):
            os.remove(model_path + ".phy")

    def write_smd_header(self, smd):
        """Write the header for this SMD file, including the required dummy skeleton and animation data"""
        smd.write("version 1\n")
        smd.write("nodes\n")
        smd.write("0 \"blender_implicit\" -1\n")
        smd.write("end\n")
        smd.write("skeleton\n")
        smd.write("time 0\n")
        smd.write("0" + "    ")
        smd.write("%f %f %f    " % (0.0, 0.0, 0.0))
        smd.write("%f %f %f\n" % (0.0, 0.0, 0.0))
        smd.write("end\n")

    def export_smd(self, context, directory, collection, kind):
        base = context.scene.BASE
        settings = base.settings
        scale = settings.scale

        reference = True if kind == 'REFERENCE' else False
        collision = True if kind == 'COLLISION' else False
        bodygroup = True if kind == 'BODYGROUP' else False
        clean_name = common.clean_filename(collection.name)

        if collision:
            collection_directory = common.verify_folder(directory + "collision" + os.sep)
            smd = open(collection_directory + clean_name + ".smd", "w")
            self.write_smd_header(smd)
            smd.write("triangles\n")

        for obj in collection.all_objects:
            if reference:
                collection_directory = common.verify_folder(directory + "reference" + os.sep)
                smd = open(collection_directory + common.clean_filename(obj.name) + ".smd", "w")

            elif bodygroup:
                collection_directory = common.verify_folder(directory + clean_name + os.sep)
                smd = open(collection_directory + common.clean_filename(obj.name) + ".smd", "w")

            if reference or bodygroup:
                self.write_smd_header(smd)
                smd.write("triangles\n")

            evaluated_obj = obj.evaluated_get(context.view_layer.depsgraph)
            temp = evaluated_obj.to_mesh()
            common.triangulate(temp)

            if reference or bodygroup:
                temp.calc_normals_split()

            for poly in temp.polygons:
                if poly.material_index < len(obj.material_slots):
                    material = obj.material_slots[poly.material_index].material
                    if material is not None:
                        smd.write(material.name + "\n")
                else:
                    smd.write("no_material" + "\n")

                for index in range(3):
                    smd.write("0    ")
                    loop_index = poly.loop_indices[index]
                    loop = temp.loops[loop_index]
                    rot = mathutils.Matrix.Rotation(math.radians(180), 4, 'Z')

                    vert_index = loop.vertex_index
                    vert = temp.vertices[vert_index]
                    vec = rot @ evaluated_obj.matrix_local @ mathutils.Vector(vert.co) * scale
                    smd.write("%f %f %f    " % (-vec[1], vec[0], vec[2]))

                    normal = vert.normal if collision else loop.normal
                    nor = mathutils.Vector([normal[0], normal[1], normal[2], 0.0])
                    nor = rot @ evaluated_obj.matrix_local @ nor
                    smd.write("%f %f %f    " % (-nor[1], nor[0], nor[2]))

                    if temp.uv_layers:
                        uv_layer = [layer for layer in temp.uv_layers if layer.active_render][0]
                        uv_loop = uv_layer.data[loop_index]
                        uv = uv_loop.uv
                        smd.write("%f %f\n" % (uv[0], uv[1]))
                    else:
                        smd.write("%f %f\n" % (0.0, 0.0))

            if reference or bodygroup:
                temp.free_normals_split()

            evaluated_obj.to_mesh_clear()
            smd.write("end\n")

    def export_meshes(self, context, directory):
        """Export this model's meshes as SMD"""
        base = context.scene.BASE
        model = base.model()

        for c in model.collection.children:
            if c.name.lower().count("reference"):
                self.export_smd(context, directory, c, 'REFERENCE')
            elif c.name.lower().count("collision"):
                self.export_smd(context, directory, c, 'COLLISION')
            else:
                self.export_smd(context, directory, c, 'BODYGROUP')

        return True

    def generate_qc(self, context):
        """Generate the QC for this model"""
        base = context.scene.BASE
        game = base.settings.game()
        model = base.model()

        modelsrc_path = game.mod + os.sep + "modelsrc" + os.sep + model.name + os.sep
        qc = open(modelsrc_path + "compile.qc", "w")
        qc.write("$modelname \"" + model.name + "\"\n")

        reference = "reference"
        for c in model.collection.children:
            clean_name = common.clean_filename(c.name)

            if c.name.lower().count("reference"):
                for o in c.all_objects:
                    o_name = common.clean_filename(o.name)
                    qc.write("$body \"" + o_name + "\" \"")
                    qc.write("reference" + os.sep + o_name + ".smd\"\n")
                    reference = "reference" + os.sep + o_name + ".smd"

            elif c.name.lower().count("collision"):
                qc.write("$collisionmodel \"" + "collision" + os.sep + clean_name)
                qc.write(".smd\" { $concave $maxconvexpieces 10000 }\n")

            else:
                qc.write("$bodygroup \"" + clean_name + "\"\n{\n")
                for o in c.all_objects:
                    o_name = common.clean_filename(o.name)
                    qc.write("    studio \"" + clean_name + os.sep + o_name + ".smd\"\n")
                qc.write("}\n")  # qc.write("    blank\n}\n")  # why does this break it??

        qc.write("$sequence idle \"" + reference + "\"\n")
        qc.write("$cdmaterials \"" + os.sep + "\"\n")
        qc.write("$surfaceprop \"" + model.surface_prop + "\"\n")
        qc.write("$staticprop\n")

        if model.autocenter:
            qc.write("$autocenter\n")
        if model.mostly_opaque:
            qc.write("$mostlyopaque\n")

        qc.close()
        return True

    @classmethod
    def poll(cls, context):
        base = context.scene.BASE
        settings = base.settings
        games = settings.games
        game_index = settings.game_index

        if games and game_index >= 0:
            game = games[game_index]

            if game.name != "Invalid Game":
                models = base.models
                model_index = base.model_index

                if models and model_index >= 0:
                    model = models[model_index]

                    if model.name and model.collection:
                        return model.collection.all_objects

        return False

    def execute(self, context):
        base = context.scene.BASE
        settings = base.settings
        games = settings.games
        game_index = settings.game_index
        game = games[game_index]

        model = base.models[base.model_index]
        model_path = common.verify_folder(game.mod + os.sep + "modelsrc" + os.sep + model.name + os.sep)
        self.delete_old(model, game.mod)

        if self.export_meshes(context, model_path) and self.generate_qc(context):
            args = [game.studiomdl, '-nop4', '-fullcollide', model_path + "compile.qc"]
            print(game.studiomdl + "    " + model_path + "compile.qc" + "\n")
            pipe = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            while True:
                code = pipe.returncode
                if code is None:
                    with open(model_path + "log.txt", "w") as log:
                        log.write(pipe.communicate()[0].decode('utf'))
                else:
                    break

        return {'FINISHED'}
