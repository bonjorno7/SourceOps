# <import>
import os, subprocess
import bpy, bmesh, mathutils
from . import common
# </import>

# <functions>
def update_model_name(self, context):
    name = bpy.path.native_pathsep(self["name"])
    if name.lower().endswith(".mdl"):
        name = name[:-4]
    self["name"] = name

def update_matdir_name(self, context):
    self["name"] = bpy.path.native_pathsep(self["name"])
# </functions>

# <types>
class Mesh(bpy.types.PropertyGroup):
    """Properties for a mesh"""
    obj: bpy.props.PointerProperty(
        name = "Mesh Object",
        description = "Object that holds the data for this mesh",
        type = bpy.types.Object,
        poll = common.is_mesh,
    )

    kind: bpy.props.EnumProperty(
        name = "Mesh Type",
        description = "Whether this mesh should be Reference (visible) or Collision (tangible)",
        items = (
            ('REFERENCE', "REF", "Reference"),
            ('COLLISION', "COL", "Collision"),
        ),
    )

class MatDir(bpy.types.PropertyGroup):
    """Properties for a material folder"""
    name: bpy.props.StringProperty(
        name = "Material Folder",
        description = "Material path, eg models\\example",
        default = "models\\example",
        update = update_matdir_name,
    )

class Model(bpy.types.PropertyGroup):
    """Properties for a model"""
    meshes: bpy.props.CollectionProperty(type = Mesh)
    mesh_index: bpy.props.IntProperty(default = 0)

    matdirs: bpy.props.CollectionProperty(type = MatDir)
    matdir_index: bpy.props.IntProperty(default = 0)

    name: bpy.props.StringProperty(
        name = "Model Name",
        description = "Your model's path, eg example\\model (don't add the file extension)",
        default = "example\\model",
        update = update_model_name,
    )

    surface_property: bpy.props.EnumProperty(
        name = "Surface Property",
        description = "Choose the surface property of your model, this affects decals and how it sounds in game",
        items = common.surface_properties,
    )

    mostly_opaque: bpy.props.BoolProperty(
        name = "Has Glass",
        description = "$mostlyopaque, use this if your model has something transparent like glass",
        default = False,
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
        base = context.scene.BASE
        model = base.models[base.model_index]

        for o in context.selected_objects:
            if o.type == 'MESH':
                duplicate = False

                for m in model.meshes:
                    if m.obj == o:
                        duplicate = True

                if not duplicate:
                    model.meshes.add()
                    mesh = model.meshes[-1]
                    mesh.obj = o

                    if mesh.obj.name.find(".col") != -1:
                        mesh.kind = 'COLLISION'

        model.mesh_index = len(model.meshes) - 1
        return {'FINISHED'}

class MeshRemove(bpy.types.Operator):
    """Remove selected mesh from the list"""
    bl_idname = "base.mesh_remove"
    bl_label = "Remove Mesh"

    @classmethod
    def poll(cls, context):
        base = context.scene.BASE
        if len(base.models) > 0:
            model = base.models[base.model_index]
            return len(model.meshes) > 0
        return False

    def execute(self, context):
        base = context.scene.BASE
        model = base.models[base.model_index]
        model.meshes.remove(model.mesh_index)
        model.mesh_index = min(max(0, model.mesh_index - 1), len(model.meshes) - 1)
        return {'FINISHED'}

class MeshMove(bpy.types.Operator):
    """Move the selected mesh up or down in the list"""
    bl_idname = "base.mesh_move"
    bl_label = "Move Mesh"

    direction: bpy.props.EnumProperty(items = (
        ('UP', "Up", "Move the item up"),
        ('DOWN', "Down", "Move the item down"),
    ))

    @classmethod
    def poll(cls, context):
        base = context.scene.BASE
        model = base.models[base.model_index]
        return len(model.meshes) > 1

    def execute(self, context):
        base = context.scene.BASE
        model = base.models[base.model_index]
        neighbor = model.mesh_index + (-1 if self.direction == 'UP' else 1)
        model.meshes.move(neighbor, model.mesh_index)
        list_length = len(model.meshes) - 1
        model.mesh_index = max(0, min(neighbor, list_length))
        return {'FINISHED'}
# </mesh list>

# <matdir list>
class MatDirList(bpy.types.UIList):
    """List of material paths for this model"""
    bl_idname = "base.matdir_list"
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text = "", emboss = False, translate = False)

