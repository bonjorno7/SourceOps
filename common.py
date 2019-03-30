# <import>
import os
import bpy, bmesh
import mathutils
# </import>

# <functions>
def is_mesh(self, obj):
    """Return whether the object is a mesh type"""
    return obj.type == 'MESH'

def is_curve(self, obj):
    """Return whether the object is a curve type"""
    return obj.type == 'CURVE'

def add_prop(layout, label, scope, prop):
    """Add a property to a panel with a label before it"""
    row = layout.row().split(factor = 0.5)
    row.label(text = label)
    row.split().row().prop(scope, prop, text = "")

def add_enum(layout, label, scope, prop):
    """Add an expanded emum property to a panel with a label before it"""
    row = layout.row().split(factor = 0.5)
    row.label(text = label)
    row.split().row().prop(scope, prop, expand = True)

def triangulate(me):
    """Triangulate the mesh"""
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces = bm.faces)
    bm.to_mesh(me)
    bm.free()

def find_collection(context, item):
    """Return the first collection this item is in, if none return the scene collection"""
    collections = item.users_collection
    if len(collections) > 0:
        return collections[0]
    return context.scene.collection
# </functions>

# <variables>
dir_up = os.pardir + os.sep + os.pardir

surface_properties = [
    ("default", "default", ""),
    ("default_silent", "default_silent", ""),
    ("floatingstandable", "floatingstandable", ""),
    ("item", "item", ""),
    ("ladder", "ladder", ""),
    ("no_decal", "no_decal", ""),
    ("player", "player", ""),
    ("player_control_clip", "player_control_clip", ""),
    ("baserock", "baserock", "Don't use this one, wiki says it\'s missing"),
    ("boulder", "boulder", "Don't use this one, wiki says it causes problems when used on models"),
    ("brick", "brick", ""),
    ("concrete", "concrete", ""),
    ("concrete_block", "concrete_block", ""),
    ("rock", "rock", ""),
    ("canister", "canister", ""),
    ("chain", "chain", ""),
    ("chainlink", "chainlink", ""),
    ("combine_metal", "combine_metal", ""),
    ("crowbar", "crowbar", ""),
    ("floating_metal_barrel", "floating_metal_barrel", ""),
    ("grenade", "grenade", ""),
    ("gunship", "gunship", ""),
    ("metal", "metal", ""),
    ("metal_barrel", "metal_barrel", ""),
    ("metal_bouncy", "metal_bouncy", ""),
    ("metal_box", "metal_box", ""),
    ("metal_seafloorcar", "metal_seafloorcar", ""),
    ("metalgrate", "metalgrate", ""),
    ("metalpanel", "metalpanel", ""),
    ("metalvent", "metalvent", ""),
    ("metalvehicle", "metalvehicle", ""),
    ("paintcan", "paintcan", ""),
    ("popcan", "popcan", ""),
    ("roller", "roller", ""),
    ("slipperymetal", "slipperymetal", ""),
    ("solidmetal", "solidmetal", ""),
    ("strider", "strider", ""),
    ("weapon", "weapon", ""),
    ("wood", "wood", ""),
    ("wood_box", "wood_box", ""),
    ("wood_crate", "wood_crate", "Doesn't work in EP2, works in L4D/L4D2. CS:GO and Portal 2 haven't been tested yet"),
    ("wood_furniture", "wood_furniture", ""),
    ("wood_lowdensity", "wood_lowdensity", "Doesn't work in EP2, works in L4D/L4D2. CS:GO and Portal 2 haven't been tested yet"),
    ("wood_plank", "wood_plank", ""),
    ("wood_panel", "wood_panel", ""),
    ("wood_solid", "wood_solid", ""),
    ("dirt", "dirt", ""),
    ("grass", "grass", ""),
    ("gravel", "gravel", ""),
    ("mud", "mud", ""),
    ("quicksand", "quicksand", ""),
    ("sand", "sand", ""),
    ("slipperyslime", "slipperyslime", ""),
    ("antlionsand", "antlionsand", ""),
    ("slime", "slime", ""),
    ("water", "water", ""),
    ("wade", "wade", ""),
    ("ice", "ice", ""),
    ("snow", "snow", ""),
    ("alienflesh", "alienflesh", ""),
    ("antlion", "antlion", ""),
    ("armorflesh", "armorflesh", ""),
    ("bloodyflesh", "bloodyflesh", ""),
    ("flesh", "flesh", ""),
    ("foliage", "foliage", ""),
    ("watermelon", "watermelon", ""),
    ("zombieflesh", "zombieflesh", ""),
    ("asphalt", "asphalt", "Don't use this one, wiki says it\'s missing"),
    ("glass", "glass", ""),
    ("glassbottle", "glassbottle", ""),
    ("combine_glass", "combine_glass", ""),
    ("tile", "tile", ""),
    ("paper", "paper", ""),
    ("papercup", "papercup", ""),
    ("cardboard", "cardboard", ""),
    ("plaster", "plaster", ""),
    ("plastic_barrel", "plastic_barrel", ""),
    ("plastic_barrel_buoyant", "plastic_barrel_buoyant", ""),
    ("plastic_box", "plastic_box", ""),
    ("plastic", "plastic", ""),
    ("rubber", "rubber", ""),
    ("rubbertire", "rubbertire", ""),
    ("slidingrubbertire", "slidingrubbertire", ""),
    ("slidingrubbertire_front", "slidingrubbertire_front", ""),
    ("slidingrubbertire_rear", "slidingrubbertire_rear", ""),
    ("jeeptire", "jeeptire", ""),
    ("brackingrubbertire", "brackingrubbertire", ""),
    ("carpet", "carpet", ""),
    ("ceiling_tile", "ceiling_tile", ""),
    ("computer", "computer", ""),
    ("pottery", "pottery", ""),
]
# </variables>