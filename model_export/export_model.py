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
        smd.write("triangles\n")

    def export_smd(self, context, directory, name, objects, combine, collision):
        """Export objects to one or more SMD files"""
        base = context.scene.BASE
        settings = base.settings
        scale = settings.scale
        common.verify_folder(directory)

        if combine:
            smd = open(directory + name + ".smd", "w")
            self.write_smd_header(smd)

        for o in objects:
            if not combine:
                o_name = common.clean_filename(o.name)
                smd = open(directory + o_name + ".smd", "w")
                self.write_smd_header(smd)

            evaluated_obj = o.evaluated_get(context.view_layer.depsgraph)
            temp = evaluated_obj.to_mesh()
            common.triangulate(temp)

            if not collision:
                temp.calc_normals_split()

            for poly in temp.polygons:
                if poly.material_index < len(o.material_slots):
                    material = o.material_slots[poly.material_index].material
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

            if not collision:
                temp.free_normals_split()

            evaluated_obj.to_mesh_clear()

            if not combine:
                smd.write("end\n")

        if combine:
            smd.write("end\n")

    def export_meshes(self, context, directory):
        """Export this model's meshes to SMD files"""
        base = context.scene.BASE
        model = base.model()

        if model.reference:
            ref_dir = directory + "reference" + os.sep
            self.export_smd(context, ref_dir, None, model.reference.objects, False, False)
            for c in model.reference.children:
                c_name = common.clean_filename(c.name)
                self.export_smd(context, ref_dir, c_name, c.all_objects, True, False)

        if model.collision:
            col_dir = directory + "collision" + os.sep
            self.export_smd(context, col_dir, "collision", model.collision.all_objects, True, True)

        if model.bodygroups:
            for bg in model.bodygroups.children:
                bg_dir = directory + common.clean_filename(bg.name) + os.sep
                self.export_smd(context, bg_dir, None, bg.objects, False, False)
                for c in bg.children:
                    c_name = common.clean_filename(c.name)
                    self.export_smd(context, bg_dir, c_name, c.all_objects, True, False)

        return True

    def generate_qc(self, context):
        """Generate the QC for this model"""
        base = context.scene.BASE
        game = base.settings.game()
        model = base.model()

        modelsrc_path = game.mod + os.sep + "modelsrc" + os.sep + model.name + os.sep
        qc = open(modelsrc_path + "compile.qc", "w")
        qc.write("$modelname \"" + model.name + "\"\n")
        idle = "AT LEAST ONE REFERENCE MESH REQUIRED"

        if model.reference:
            for o in model.reference.objects:
                o_name = common.clean_filename(o.name)
                qc.write("$body \"" + o_name + "\" \"")
                qc.write("reference" + os.sep + o_name + ".smd\"\n")
                idle = "reference" + os.sep + o_name + ".smd"

            for c in model.reference.children:
                c_name = common.clean_filename(c.name)
                qc.write("$body \"" + c_name + "\" \"")
                qc.write("reference" + os.sep + c_name + ".smd\"\n")
                idle = "reference" + os.sep + c_name + ".smd"

        if model.collision:
            qc.write("$collisionmodel \"collision" + os.sep + "collision.smd\"\n")
            qc.write("{\n    $concave\n    $maxconvexpieces 10000\n}\n")

        if model.bodygroups:
            for bg in model.bodygroups.children:
                bg_name = common.clean_filename(bg.name)
                qc.write("$bodygroup \"" + bg_name + "\"\n{\n")

                for o in bg.objects:
                    o_name = common.clean_filename(o.name)
                    qc.write("    studio \"" + bg_name + os.sep + o_name + ".smd\"\n")

                for c in bg.children:
                    c_name = common.clean_filename(c.name)
                    qc.write("    studio \"" + bg_name + os.sep + c_name + ".smd\"\n")

                # BUG Putting blank at the end of a bodygroup breaks it.
                qc.write("}\n")  # qc.write("    blank\n}\n")

        qc.write("$sequence idle \"" + idle + "\"\n")
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
                    return model.name

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
