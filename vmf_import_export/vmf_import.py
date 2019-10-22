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
from . import driver



class ImportVMF(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Imports the VMF given a path"""
    bl_idname = "sourceops.import_vmf"
    bl_label = "Import VMF"
    bl_options = {"REGISTER", "UNDO"}

    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def create_mesh(mesh):
        bm_faces = []
        me = bpy.data.meshes.new('myMesh')
        ob = bpy.data.objects.new('myObject', me)
        ob.show_name = True
        bpy.context.collection.objects.link(ob)

        bm = bmesh.new()
        bm.from_mesh(me)
        for face in mesh:
            for i, vert in enumerate(face):
                face[i] = bm.verts.new(vert.value)
            bmesh.ops.contextual_create(bm, geom=face)
        bm.to_mesh(me)
            

    def execute(self, context):
        # game = common.get_game(context)
        # mod_folder = None if not game else Path(game.mod)
        file = self.properties.filepath
        for f in self.files:
            print(f'Trying to import {file}')
            #if not f.name.lower().endswith(".vmf"):
            #    continue
            meshes = driver.generate_meshes(file)
            print(f'Num objects = {len(meshes)}')
            print(f'Num faces in object 1 = {len(meshes[0])}')
            print(f'Num verts in object 1 face 1 = {len(meshes[0][0])}')

            for mesh in meshes:
                ImportVMF.create_mesh(mesh)

        return {"FINISHED"}


class VMFImportPanel(bpy.types.Panel):
    bl_idname = "SOURCEOPS_PT_VMFImportPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "SourceOps"
    bl_label = "VMF Importer"

    def draw_header(self, context):
        self.layout.label(icon='FILE_IMAGE')

    def draw(self, context):
        self.layout.operator(ImportVMF.bl_idname)
