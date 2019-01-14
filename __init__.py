# <definition>
bl_info = {
    "blender" : (2, 80, 0),
    "name" : "Blender Source Extras",
    "description" : "Simple add-on to augment Blender Source Tools",
    "author" : "bonjorno7",
    "version" : (0, 7),
    "location" : "3D View > Sidebar",
    "category" : "Extra",
    "warning" : "",
}
# </definition>

# <libraries>
from . import options
from . import qc_generator
from . import ramp_tool
# </libraries>

# <registering>
def register():
    options.register()
    qc_generator.register()
    ramp_tool.register()
# </registering>

# <unregistering>
def unregister():
    options.unregister()
    qc_generator.unregister()
    ramp_tool.unregister()
# </unregistering>

# <main>
if __name__ == "__main__":
    register()
# </main>