class MatDirAdd(bpy.types.Operator):
    """Add a new material path to this model"""
    bl_idname = "base.matdir_add"
    bl_label = "Add Material Folder"

    def execute(self, context):
        base = context.scene.BASE
        model = base.models[base.model_index]
        model.matdirs.add()
        model.matdir_index = len(model.matdirs) - 1
        return {'FINISHED'}

class MatDirRemove(bpy.types.Operator):
    """Remove the selected material path from this model"""
    bl_idname = "base.matdir_remove"
    bl_label = "Remove Material Folder"

    @classmethod
    def poll(cls, context):
        base = context.scene.BASE
        if len(base.models) > 0:
            model = base.models[base.model_index]
            return len(model.matdirs) > 0
        return False

    def execute(self, context):
        base = context.scene.BASE
        model = base.models[base.model_index]
        model.matdirs.remove(model.matdir_index)
        model.matdir_index = min(
            max(0, model.matdir_index - 1),
            len(model.matdirs) - 1
        )
        return {'FINISHED'}

class MatDirMove(bpy.types.Operator):
    """Move the selected material folder up or down in the list"""
    bl_idname = "base.matdir_move"
    bl_label = "Move Material Folder"

    direction: bpy.props.EnumProperty(items = (
        ('UP', "Up", "Move the item up"),
        ('DOWN', "Down", "Move the item down"),
    ))

    @classmethod
    def poll(cls, context):
        base = context.scene.BASE
        model = base.models[base.model_index]
        return len(model.matdirs) > 1

    def execute(self, context):
        base = context.scene.BASE
        model = base.models[base.model_index]
        neighbor = model.matdir_index + (-1 if self.direction == 'UP' else 1)
        model.matdirs.move(neighbor, model.matdir_index)
        list_length = len(model.matdirs) - 1
        model.matdir_index = max(0, min(neighbor, list_length))
        return {'FINISHED'}
# </matdir list>

# <model list>
class ModelList(bpy.types.UIList):
    """List of models"""
    bl_idname = "base.model_list"
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text = "", emboss = False, translate = False)

class ModelAdd(bpy.types.Operator):
    """Create a model"""
    bl_idname = "base.model_add"
    bl_label = "Add Model"

    def execute(self, context):
        base = context.scene.BASE
        base.models.add()
        base.model_index = len(base.models) - 1
        return {'FINISHED'}

class ModelRemove(bpy.types.Operator):
    """Remove the selected model"""
    bl_idname = "base.model_remove"
    bl_label = "Remove Model"

    @classmethod
    def poll(cls, context):
        base = context.scene.BASE
        return len(base.models) > 0

    def execute(self, context):
        base = context.scene.BASE
        base.models.remove(base.model_index)
        base.model_index = min(
            max(0, base.model_index - 1),
            len(base.models) - 1
        )
        return {'FINISHED'}

class ModelCopy(bpy.types.Operator):
    """Copy this model, everything except the list of meshes"""
    bl_idname = "base.model_copy"
    bl_label = "Copy Model"

    @classmethod
    def poll(cls, context):
        base = context.scene.BASE
        return len(base.models) > 0

    def execute(self, context):
        base = context.scene.BASE
        old = base.models[base.model_index]
        base.models.add()
        new = base.models[-1]

        new.name = old.name
        new.surface_property = old.surface_property
        new.mostly_opaque = old.mostly_opaque

        for matdir in old.matdirs:
            new.matdirs.add()
            new.matdirs[-1].name = matdir.name

        base.model_index = len(base.models) - 1
        return {'FINISHED'}

class ModelMove(bpy.types.Operator):
    """Move the selected model up or down in the list"""
    bl_idname = "base.model_move"
    bl_label = "Move Model"

    direction: bpy.props.EnumProperty(items = (
        ('UP', "Up", "Move the item up"),
        ('DOWN', "Down", "Move the item down"),
    ))

    @classmethod
    def poll(cls, context):
        base = context.scene.BASE
        return len(base.models) > 1

    def execute(self, context):
        base = context.scene.BASE
        neighbor = base.model_index + (-1 if self.direction == 'UP' else 1)
        base.models.move(neighbor, base.model_index)
        list_length = len(base.models) - 1
        base.model_index = max(0, min(neighbor, list_length))
        return {'FINISHED'}
