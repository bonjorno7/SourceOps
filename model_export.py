# <import>
import os, subprocess
import bpy, bmesh
from . import common
# </import>

# </types>
class Mesh(bpy.types.PropertyGroup):
    """Properties for a mesh"""
    obj: bpy.props.PointerProperty(
        type = bpy.types.Object,
        poll = common.is_mesh,
    )

    kind: bpy.props.EnumProperty(items = (
        ('REFERENCE', "REF", "Reference"),
        ('COLLISION', "COL", "Collision"),
    ))

class MatDir(bpy.types.PropertyGroup):
    """Properties for a material folder"""
    name: bpy.props.StringProperty(
        name = "",
        description = "Material path, eg models\\props\\example",
        default = "models\\props\\example",
    )

class Model(bpy.types.PropertyGroup):
    """Properties for a model"""
    meshes: bpy.props.CollectionProperty(type = Mesh)
    mesh_index: bpy.props.IntProperty(name = "", default = 0)

    matdirs: bpy.props.CollectionProperty(type = MatDir)
    matdir_index: bpy.props.IntProperty(name = "", default = 0)

    name: bpy.props.StringProperty(
        name = "",
        description = "Your model's path, eg props\\example\\model (do not add the file extension)",
        default = "props\\example\\model",
    )

    surface_property: bpy.props.EnumProperty(
        name = "",
        description = "Choose the substance your model is made out of, this affects decals and how it sounds in game",
        items = common.surface_properties,
    )

    weighted_normals: bpy.props.BoolProperty(
        name = "",
        description = "Should this model use weighted normals, meaning the larger the face the bigger influence it has on the vertex normal",
        default = True,
    )
# </types>

# <mesh list>
class MeshList(bpy.types.UIList):
    """List of meshes for this model"""
    bl_idname = "base.mesh_list"
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row().split(factor = 0.6)
        row.label(text = item.obj.name)
        row.split().row().prop(item, "kind", expand = True)

class MeshAdd(bpy.types.Operator):
    """Add selected objects as meshes to this model"""
    bl_idname = "base.mesh_add"
    bl_label = "Add Mesh"

    def execute(self, context):
        model = context.scene.BASE.models[context.scene.BASE.model_index]
        for o in context.selected_objects:
            if o.type == 'MESH':
                duplicate = False
                for m in model.meshes:
                    if m.obj == o:
                        duplicate = True
                if not duplicate:
                    model.meshes.add()
                    mesh = model.meshes[len(model.meshes) - 1]
                    mesh.obj = o
        return {'FINISHED'}

class MeshRemove(bpy.types.Operator):
    """Remove selected mesh from the list"""
    bl_idname = "base.mesh_remove"
    bl_label = "Remove Mesh"

    @classmethod
    def poll(cls, context):
        model = context.scene.BASE.models[context.scene.BASE.model_index]
        return len(model.meshes) > 0

    def execute(self, context):
        model = context.scene.BASE.models[context.scene.BASE.model_index]
        model.meshes.remove(model.mesh_index)
        model.mesh_index = min(max(0, model.mesh_index - 1), len(model.meshes) - 1)
        return {'FINISHED'}
# </mesh list>

# <matdir list>
class MatDirList(bpy.types.UIList):
    """List of material paths for this model"""
    bl_idname = "base.matdir_list"
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", emboss = False, translate = False)

class MatDirAdd(bpy.types.Operator):
    """Add a new material path to this model"""
    bl_idname = "base.matdir_add"
    bl_label = "Add Material Folder"

    def execute(self, context):
        model = context.scene.BASE.models[context.scene.BASE.model_index]
        model.matdirs.add()
        return {'FINISHED'}

class MatDirRemove(bpy.types.Operator):
    """Remove the selected material path from this model"""
    bl_idname = "base.matdir_remove"
    bl_label = "Remove Material Folder"

    @classmethod
    def poll(cls, context):
        model = context.scene.BASE.models[context.scene.BASE.model_index]
        return len(model.matdirs) > 0

    def execute(self, context):
        model = context.scene.BASE.models[context.scene.BASE.model_index]
        model.matdirs.remove(model.matdir_index)
        model.matdir_index = min(max(0, model.matdir_index - 1), len(model.matdirs) - 1)
        return {'FINISHED'}
# </matdir list>

# <model list>
class ModelList(bpy.types.UIList):
    """List of models"""
    bl_idname = "base.model_list"
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", emboss = False, translate = False)

class ModelAdd(bpy.types.Operator):
    """Create a model"""
    bl_idname = "base.model_add"
    bl_label = "Add Model"

    def execute(self, context):
        context.scene.BASE.models.add()
        return {'FINISHED'}

