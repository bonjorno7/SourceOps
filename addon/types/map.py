import bpy
import bmesh
import mathutils
from .. pyvmf import pyvmf
import pathlib

class Plane:
    def __init__(self, vL):
        self.v1 = mathutils.Vector([vL[0].x, vL[0].y, vL[0].z])
        self.v2 = mathutils.Vector([vL[1].x, vL[1].y, vL[1].z])
        self.v3 = mathutils.Vector([vL[2].x, vL[2].y, vL[2].z])
        
        self.gen_ijk_form()
        
    def gen_ijk_form(self):
        onetotwo = self.v1 - self.v2
        onetothree = self.v1 - self.v3
    
        self.normal = onetotwo.cross(onetothree).normalized()*-1
        self.d = -self.normal.dot(self.v1)

class Map:

    def __init__(self, vmf, epsilon):
        self.vmf = vmf
        self.epsilon = epsilon
        
        self.generate_meshes()

    @staticmethod
    def get_intersection(p1, p2, p3):
        n1 = p1.normal    
        n2 = p2.normal
        n3 = p3.normal

        d1 = p1.d
        d2 = p2.d
        d3 = p3.d

        denom = n1.dot(n2.cross(n3))

        if abs(denom) < 10**-8:
            return None


        ret = ( ((n2.cross(n3)) * (d1))
               +((n3.cross(n1)) * (d2))
               +((n1.cross(n2)) * (d3))) / -denom
               
        return ret

    @staticmethod
    def round_to_nearest(val, base):
        return base * round(val/base)

    def generate_meshes(self):
        self.meshes = []
    
        for solid in self.vmf.get_solids():
            
            sides = solid.get_sides()
            polys = [[[]] for side in sides] # Double nested to make room for textures later on
            
            for i in range(0,len(sides)-2):
                for j in range(i,len(sides)-1):
                    for k in range(j, len(sides)):
                        if i != j and i != k and j != k:
                            p_i = Plane(sides[i].get_vertices())
                            p_j = Plane(sides[j].get_vertices())
                            p_k = Plane(sides[k].get_vertices())
                        
                            curVertex = self.get_intersection(p_i, p_j, p_k)
                            if curVertex is None:
                                continue
                                
                            legal = True
                            for m in sides:
                                p_m = Plane(m.get_vertices())
                                
                                if(p_m.normal.dot(curVertex) + p_m.d)>self.epsilon:
                                   legal = False
                            
                            if legal is True:
                               polys[i][0].append(curVertex)
                               polys[j][0].append(curVertex)
                               polys[k][0].append(curVertex)
            self.meshes.append(polys)

class MapToMesh:
    def __init__(self, map, brush_scale):
        self.map = map
        self.brush_scale = brush_scale
        
    def create_mesh(self, mesh, col, mat):
        bm_faces = []
        me = bpy.data.meshes.new('brush_mesh_PLACEHOLDER')
        ob = bpy.data.objects.new('brush_id_PLACEHOLDER', me)
        ob.show_name = False
        
        col.objects.link(ob)

        bm = bmesh.new()
        bm.from_mesh(me)

        obj_mats = {}
        
        indToNum = {}

        for i, item in enumerate(mesh):
                
            face = item[0]

            ob.data.materials.append(mat)
            
            new_face = []
            
            for vert in face:
                new_face.append(bm.verts.new(vert*self.brush_scale))
                
            result = bmesh.ops.contextual_create(bm, geom=new_face)

            if not result["faces"]:
                continue
            
            poly = result["faces"][0]
                
            
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01*self.brush_scale)
        
        bm.to_mesh(me)
        
        return me
        
    def import_meshes(self):
        b_mat = bpy.data.materials.new(name="testmat")
        b_mat.use_nodes = True
                
        bsdf = b_mat.node_tree.nodes["Principled BSDF"]
        
        vmf_col = bpy.data.collections.new("TEST")
        bpy.context.collection.children.link(vmf_col)
        
        for mesh in self.map.meshes:
            procMesh = self.create_mesh(mesh, vmf_col, b_mat)
            
        bpy.ops.view3d.view_all()
        for a in bpy.context.screen.areas:
            if a.type == 'VIEW_3D':
                for s in a.spaces:
                    if s.type == 'VIEW_3D':
                        s.clip_end = 100000 # Placeholder value until I make it work properly
        
        return {"FINISHED"}

        