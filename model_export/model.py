import bpy
import os
from . surface_props import surface_props


class ModelProps(bpy.types.PropertyGroup):
    """Properties for a model"""
    bl_idname = "BASE_PG_ModelProps"
    collection: bpy.props.PointerProperty(type=bpy.types.Collection)

    def update_model_name(self, context):
        name = bpy.path.native_pathsep(self["name"])
        if name.lower().endswith(".mdl"):
            name = name[:-4]
        self["name"] = name

    name: bpy.props.StringProperty(
        name="Model Name",
        description="Your model's path, eg example" +
        os.sep + "model (don't add the file extension)",
        default="example" + os.sep + "model",
        update=update_model_name,
    )

    surface_prop: bpy.props.EnumProperty(
        name="Surface Property",
        description="Choose the surface property of your model, this affects decals and how it sounds in game",
        items=surface_props,
    )

    autocenter: bpy.props.BoolProperty(
        name="Auto Center",
        description="$autocenter, aligns the model's $origin to the center of its bounding box",
        default=False,
    )

    mostly_opaque: bpy.props.BoolProperty(
        name="Has Glass",
        description="$mostlyopaque, use this if your model has something transparent like glass",
        default=False,
    )


class ModelList(bpy.types.UIList):
    """List of models"""
    bl_idname = "BASE_UL_ModelList"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, translate=False)


class AddModel(bpy.types.Operator):
    """Create a model"""
    bl_idname = "base.add_model"
    bl_label = "Add Model"

    def execute(self, context):
        base = context.scene.BASE
        base.models.add()
        base.model_index = len(base.models) - 1
        return {'FINISHED'}


class RemoveModel(bpy.types.Operator):
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


class MoveModel(bpy.types.Operator):
    """Move the selected model up or down in the list"""
    bl_idname = "base.move_model"
    bl_label = "Move Model"

    direction: bpy.props.EnumProperty(items=(
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