class ModelRemove(bpy.types.Operator):
    """Remove the selected model"""
    bl_idname = "base.model_remove"
    bl_label = "Remove Model"

    @classmethod
    def poll(cls, context):
        return len(context.scene.BASE.models) > 0

    def execute(self, context):
        context.scene.BASE.models.remove(context.scene.BASE.model_index)
        context.scene.BASE.model_index = min(
            max(0, context.scene.BASE.model_index - 1),
            len(context.scene.BASE.models) - 1
        )
        return {'FINISHED'}
# </model list>

# <panel>
class ModelExportPanel(bpy.types.Panel):
    bl_idname = "base.model_export_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Model Export"

    def draw(self, context):
        box = self.layout.box()
        box.label(text = "Models", icon = 'CUBE')
        row = box.row()
        row.template_list("base.model_list", "", context.scene.BASE, "models", context.scene.BASE, "model_index", rows = 3)
        col = row.column(align = True)
        col.operator("base.model_add", text = "", icon = 'ADD')
        col.operator("base.model_remove", text = "", icon = 'REMOVE')

        models = context.scene.BASE.models
        model_index = context.scene.BASE.model_index
        if models and model_index >= 0:
            model = models[model_index]

            common.add_prop(box, "Surface Property", model, "surface_property")
            common.add_prop(box, "Weighted Normals", model, "weighted_normals")

            box = self.layout.box()
            box.label(text = "Meshes", icon = 'MESH_DATA')
            row = box.row()
            row.template_list("base.mesh_list", "", model, "meshes", model, "mesh_index", rows = 3)
            col = row.column(align = True)
            col.operator("base.mesh_add", text = "", icon = 'ADD')
            col.operator("base.mesh_remove", text = "", icon = 'REMOVE')

            box = self.layout.box()
            box.label(text = "Material Folders", icon = 'FILE_FOLDER')
            row = box.row()
            row.template_list("base.matdir_list", "", model, "matdirs", model, "matdir_index", rows = 3)
            col = row.column(align = True)
            col.operator("base.matdir_add", text = "", icon = 'ADD')
            col.operator("base.matdir_remove", text = "", icon = 'REMOVE')

            box = self.layout.box()
            box.label(text = "Export", icon = 'FILE')
            box.operator("base.model_export")
            box.operator("base.model_view")
# </panel>

