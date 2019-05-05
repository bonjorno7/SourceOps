import os
import subprocess
import math
import bpy
import bmesh
import mathutils
from .. import common


class SurfToolsPanel(bpy.types.Panel):
    bl_idname = "BASE_PT_SurfToolsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Surf Tools"

    def draw_header(self, context):
        self.layout.label(icon='MARKER')

    def draw(self, context):
        pass


class CollisionPanel(bpy.types.Panel):
    bl_idname = "BASE_PT_CollisionPanel"
    bl_parent_id = "BASE_PT_SurfToolsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Collision Generator"

    def draw_header(self, context):
        self.layout.label(icon='MESH_ICOSPHERE')

    def draw(self, context):
        collision = context.scene.BASE.collision
        common.add_enum(self.layout, "Target", collision, "target")
        common.add_enum(self.layout, "Modifiers", collision, "modifiers")
        common.add_prop(self.layout, "Thickness", collision, "thickness")
        self.layout.operator("base.surf_collision")


class CurvedRampPanel(bpy.types.Panel):
    bl_idname = "BASE_PT_CurvedRampPanel"
    bl_parent_id = "BASE_PT_SurfToolsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "BASE"
    bl_label = "Curved Ramp Tool"

    def draw_header(self, context):
        self.layout.label(icon='CURVE_DATA')

    def draw(self, context):
        surf_ramp = context.scene.BASE.surf_ramp
        common.add_prop(self.layout, "Curve", surf_ramp, "curve")
        common.add_prop(self.layout, "Segment", surf_ramp, "segment")
        if surf_ramp.segment:
            common.add_prop(self.layout, "Start Cap", surf_ramp, "start_cap")
            common.add_prop(self.layout, "End Cap", surf_ramp, "end_cap")
        self.layout.operator("base.surf_rampify")
