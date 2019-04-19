# <pep8 compliant>


# <import>
import os, subprocess, math
import bpy, bmesh, mathutils
from .. import common
# </import>

# <props>
class BASE_PG_MeshProps(bpy.types.PropertyGroup):
    """Properties for a mesh"""
    obj: bpy.props.PointerProperty(
        name = "Mesh Object",
        description = "Object that holds the data for this mesh",
        type = bpy.types.Object,
        poll = common.is_mesh,
    )

    kind: bpy.props.EnumProperty(
        name = "Mesh Type",
        description = "Whether this mesh should be Reference (visible) or Collision (tangible)",
        items = (
            ('REFERENCE', "REF", "Reference"),
            ('COLLISION', "COL", "Collision"),
        ),
    )
# </props>

# <list>
class BASE_UL_MeshList(bpy.types.UIList):
    """List of meshes for this model"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row().split(factor = 0.6)
        row.label(text = item.obj.name)
        row.split().row().prop(item, "kind", expand = True)

class BASE_OT_AddMesh(bpy.types.Operator):
    """Add selected objects as meshes to this model"""
    bl_idname = "base.add_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        base = context.scene.BASE
        model = base.models[base.model_index]

        for o in context.selected_objects:
            if o.type == 'MESH':
                duplicate = False

                for m in model.meshes:
                    if m.obj == o:
                        duplicate = True

                if not duplicate:
                    model.meshes.add()
                    mesh = model.meshes[-1]
                    mesh.obj = o

                    if mesh.obj.name.find(".col") != -1:
                        mesh.kind = 'COLLISION'

        model.mesh_index = len(model.meshes) - 1
        return {'FINISHED'}

class BASE_OT_RemoveMesh(bpy.types.Operator):
    """Remove selected mesh from the list"""
    bl_idname = "base.remove_mesh"
    bl_label = "Remove Mesh"

    @classmethod
    def poll(cls, context):
        base = context.scene.BASE
        if len(base.models) > 0:
            model = base.models[base.model_index]
            return len(model.meshes) > 0
        return False

    def execute(self, context):
        base = context.scene.BASE
        model = base.models[base.model_index]
        model.meshes.remove(model.mesh_index)
        model.mesh_index = min(max(0, model.mesh_index - 1), len(model.meshes) - 1)
        return {'FINISHED'}

class BASE_OT_MoveMesh(bpy.types.Operator):
    """Move the selected mesh up or down in the list"""
    bl_idname = "base.move_mesh"
    bl_label = "Move Mesh"

    direction: bpy.props.EnumProperty(items = (
        ('UP', "Up", "Move the item up"),
        ('DOWN', "Down", "Move the item down"),
    ))

    @classmethod
    def poll(cls, context):
        base = context.scene.BASE
        model = base.models[base.model_index]
        return len(model.meshes) > 1

    def execute(self, context):
        base = context.scene.BASE
        model = base.models[base.model_index]
        neighbor = model.mesh_index + (-1 if self.direction == 'UP' else 1)
        model.meshes.move(neighbor, model.mesh_index)
        list_length = len(model.meshes) - 1
        model.mesh_index = max(0, min(neighbor, list_length))
        return {'FINISHED'}
# </list>