# <operators>
class ModelExport(bpy.types.Operator):
    """Export this model's meshes, generate a QC and compile it"""
    bl_idname = "base.model_export"
    bl_label = "Export and Compile"

    @classmethod
    def poll(cls, context):
        settings = context.scene.BASE.settings
        games = settings.games
        game_index = settings.game_index

        if games and game_index >= 0:
            game = games[game_index]

            if game.path:
                models = context.scene.BASE.models
                model_index = context.scene.BASE.model_index

                if models and model_index >= 0:
                    model = models[model_index]
                    return model.name and model.meshes and model.matdirs

        return False

    def refresh_meshes(self, model):
        """Refresh the list of meshes for this model, remove ones that don't exist anymore"""
        meshes_to_remove = []
        for i, m in enumerate(model.meshes):
            if not m.obj.users_scene:
                meshes_to_remove.append(i)
        for i in reversed(meshes_to_remove):
            model.meshes.remove(i)

    def write_smd_header(self, smd):
        """Write the header for this SMD file, including the required dummy skeleton and animation data"""
        smd.write("version 1\n")
        smd.write("nodes\n")
        smd.write("0 \"blender_implicit\" -1\n")
        smd.write("end\n")
        smd.write("skeleton\n")
        smd.write("time 0\n")
        smd.write("0" + "    ")
        smd.write(str(0.0) + " " + str(0.0) + " " + str(0.0) + "    ")
        smd.write(str(0.0) + " " + str(0.0) + " " + str(0.0) + "\n")
        smd.write("end\n")

    def export_meshes(self, context, directory):
        """Export this model's meshes as SMD"""
        settings = context.scene.BASE.settings
        scale = settings.scale
        model = context.scene.BASE.models[context.scene.BASE.model_index]
        self.refresh_meshes(model)
        if not model.meshes: return None

        references = []
        collisions = []

        for mesh in model.meshes:
            if mesh.kind == 'REFERENCE':
                references.append(mesh.obj)
            if mesh.kind == 'COLLISION':
                collisions.append(mesh.obj)

        ref = open(directory + "reference.smd", "w+")
        self.write_smd_header(ref)
        ref.write("triangles\n")

        for obj in references:
            temp = obj.to_mesh(context.depsgraph, apply_modifiers = True, calc_undeformed = False)
            common.triangulate(temp)
            common.split_sharp(temp)
            bm = bmesh.new()
            bm.from_mesh(temp)

            for face in bm.faces:
                material_name = "no_material"
                if face.material_index < len(obj.material_slots):
                    material = obj.material_slots[face.material_index].material
                    if material != None: material_name = material.name
                ref.write(material_name + "\n")

                for index, vert in enumerate(face.verts):
                    ref.write("0" + "    ")
                    ref.write(str(-vert.co[1] * scale) + " " + str(vert.co[0] * scale) + " " + str(vert.co[2] * scale) + "    ")

                    normal = common.weighted_normal(vert) if model.weighted_normals else vert.normal
                    ref.write(str(-normal[1]) + " " + str(normal[0]) + " " + str(normal[2]) + "    ")

                    uv_layers = bm.loops.layers.uv
                    if uv_layers:
                        uv = face.loops[index][uv_layers[0]].uv
                        ref.write(str(uv[0]) + " " + str(uv[1]))
                    else: ref.write(str(0) + " " + str(0))
                    ref.write("\n")

            bm.free()
            del temp

        ref.write("end\n")
        ref.close()

        col = open(directory + "collision.smd", "w+")
        self.write_smd_header(col)
        col.write("triangles\n")

        for obj in collisions:
            temp = obj.to_mesh(context.depsgraph, apply_modifiers = True, calc_undeformed = False)
            common.triangulate(temp)
            bm = bmesh.new()
            bm.from_mesh(temp)

            for face in bm.faces:
                col.write("no_material" + "\n")

                for index, vert in enumerate(face.verts):
                    col.write("0" + "    ")
                    col.write(str(-vert.co[1] * scale) + " " + str(vert.co[0] * scale) + " " + str(vert.co[2] * scale) + "    ")

                    normal = vert.normal
                    col.write(str(-normal[1]) + " " + str(normal[0]) + " " + str(normal[2]) + "    ")

                    col.write(str(0) + " " + str(0))
                    col.write("\n")

            bm.free()
            del temp

        col.write("end\n")
        col.close()

        return True

    def generate_qc(self, context, directory):
        """Generate the QC for this model"""
        model = context.scene.BASE.models[context.scene.BASE.model_index]
        modelname = model.name
        if not modelname.lower().endswith(".mdl"):
            modelname += ".mdl"

        qc = open(directory + "compile.qc", "w+")
        qc.write("$modelname \"" + modelname + "\"\n")
        qc.write("$body shell \"reference.smd\"\n")
        if any(mesh.kind == 'COLLISION' for mesh in model.meshes):
            qc.write("$collisionmodel \"collision.smd\" { $concave $maxconvexpieces 4500 }\n")
        qc.write("$sequence idle \"reference.smd\"\n")
        for matdir in model.matdirs: qc.write("$cdmaterials \"" + matdir.name + "\"\n")
        qc.write("$surfaceprop \"" + model.surface_property + "\"\n")
        qc.write("$staticprop")
        qc.close()
        return True

    def execute(self, context):
        settings = context.scene.BASE.settings
        game_path, _ = os.path.split(settings.games[settings.game_index].path)
        model = context.scene.BASE.models[context.scene.BASE.model_index]
        model_path = game_path + os.sep + "modelsrc" + os.sep + model.name + os.sep
        if not os.path.exists(model_path): os.makedirs(model_path)

        if self.export_meshes(context, model_path) and self.generate_qc(context, model_path):
            path, _ = os.path.split(game_path)
            studiomdl = path + "\\bin\\studiomdl.exe"
            print(studiomdl + " " + model_path + "compile.qc" + "\n")
            process = subprocess.Popen([studiomdl, model_path + "compile.qc"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            stdout, stderr = process.communicate()

            log = open(model_path + "log.txt", "w+")
            log.write(stdout.decode("utf-8"))
            log.close()
        return {'FINISHED'}

class ModelView(bpy.types.Operator):
    """Open this model in HLMV"""
    bl_idname = "base.model_view"
    bl_label = "View Compiled Model"

    @classmethod
    def poll(cls, context):
        settings = context.scene.BASE.settings
        games = settings.games
        game_index = settings.game_index

        if games and game_index >= 0:
            game = games[game_index]

            if game.path:
                models = context.scene.BASE.models
                model_index = context.scene.BASE.model_index

                if models and model_index >= 0:
                    model = models[model_index]
                    return model.name and model.meshes and model.matdirs

        return False

    def execute(self, context):
        settings = context.scene.BASE.settings
        game_path, _ = os.path.split(settings.games[settings.game_index].path)
        model = context.scene.BASE.models[context.scene.BASE.model_index]
        model_path = game_path + os.sep + "models" + os.sep + model.name + ".mdl"

        print(model_path + "\n")
        if os.path.isfile(model_path):
            path, _ = os.path.split(game_path)
            hlmv = path + "\\bin\\hlmv.exe"
            args = [hlmv, "-game", game_path, model_path]
            subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        return {'FINISHED'}
# </operators>