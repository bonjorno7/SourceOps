# <pep8 compliant>


# <import>
import os, subprocess, math
import bpy, bmesh, mathutils
from .. import common


# </import>

# <functions>
def refresh_meshes(model):
    """Refresh the list of meshes for this model, remove ones that don't exist anymore"""
    meshes_to_remove = []
    for i, m in enumerate(model.meshes):
        if not m.obj.users_scene:
            meshes_to_remove.append(i)
    for i in reversed(meshes_to_remove):
        model.meshes.remove(i)


def write_smd_header(smd):
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


def export_meshes(context, directory):
    """Export this model's meshes as SMD"""
    settings = context.scene.BASE.settings
    scale = settings.scale
    model = context.scene.BASE.models[context.scene.BASE.model_index]
    refresh_meshes(model)
    if not model.meshes: return None

    references = []
    collisions = []

    for mesh in model.meshes:
        if mesh.kind == 'REFERENCE':
            references.append(mesh.obj)
        if mesh.kind == 'COLLISION':
            collisions.append(mesh.obj)

    with open(directory + "reference.smd", "w+") as ref:
        write_smd_header(ref)
        ref.write("triangles\n")

        for obj in references:
            temp = obj.to_mesh(context.depsgraph, apply_modifiers=True, calc_undeformed=False)
            common.triangulate(temp)
            temp.calc_normals_split()

            for poly in temp.polygons:
                material_name = "no_material"
                if poly.material_index < len(obj.material_slots):
                    material = obj.material_slots[poly.material_index].material
                    if material != None: material_name = material.name
                ref.write(material_name + "\n")

                for index in range(3):
                    ref.write("0    ")
                    loop_index = poly.loop_indices[index]
                    loop = temp.loops[loop_index]

                    vert_index = loop.vertex_index
                    vert = temp.vertices[vert_index]
                    rot = mathutils.Matrix.Rotation(math.radians(180), 4, 'Z')
                    vec = rot @ obj.matrix_local @ mathutils.Vector(vert.co)
                    ref.write("%f %f %f    " % (-vec[1] * scale, vec[0] * scale, vec[2] * scale))

                    normal = mathutils.Vector([loop.normal[0], loop.normal[1], loop.normal[2], 0.0])
                    normal = rot @ obj.matrix_local @ normal
                    ref.write("%f %f %f    " % (-normal[1], normal[0], normal[2]))

                    if temp.uv_layers:
                        uv_layer = [layer for layer in temp.uv_layers if layer.active_render][0]
                        uv_loop = uv_layer.data[loop_index]
                        uv = uv_loop.uv
                        ref.write("%f %f\n" % (uv[0], uv[1]))
                    else:
                        ref.write("%f %f\n" % (0.0, 0.0))

            temp.free_normals_split()
            bpy.data.meshes.remove(temp)

        ref.write("end\n")

    with open(directory + "collision.smd", "w+") as col:
        write_smd_header(col)
        col.write("triangles\n")

        for obj in collisions:
            temp = obj.to_mesh(context.depsgraph, apply_modifiers=True, calc_undeformed=False)
            common.triangulate(temp)

            for poly in temp.polygons:
                col.write("no_material" + "\n")

                for index in range(3):
                    col.write("0" + "    ")
                    loop_index = poly.loop_indices[index]
                    loop = temp.loops[loop_index]

                    vert_index = loop.vertex_index
                    vert = temp.vertices[vert_index]
                    rot = mathutils.Matrix.Rotation(math.radians(180), 4, 'Z')
                    vec = rot @ obj.matrix_local @ mathutils.Vector(vert.co)
                    col.write("%f %f %f    " % (-vec[1] * scale, vec[0] * scale, vec[2] * scale))

                    normal = mathutils.Vector([vert.normal[0], vert.normal[1], vert.normal[2], 0.0])
                    normal = rot @ obj.matrix_local @ normal
                    col.write("%f %f %f    " % (-normal[1], normal[0], normal[2]))

                    col.write("%f %f\n" % (0.0, 0.0))

            bpy.data.meshes.remove(temp)

        col.write("end\n")

    return True


def generate_qc(context, game_path):
    """Generate the QC for this model"""
    base = context.scene.BASE
    model = base.models[base.model_index]

    # deleting the old model so that the model viewer won't load it if you try to view it while it's still compiling
    model_path = game_path + os.sep + "models" + os.sep + model.name
    if os.path.isfile(model_path + ".dx90.vtx"): os.remove(model_path + ".dx90.vtx")
    if os.path.isfile(model_path + ".dx80.vtx"): os.remove(model_path + ".dx80.vtx")
    if os.path.isfile(model_path + ".sw.vtx"): os.remove(model_path + ".sw.vtx")
    if os.path.isfile(model_path + ".vvd"): os.remove(model_path + ".vvd")
    if os.path.isfile(model_path + ".mdl"): os.remove(model_path + ".mdl")
    if os.path.isfile(model_path + ".phy"): os.remove(model_path + ".phy")

    modelsrc_path = game_path + os.sep + "modelsrc" + os.sep + model.name + os.sep
    qc = open(modelsrc_path + "compile.qc", "w+")
    qc.write("$modelname \"" + model.name + "\"\n")
    qc.write("$body shell \"reference.smd\"\n")
    if any(mesh.kind == 'COLLISION' for mesh in model.meshes):
        qc.write("$collisionmodel \"collision.smd\" {\n\t$concave\n\t$maxconvexpieces 10000\n}\n")
    qc.write("$sequence idle \"reference.smd\"\n")
    qc.write("$cdmaterials \"" + os.sep + "\"\n")
    qc.write("$surfaceprop \"" + model.surface_prop + "\"\n")
    qc.write("$staticprop\n")

    if model.autocenter: qc.write("$autocenter\n")
    if model.mostly_opaque: qc.write("$mostlyopaque\n")

    qc.close()
    return True


# </functions>

# <operators>
class BASE_OT_ExportModel(bpy.types.Operator):
    """Export this model's meshes, generate a QC and compile it"""
    bl_idname = "base.export_model"
    bl_label = "Export Model"

    @classmethod
    def poll(cls, context):
        base = context.scene.BASE
        settings = base.settings
        games = settings.games
        game_index = settings.game_index

        if games and game_index >= 0:
            game = games[game_index]

            if game.path:
                models = base.models
                model_index = base.model_index

                if models and model_index >= 0:
                    model = models[model_index]

                    if model.name and model.meshes:
                        return not game.name == "Invalid Game"

        return False

    def execute(self, context):
        base = context.scene.BASE
        settings = base.settings
        games = settings.games
        game_index = settings.game_index
        game = games[game_index]

        model = base.models[base.model_index]
        model_path = game.path + os.sep + "modelsrc" + os.sep + model.name + os.sep
        if not os.path.exists(model_path): os.makedirs(model_path)

        if export_meshes(context, model_path) and generate_qc(context, game.path):
            args = [game.studiomdl, '-nop4', '-fullcollide', model_path + "compile.qc"]
            print(game.studiomdl + "    " + model_path + "compile.qc" + "\n")
            pipe = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while 1:
                code = pipe.returncode
                if code is None:
                    with open(model_path + "log.txt", "w+") as log:
                        log.write(pipe.communicate()[0].decode('utf'))
                else:
                    break
        return {'FINISHED'}
# </operators>
