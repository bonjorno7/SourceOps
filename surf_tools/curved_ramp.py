import os
import subprocess
import math
import bpy
import bmesh
import mathutils
from .. import common


class SurfRampProps(bpy.types.PropertyGroup):
    """Properties for the Surf Ramp Tool"""
    bl_idname = "SOURCEOPS_PG_SurfRampProps"

    curve: bpy.props.PointerProperty(
        name="Curve",
        description="Select your Ramp Curve object here",
        type=bpy.types.Object,
        poll=common.is_curve,
    )

    segment: bpy.props.PointerProperty(
        name="Segment",
        description="Select your Ramp Reference mesh here",
        type=bpy.types.Object,
        poll=common.is_mesh,
    )

    start_cap: bpy.props.PointerProperty(
        name="Start Cap",
        description="Select your Reference Start Cap here",
        type=bpy.types.Object,
        poll=common.is_mesh,
    )

    end_cap: bpy.props.PointerProperty(
        name="End Cap",
        description="Select your Reference End Cap here",
        type=bpy.types.Object,
        poll=common.is_mesh,
    )


class SurfRampify(bpy.types.Operator):
    """Add the appropriate modifiers to the chosen objects"""
    bl_idname = "sourceops.surf_rampify"
    bl_label = "Add Modifiers"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        g = common.get_globals(context)
        sr = g.surf_ramp
        return sr.curve and sr.segment

    def execute(self, context):
        g = common.get_globals(context)
        sr = g.surf_ramp
        sr.segment.modifiers.clear()

        array = sr.segment.modifiers.new("Array", 'ARRAY')
        array.show_expanded = True
        array.show_in_editmode = False
        array.fit_type = 'FIT_CURVE'
        array.relative_offset_displace = (0, 0, 1)
        array.use_merge_vertices = True
        array.use_merge_vertices_cap = True
        if sr.start_cap:
            array.start_cap = sr.start_cap
        if sr.end_cap:
            array.end_cap = sr.end_cap

        curve = sr.segment.modifiers.new("Curve", 'CURVE')
        curve.show_expanded = True
        curve.show_in_editmode = False
        curve.deform_axis = 'POS_Z'
        array.curve = sr.curve
        curve.object = sr.curve

        return {"FINISHED"}
