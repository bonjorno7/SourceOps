# <libraries>
import os
import bpy
# </libraries>

#<functions>
def is_mesh(self, obj):
    return obj.type == 'MESH'

def is_curve(self, obj):
    return obj.type == 'CURVE'

def add_prop(self, label, scope, prop):
    r = self.layout.row()
    s = r.split(factor = 0.4)
    c = s.column()
    c.label(text = label)
    s = s.split()
    c = s.column()
    c.prop(scope, prop)

def replace_slashes(path):
    wrong_slash = "\\" if os.sep == "/" else "/"
    new_path = ""
    for c in path:
        if c == wrong_slash: new_path += os.sep
        else: new_path += c
    return new_path
#</functions>

# <variables>
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