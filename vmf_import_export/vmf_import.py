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
from ..material_import_export import vmt
from ..material_import_export import import_vtf
from . import driver
from ..utils.vpk_search import vpk

BRUSH_SCALE = 1

def find_file_in_vpks(vpk_lst, filepath):
    for i in vpk_lst:
        try:
            pak = vpk.open(i)
        except FileNotFoundError:
            continue
        try:
            k = filepath.rfind("/")
            pakfile = pak.get_file(filepath[:k] + "\\" + filepath[k+1:])
            if pakfile is not None:
                return pakfile
        except KeyError:
            continue


class ImportVMF(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Imports the VMF given a path"""
    bl_idname = "sourceops.import_vmf"
    bl_label = "Import VMF"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".vmf"

    filter_glob = bpy.props.StringProperty (
        default = "*.vmf",
        options = {'HIDDEN'}
    )

    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def create_mesh(mesh, col, mat_dict):
        bm_faces = []
        me = bpy.data.meshes.new('brush_mesh_PLACEHOLDER')
        ob = bpy.data.objects.new('brush_id_PLACEHOLDER', me)
        ob.show_name = False
        
        col.objects.link(ob)

        bm = bmesh.new()
        bm.from_mesh(me)

        obj_mats = {}

        for i, item in enumerate(mesh):
                
            face = item[0]
            num = item[1]
            if num == -1:
                raise Exception("Something went wrong")

            cur_index = len(obj_mats)
            try:
                cur_index = obj_mats[mat_dict[num]]
            except:
                obj_mats[mat_dict[num]]=len(obj_mats)
                ob.data.materials.append(mat_dict[num])
            
            new_face = []
            for vert in face:
                new_face.append(bm.verts.new((vert*BRUSH_SCALE).value))
            result = bmesh.ops.contextual_create(bm, geom=new_face)

            poly = result["faces"][0]
            poly.material_index = cur_index
            
            
            
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
        bm.to_mesh(me)
        


    def execute(self, context):
        game = common.get_game(context)


        searchpaths = []
        in_sp = False
        for line in open(game.gameinfo):
            
            if in_sp is False:
                if line.strip() == "SearchPaths":
                    in_sp = True
            elif line.strip() == "}":
                break
            else:
                if len(line.split()) > 1:
                    if line.strip()[0:2] != "//":
                        path = line.split()[1]
                        path = path.replace("|all_source_engine_paths|",
                                            game.game.replace("\\","/") + "/")
                        path = path.replace("|gameinfo_path|",
                                            game.mod.replace("\\","/") + "/")

                        searchpaths.append(path)
        
        materials_path = game.mod + "/materials/"
        
        file = self.properties.filepath

        vpks = []

        for p in searchpaths:
                if p[-4:]==".vpk":
                    vpks.append(p[:-4] + "_dir.vpk")
        for f in self.files:

            #print(f'Length: {len(searchpaths)}')
            for p in vpks:
                print(p)
                
            print(f'Trying to import {file}')
            #if not f.name.lower().endswith(".vmf"):
            #    continue
            meshes, tex_dict = driver.generate_meshes(file)

            vmf_col = bpy.data.collections.new(file.split("/")[-1].split("\\")[-1])
            bpy.context.collection.children.link(vmf_col)

            mat_dict = {}

            for num, tex in tex_dict.items():
                
                mat = find_file_in_vpks(vpks, "materials/" + tex + ".vmt")
                #print("materials/" + tex + ".vmt")
                if mat is not None:
                    #print("Found:" + tex)
                    material = vmt.VMT(file=mat, game_dir = Path(game.mod))
                    material.parse()
                else:
                    mat_path = materials_path + tex + ".vmt"

                    material = vmt.VMT(mat_path)
                    material.parse()

                b_mat = bpy.data.materials.new(name=tex.split("/")[-1])
                b_mat.use_nodes = True


                bsdf = b_mat.node_tree.nodes["Principled BSDF"]
                #pprint(material.textures)
                for key, val in material.textures.items():
                    
                    img = None
                    
                    if isinstance(val, str):
                        vtf_file = find_file_in_vpks(vpks, "materials/" + val.lower() + ".vtf")
                        img = import_vtf.import_texture_from_vpk(vtf_file, tex.split("/")[-1])
                    else:
                        img = import_vtf.import_texture(val)

                    if img is not None:
                        teximg = b_mat.node_tree.nodes.new('ShaderNodeTexImage')
                        teximg.image = img

                        if key.lower() == "$basetexture":
                            b_mat.node_tree.links.new(bsdf.inputs['Base Color'],
                                              teximg.outputs['Color'])

                            #context.selected_objects[0].data.materials.append(b_mat)
                            mat_dict[num] = b_mat

            
            for mesh in meshes:
                ImportVMF.create_mesh(mesh, vmf_col, mat_dict)
                

            bpy.ops.view3d.view_all()
            for a in bpy.context.screen.areas:
                if a.type == 'VIEW_3D':
                    for s in a.spaces:
                        if s.type == 'VIEW_3D':
                            s.clip_end = 100000 # Placeholder value until I make it work properly
            

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
