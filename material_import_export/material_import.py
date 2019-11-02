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

            material = vmt.VMT(folder / f.name, mod_folder)
            material.parse()

            b_mat = bpy.data.materials.new(name=f.name[:-4])
            b_mat.use_nodes = True

            bsdf = b_mat.node_tree.nodes["Principled BSDF"]
            # all used textures are in material.textures
            # TODO: implement cycles material builder
            #pprint(material.textures)
            for key, tex in material.textures.items():
                img=import_vtf.import_texture(tex)

                teximg = b_mat.node_tree.nodes.new('ShaderNodeTexImage')
                teximg.image = img

                if key.lower() == "$basetexture":
                    b_mat.node_tree.links.new(bsdf.inputs['Base Color'],
                                              teximg.outputs['Color'])

                    context.selected_objects[0].data.materials.append(b_mat)
                    
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
