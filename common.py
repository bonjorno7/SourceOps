# <libraries>
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
#</functions>

# <variables>
surface_properties = [
    ("00", "default", ""),
    ("01", "default_silent", ""),
    ("02", "floatingstandable", ""),
    ("03", "item", ""),
    ("04", "ladder", ""),
    ("05", "no_decal", ""),
    ("06", "player", ""),
    ("07", "player_control_clip", ""),
    ("08", "baserock", ""),
    ("09", "boulder", ""),
    ("10", "brick", ""),
    ("11", "concrete", ""),
    ("12", "concrete_block", ""),
    ("12", "rock", ""),
    ("13", "canister", ""),
    ("14", "chain", ""),
    ("15", "chainlink", ""),
    ("16", "combine_metal", ""),
    ("17", "crowbar", ""),
    ("18", "floating_metal_barrel", ""),
    ("19", "grenade", ""),
    ("20", "gunship", ""),
    ("21", "metal", ""),
    ("22", "metal_barrel", ""),
    ("23", "metal_bouncy", ""),
    ("24", "metal_box", ""),
    ("25", "metal_seafloorcar", ""),
    ("26", "metalgrate", ""),
    ("27", "metalpanel", ""),
    ("28", "metalvent", ""),
    ("29", "metalvehicle", ""),
    ("30", "paintcan", ""),
    ("31", "popcan", ""),
    ("32", "roller", ""),
    ("33", "slipperymetal", ""),
    ("34", "solidmetal", ""),
    ("35", "strider", ""),
    ("36", "weapon", ""),
    ("37", "wood", ""),
    ("38", "wood_box", ""),
    ("39", "wood_crate", ""),
    ("40", "wood_furniture", ""),
    ("41", "wood_lowdensity", ""),
    ("42", "wood_plank", ""),
    ("43", "wood_panel", ""),
    ("44", "wood_solid", ""),
    ("45", "dirt", ""),
    ("46", "grass", ""),
    ("47", "gravel", ""),
    ("48", "mud", ""),
    ("49", "quicksand", ""),
    ("50", "sand", ""),
    ("51", "slipperyslime", ""),
    ("52", "antlionsand", ""),
    ("53", "slime", ""),
    ("54", "water", ""),
    ("55", "wade", ""),
    ("56", "ice", ""),
    ("57", "snow", ""),
    ("58", "alienflesh", ""),
    ("59", "antlion", ""),
    ("60", "armorflesh", ""),
    ("61", "bloodyflesh", ""),
    ("62", "flesh", ""),
    ("63", "foliage", ""),
    ("64", "watermelon", ""),
    ("65", "zombieflesh", ""),
    ("66", "asphalt", ""),
    ("67", "glass", ""),
    ("68", "glassbottle", ""),
    ("69", "combine_glass", ""),
    ("70", "tile", ""),
    ("71", "paper", ""),
    ("72", "papercup", ""),
    ("73", "cardboard", ""),
    ("74", "plaster", ""),
    ("75", "plastic_barrel", ""),
    ("76", "plastic_barrel_buoyant", ""),
    ("77", "plastic_box", ""),
    ("78", "plastic", ""),
    ("79", "rubber", ""),
    ("80", "rubbertire", ""),
    ("81", "slidingrubbertire", ""),
    ("82", "slidingrubbertire_front", ""),
    ("83", "slidingrubbertire_rear", ""),
    ("84", "jeeptire", ""),
    ("85", "brackingrubbertire", ""),
    ("86", "carpet", ""),
    ("87", "ceiling_tile", ""),
    ("88", "computer", ""),
    ("89", "pottery", ""),
]
# </variables>