from vpk_search import vpk
from vtf_wrapper import VTFLib, VTFLibEnums
from vtf_wrapper.VTFLibEnums import ImageFlag

vtf_lib = VTFLib.VTFLib()

def find_file_in_vpks(vpk_lst, filepath):
    for i in vpk_lst:
        pak = vpk.open(i)
        try:
            k = filepath.rfind("/")
            pakfile = pak.get_file(filepath[:k] + "\\" + filepath[k+1:])
            if pakfile is not None:
                return pakfile
        except KeyError:
            continue
        
        

#pak1 = vpk.open("E:/Steam/steamapps/common/Counter-Strike Source/cstrike/cstrike_pak_dir.vpk")
#pakfile = pak1["materials/tools/toolsskybox.vmt"]
#print(pakfile.read().decode('utf-16le'))



file = find_file_in_vpks(["E:/Steam/steamapps/common/Counter-Strike Source/cstrike/cstrike_pak_dir.vpk",
                          "E:/Steam/steamapps/common/Counter-Strike Source/hl2/hl2_textures_dir.vpk",
                          "E:/Steam/steamapps/common/Counter-Strike Source/hl2/hl2_sound_vo_english_dir.vpk",
                          "E:/Steam/steamapps/common/Counter-Strike Source/hl2/hl2_sound_misc_dir.vpk",
                          "E:/Steam/steamapps/common/Counter-Strike Source/hl2/hl2_misc_dir.vpk",
                          "E:/Steam/steamapps/common/Counter-Strike Source/platform/platform_misc_dir.vpk"],
                         "materials/tools/toolsnodraw.vmt")
if file is not None:
    for i in file.read().decode('unicode_escape').splitlines():
        if i.split()[0].lower() == "\"$basetexture\"":
            print("materials/"+i.split()[1].lower()[1:-1] + ".vtf")
            vtf_file = find_file_in_vpks(["E:/Steam/steamapps/common/Counter-Strike Source/cstrike/cstrike_pak_dir.vpk",
                          "E:/Steam/steamapps/common/Counter-Strike Source/hl2/hl2_textures_dir.vpk",
                          "E:/Steam/steamapps/common/Counter-Strike Source/hl2/hl2_sound_vo_english_dir.vpk",
                          "E:/Steam/steamapps/common/Counter-Strike Source/hl2/hl2_sound_misc_dir.vpk",
                          "E:/Steam/steamapps/common/Counter-Strike Source/hl2/hl2_misc_dir.vpk",
                          "E:/Steam/steamapps/common/Counter-Strike Source/platform/platform_misc_dir.vpk"],
                                          "materials/"+i.split()[1].lower()[1:-1] + ".vtf")
            
            if vtf_file is not None:
                print(vtf_lib.image_load_from_mem(vtf_file))

                vtf_lib.image_save("E:/GitHub/SourceOps/utils/test.vtf")