# </model list>

# <panels>
class ModelExportPanel(bpy.types.Panel):
    bl_idname = "base.model_export_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Model Export"

    def draw_header(self, context):
        self.layout.label(icon = 'EXPORT')

    def draw(self, context):
        pass

class ModelPanel(bpy.types.Panel):
    bl_parent_id = "base.model_export_panel"
    bl_idname = "base.model_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Models"

    def draw_header(self, context):
        self.layout.label(icon = 'CUBE')

    def draw(self, context):
        row = self.layout.row()
        row.template_list("base.model_list", "", context.scene.BASE, "models", context.scene.BASE, "model_index", rows = 5)
        col = row.column(align = True)
        col.operator("base.model_add", text = "", icon = 'ADD')
        col.operator("base.model_remove", text = "", icon = 'REMOVE')
        col.separator()
        col.operator("base.model_copy", text = "", icon = 'COPYDOWN')
        col.separator()
        col.operator("base.model_move", text = "", icon = 'TRIA_UP').direction = 'UP'
        col.operator("base.model_move", text = "", icon = 'TRIA_DOWN').direction = 'DOWN'

        models = context.scene.BASE.models
        model_index = context.scene.BASE.model_index
        if models and model_index >= 0:
            model = models[model_index]
            common.add_prop(self.layout, "Surface", model, "surface_property")
            self.layout.prop(model, "mostly_opaque")

            flow = self.layout.grid_flow(even_columns=True)
            col = flow.column()
            col.operator("base.model_export")
            col = flow.column()
            col.operator("base.model_view")

class MeshPanel(bpy.types.Panel):
    bl_parent_id = "base.model_export_panel"
    bl_idname = "base.mesh_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Meshes"

    @classmethod
    def poll(cls, context):
        models = context.scene.BASE.models
        model_index = context.scene.BASE.model_index
        return models and model_index >= 0

    def draw_header(self, context):
        self.layout.label(icon = 'MESH_DATA')

    def draw(self, context):
        models = context.scene.BASE.models
        model_index = context.scene.BASE.model_index
        model = models[model_index]

        row = self.layout.row()
        row.template_list("base.mesh_list", "", model, "meshes", model, "mesh_index", rows = 4)
        col = row.column(align = True)
        col.operator("base.mesh_add", text = "", icon = 'ADD')
        col.operator("base.mesh_remove", text = "", icon = 'REMOVE')
        col.separator()
        col.operator("base.mesh_move", text = "", icon = 'TRIA_UP').direction = 'UP'
        col.operator("base.mesh_move", text = "", icon = 'TRIA_DOWN').direction = 'DOWN'

class MatDirPanel(bpy.types.Panel):
    bl_parent_id = "base.model_export_panel"
    bl_idname = "base.matdir_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Material Folders"

    @classmethod
    def poll(cls, context):
        models = context.scene.BASE.models
        model_index = context.scene.BASE.model_index
        return models and model_index >= 0

    def draw_header(self, context):
        self.layout.label(icon = 'FILE_FOLDER')

    def draw(self, context):
        models = context.scene.BASE.models
        model_index = context.scene.BASE.model_index
        model = models[model_index]

        row = self.layout.row()
        row.template_list("base.matdir_list", "", model, "matdirs", model, "matdir_index", rows = 4)
        col = row.column(align = True)
        col.operator("base.matdir_add", text = "", icon = 'ADD')
        col.operator("base.matdir_remove", text = "", icon = 'REMOVE')
        col.separator()
        col.operator("base.matdir_move", text = "", icon = 'TRIA_UP').direction = 'UP'
        col.operator("base.matdir_move", text = "", icon = 'TRIA_DOWN').direction = 'DOWN'
# </panels>

