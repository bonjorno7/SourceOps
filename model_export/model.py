# <import>
import os, subprocess, math
import bpy, bmesh, mathutils
from .. import common

from . mesh import BASE_PG_MeshProps
from . surface_props import surface_props
# </import>

# <functions>
def update_model_name(self, context):
    name = bpy.path.native_pathsep(self["name"])
    if name.lower().endswith(".mdl"):
        name = name[:-4]
    self["name"] = name
# </functions>

# <props>
class BASE_PG_ModelProps(bpy.types.PropertyGroup):
    """Properties for a model"""
    meshes: bpy.props.CollectionProperty(type = BASE_PG_MeshProps)
    mesh_index: bpy.props.IntProperty(default = 0)

    name: bpy.props.StringProperty(
        name = "Model Name",
        description = "Your model's path, eg example\\model (don't add the file extension)",
        default = "example\\model",
        update = update_model_name,
    )

    surface_prop: bpy.props.EnumProperty(
        name = "Surface Property",
        description = "Choose the surface property of your model, this affects decals and how it sounds in game",
        items = surface_props,
    )

    autocenter: bpy.props.BoolProperty(
        name = "Auto Center",
        description = "$autocenter, aligns the model's $origin to the center of its bounding box and creates an attachment point called \"placementOrigin\" where its origin used to be",
        default = False,
    )

    mostly_opaque: bpy.props.BoolProperty(
        name = "Has Glass",
        description = "$mostlyopaque, use this if your model has something transparent like glass",
        default = False,
    )
# </props>

# <list>
class BASE_UL_ModelList(bpy.types.UIList):
    """List of models"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text = "", emboss = False, translate = False)

class BASE_OT_AddModel(bpy.types.Operator):
    """Create a model"""
    bl_idname = "base.add_model"
    bl_label = "Add Model"

    def execute(self, context):
        base = context.scene.BASE
        base.models.add()
        base.model_index = len(base.models) - 1
        return {'FINISHED'}

class BASE_OT_RemoveModel(bpy.types.Operator):
    """Remove the selected model"""
    bl_idname = "base.remove_model"
    bl_label = "Remove Model"

    @classmethod
    def poll(cls, context):
        base = context.scene.BASE
        return len(base.models) > 0

    def execute(self, context):
        base = context.scene.BASE
        base.models.remove(base.model_index)
        base.model_index = min(
            max(0, base.model_index - 1),
            len(base.models) - 1
        )
        return {'FINISHED'}

class BASE_OT_MoveModel(bpy.types.Operator):
    """Move the selected model up or down in the list"""
    bl_idname = "base.move_model"
    bl_label = "Move Model"

    direction: bpy.props.EnumProperty(items = (
        ('UP', "Up", "Move the item up"),
        ('DOWN', "Down", "Move the item down"),
    ))

    @classmethod
    def poll(cls, context):
        base = context.scene.BASE
        return len(base.models) > 1

    def execute(self, context):
        base = context.scene.BASE
        neighbor = base.model_index + (-1 if self.direction == 'UP' else 1)
        base.models.move(neighbor, base.model_index)
        list_length = len(base.models) - 1
        base.model_index = max(0, min(neighbor, list_length))
        return {'FINISHED'}
# </list>