import os
import subprocess
import math
import bpy
import mathutils
from .. import common
from . import surface_props


class ModelProps(bpy.types.PropertyGroup):
    """Holds the variables and functions for a model"""
    bl_idname = "BASE_PG_ModelProps"

    reference: bpy.props.PointerProperty(type=bpy.types.Collection)
    collision: bpy.props.PointerProperty(type=bpy.types.Collection)
    bodygroups: bpy.props.PointerProperty(type=bpy.types.Collection)

    def update_name(self, context):
        name = bpy.path.native_pathsep(self["name"])
        if name.lower().endswith(".mdl"):
            name = name[:-4]
        self["name"] = name

    name: bpy.props.StringProperty(
        name="Model Name",
        description="Your model's path, eg example" + os.sep + "model",
        default="example" + os.sep + "model",
        update=update_name,
    )

    surface_prop: bpy.props.EnumProperty(
        name="Surface Property",
        description="Choose the surface property of your model, this affects decals and how it sounds in game",
        items=surface_props.surface_props,
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
        model_path = game.mod + os.sep + "models" + os.sep + self.name
        common.remove_if_exists(model_path + ".dx90.vtx")
        common.remove_if_exists(model_path + ".dx80.vtx")
        common.remove_if_exists(model_path + ".sw.vtx")
        common.remove_if_exists(model_path + ".vvd")
        common.remove_if_exists(model_path + ".mdl")
        common.remove_if_exists(model_path + ".phy")

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

    def export_smd(self, context, directory, filename, objects, combine, collision):
        """Export objects to one or more SMD files"""
        scale = common.get_scale(context)
        common.verify_folder(directory)

        if combine:
            smd = open(directory + filename + ".smd", "w")
            self.write_smd_header(smd)
            smd.write("triangles\n")

        for o in objects:
            if not combine:
                o_name = common.clean_filename(o.name)
                smd = open(directory + o_name + ".smd", "w")
                self.write_smd_header(smd)
                smd.write("triangles\n")

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
        if self.reference:
            ref_dir = directory + "reference" + os.sep
            self.export_smd(context, ref_dir, None, self.reference.objects, False, False)
            for c in self.reference.children:
                c_name = common.clean_filename(c.name)
                self.export_smd(context, ref_dir, c_name, c.all_objects, True, False)

        if self.collision:
            col_dir = directory + "collision" + os.sep
            self.export_smd(context, col_dir, "collision", self.collision.all_objects, True, True)

        if self.bodygroups:
            for bg in self.bodygroups.children:
                bg_dir = directory + common.clean_filename(bg.name) + os.sep
                self.export_smd(context, bg_dir, None, bg.objects, False, False)
                for c in bg.children:
                    c_name = common.clean_filename(c.name)
                    self.export_smd(context, bg_dir, c_name, c.all_objects, True, False)

        return True

    def generate_qc(self, context, directory):
        """Generate the QC for this model"""
        qc = open(directory + "compile.qc", "w")
        qc.write("$modelname \"" + self.name + "\"\n")
        idle = "AT LEAST ONE REFERENCE MESH REQUIRED"

        if self.reference:
            for o in self.reference.objects:
                o_name = common.clean_filename(o.name)
                qc.write("$body \"" + o_name + "\" \"")
                qc.write("reference" + os.sep + o_name + ".smd\"\n")
                idle = "reference" + os.sep + o_name + ".smd"

            for c in self.reference.children:
                c_name = common.clean_filename(c.name)
                qc.write("$body \"" + c_name + "\" \"")
                qc.write("reference" + os.sep + c_name + ".smd\"\n")
                idle = "reference" + os.sep + c_name + ".smd"

        if self.collision:
            qc.write("$collisionmodel \"collision" + os.sep + "collision.smd\"\n")
            qc.write("{\n    $concave\n    $maxconvexpieces 10000\n}\n")

        if self.bodygroups:
            for bg in self.bodygroups.children:
                bg_name = common.clean_filename(bg.name)
                qc.write("$bodygroup \"" + bg_name + "\"\n{\n")

                for o in bg.objects:
                    o_name = common.clean_filename(o.name)
                    qc.write("    studio \"" + bg_name + os.sep + o_name + ".smd\"\n")

                for c in bg.children:
                    c_name = common.clean_filename(c.name)
                    qc.write("    studio \"" + bg_name + os.sep + c_name + ".smd\"\n")

                # BUG Putting blank at the end of a bodygroup breaks it.
                # qc.write("    blank\n")

                qc.write("}\n")

        qc.write("$sequence idle \"" + idle + "\"\n")
        qc.write("$cdmaterials \"" + os.sep + "\"\n")
        qc.write("$surfaceprop \"" + self.surface_prop + "\"\n")
        qc.write("$staticprop\n")

        if self.autocenter:
            qc.write("$autocenter\n")
        if self.mostly_opaque:
            qc.write("$mostlyopaque\n")

        qc.close()
        return True

    def export(self, context):
        game = common.get_game(context)
        directory = game.mod + os.sep + "modelsrc" + os.sep + self.name + os.sep
        common.verify_folder(directory)
        self.remove_old(context)

        if self.export_meshes(context, directory) and self.generate_qc(context, directory):
            args = [game.studiomdl, '-nop4', '-fullcollide', directory + "compile.qc"]
            print(game.studiomdl + "    " + directory + "compile.qc" + "\n")
            pipe = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            while True:
                code = pipe.returncode
                if code is None:
                    with open(directory + "log.txt", "w") as log:
                        log.write(pipe.communicate()[0].decode('utf'))
                else:
                    break

            return True
        return False

    def view(self, context):
        game = common.get_game(context)
        model_path = game.mod + os.sep + "models" + os.sep + self.name
        mdl_path = model_path + ".mdl"
        dx90_path = model_path + ".dx90.vtx"

        args = [game.hlmv, "-game", game.mod, mdl_path]
        print(game.hlmv + "    " + mdl_path + "\n")

        if os.path.isfile(dx90_path):
            subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        return False
