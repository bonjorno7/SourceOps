import os
import subprocess
import math
from pathlib import Path
from pprint import pprint
import bpy
import bmesh
import mathutils
import bpy_extras
from .. import common
from . import vmt
from . import import_vtf


class ImportMaterial(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Create materials with the names of the paths to your VMTs relative to the materials folder and import the VTFs as PNGs"""
    bl_idname = "sourceops.import_material"
    bl_label = "Import Materials"
    bl_options = {"REGISTER", "UNDO"}

    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def clear_node_tree(self, node_tree):
        node_tree.nodes.clear()
        node_tree.links.clear()
        return node_tree

    def output_node(self, nodes, x, y):
        node = nodes.new("ShaderNodeOutputMaterial")
        node.location = [x, y]
        node.select = False
        return node

    def principled_node(self, nodes, x, y):
        node = nodes.new("ShaderNodeBsdfPrincipled")
        node.location = [x, y]
        node.select = False
        return node

    def normal_map_node(self, nodes, x, y):
        node = nodes.new("ShaderNodeNormalMap")
        node.location = [x, y]
        node.select = False
        node.hide = True
        return node

    def image_node(self, nodes, image, x, y):
        node = nodes.new("ShaderNodeTexImage")
        node.location = [x, y]
        node.select = False
        node.image = image
        node.hide = True
        return node

    def socket(self, node, identifier):
        for socket in node.outputs:
            if socket.identifier == identifier:
                return socket

        for socket in node.inputs:
            if socket.identifier == identifier:
                return socket

    def execute(self, context):
        game = common.get_game(context)
        if not game or not game.verify():
            self.report({"ERROR"}, "Game is invalid")
            return {'CANCELLED'}

        mod_folder = Path(game.mod)
        folder = Path(self.properties.filepath).parent
        for f in self.files:
            print(f"Trying to import {f.name}")
            if not f.name.lower().endswith(".vmt"):
                continue

            valve_mat = vmt.VMT(folder / f.name, mod_folder)
            valve_mat.parse()

            # all used textures are in valve_mat.textures
            pprint(valve_mat.textures)

            images = {}
            for tex_type, tex in valve_mat.textures.items():
                images[tex_type] = import_vtf.import_texture(tex)
                # names = import_vtf.import_texture(tex)
                # for n in names:
                #    images.append(bpy.data.images[n])

            mats_folder = Path(game.mod + os.sep + "materials" + os.sep)
            blender_mat_name = Path(valve_mat.filepath).relative_to(mats_folder)
            mat = bpy.data.materials.new(name=str(blender_mat_name)[:-4])

            mat.use_nodes = True
            node_tree = self.clear_node_tree(mat.node_tree)
            nodes, links = node_tree.nodes, node_tree.links

            node_output = self.output_node(nodes, 0, 0)
            node_principled = self.principled_node(nodes, -400, 0)
            node_normal_map = self.normal_map_node(nodes, -600, -520)

            links.new(self.socket(node_output, "Surface"), self.socket(node_principled, "BSDF"))
            links.new(self.socket(node_principled, "Normal"), self.socket(node_normal_map, "Normal"))

            for image_type, image in images.items():
                node_image = self.image_node(nodes, image, -900, -520)
                links.new(self.socket(node_image, "Color"), self.socket(node_principled, "Base Color"))

        return {"FINISHED"}


class MaterialImportPanel(bpy.types.Panel):
    bl_idname = "SOURCEOPS_PT_MaterialImportPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "SourceOps"
    bl_label = "Material Importer"

    def draw_header(self, context):
        self.layout.label(icon='FILE_IMAGE')

    def draw(self, context):
        self.layout.operator(ImportMaterial.bl_idname)