# <operators>
class ModelExport(bpy.types.Operator):
    """Export this model's meshes, generate a QC and compile it"""
    bl_idname = "base.model_export"
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
            temp.calc_normals_split()

            for poly in temp.polygons:
                material_name = "no_material"
                if poly.material_index < len(obj.material_slots):
                    material = obj.material_slots[poly.material_index].material
                    if material != None: material_name = material.name
                ref.write(material_name + "\n")

                for index in range(3):
                    ref.write("0" + "    ")
                    loop_index = poly.loop_indices[index]
                    loop = temp.loops[loop_index]

                    vert_index = loop.vertex_index
                    vert = temp.vertices[vert_index]
                    vec = obj.matrix_local @ mathutils.Vector(vert.co)
                    ref.write(str(-vec[1] * scale) + " " + str(vec[0] * scale) + " " + str(vec[2] * scale) + "    ")

                    normal = loop.normal
                    ref.write(str(-normal[1]) + " " + str(normal[0]) + " " + str(normal[2]) + "    ")

                    if temp.uv_layers:
                        uv_layer = [layer for layer in temp.uv_layers if layer.active_render][0]
                        uv_loop = uv_layer.data[loop_index]
                        uv = uv_loop.uv
                        ref.write(str(uv[0]) + " " + str(uv[1]) + "\n")
                    else:
                        ref.write(str(0) + " " + str(0) + "\n")

            temp.free_normals_split()
            bpy.data.meshes.remove(temp)

        ref.write("end\n")
        ref.close()

        col = open(directory + "collision.smd", "w+")
        self.write_smd_header(col)
        col.write("triangles\n")

        for obj in collisions:
            temp = obj.to_mesh(context.depsgraph, apply_modifiers = True, calc_undeformed = False)
            common.triangulate(temp)

            for poly in temp.polygons:
                col.write("no_material" + "\n")

                for index in range(3):
                    col.write("0" + "    ")
                    loop_index = poly.loop_indices[index]
                    loop = temp.loops[loop_index]

                    vert_index = loop.vertex_index
                    vert = temp.vertices[vert_index]
                    vec = obj.matrix_local @ mathutils.Vector(vert.co)
                    col.write(str(-vec[1] * scale) + " " + str(vec[0] * scale) + " " + str(vec[2] * scale) + "    ")

                    normal = vert.normal
                    col.write(str(-normal[1]) + " " + str(normal[0]) + " " + str(normal[2]) + "    ")

                    col.write(str(0) + " " + str(0))
                    col.write("\n")

            bpy.data.meshes.remove(temp)

        col.write("end\n")
        col.close()

        return True

    def generate_qc(self, context, game_path):
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
            qc.write("$collisionmodel \"collision.smd\" { $concave $maxconvexpieces 10000 }\n")
        qc.write("$sequence idle \"reference.smd\"\n")
        for matdir in model.matdirs:
            qc.write("$cdmaterials \"" + matdir.name + "\"\n")
        qc.write("$surfaceprop \"" + model.surface_property + "\"\n")
        qc.write("$staticprop\n")

        if model.mostly_opaque:
            qc.write("$mostlyopaque\n")

        qc.close()
        return True

    def execute(self, context):
        settings = context.scene.BASE.settings
        game_path, _ = os.path.split(settings.games[settings.game_index].path)
        model = context.scene.BASE.models[context.scene.BASE.model_index]
        model_path = game_path + os.sep + "modelsrc" + os.sep + model.name + os.sep
        if not os.path.exists(model_path): os.makedirs(model_path)

        if self.export_meshes(context, model_path) and self.generate_qc(context, game_path):
            path, _ = os.path.split(game_path)
            studiomdl = path + "\\bin\\studiomdl.exe"
            print(studiomdl + "    " + model_path + "compile.qc" + "\n")
            subprocess.Popen([studiomdl, model_path + "compile.qc"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)

            #log = open(model_path + "log.txt", "w+")
            #log.write(stdout.decode("utf-8"))
            #log.close()
        return {'FINISHED'}

class ModelView(bpy.types.Operator):
    """Open this model in HLMV"""
    bl_idname = "base.model_view"
    bl_label = "View Model"

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
            print(hlmv + "    " + model_path + "\n")
            subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        return {'FINISHED'}
# </operators>