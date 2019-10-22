from parser_p import *
from lexer import *
from utils import *

from datatypes import *
from vmf_classes import *

def round_to_nearest(val, base):
    return base * round(val/base)

def generate_meshes(filepath):
    lex = lexFile(filepath)
    lex.cleanup()

    parse = parseFile(lex.tokens)

    world = search_all_first_class(parse.classes, "world")

    solids = search_single_class(world, "solid")

    meshes = []
    for solid in solids:
        sides = search_single_class(solid, "side")
        polys = [[] for i in range(0, len(sides))]
        for i in range(0,len(sides)-2):
            for j in range(i,len(sides)-1):
                for k in range(j, len(sides)):
                    if i != j and i != k and j != k:
                        
                        p_i = sides[i].keyvals["plane"]
                        p_j = sides[j].keyvals["plane"]
                        p_k = sides[k].keyvals["plane"]

                        legal = True
                        newVertex = brush_utils.get_intersection(p_i, p_j, p_k)
                        if newVertex is None:
                            continue

                        for m in sides:
                            
                            if(vec3.dot(m.keyvals["plane"].normal, newVertex) + m.keyvals["plane"].d)>10**-5:
                               legal = False


                        newVertex.x = round_to_nearest(newVertex.x, 0.01)
                        newVertex.y = round_to_nearest(newVertex.y, 0.01)
                        newVertex.z = round_to_nearest(newVertex.z, 0.01)

                        if legal is True:
                               polys[i].append(newVertex)
                               polys[j].append(newVertex)
                               polys[k].append(newVertex)
        meshes.append(polys)
    return meshes

if __name__ == "__main__":

    print(brush_utils.get_intersection(
        vec3x3("(-192 320 64) (-448 320 64) (-448 320 256)"),
        vec3x3("(-448 320 64) (-192 320 64) (-192 384 64)"),
        vec3x3("(-192 384 64) (-192 320 64) (-192 320 256)")).string())
    
    """meshes = generate_meshes("data.txt")

    for i in meshes:
        for o in i:
            [print(p.string()) for p in o]
            print()
        print()"""
                            
