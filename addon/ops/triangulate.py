import bpy


class SOURCEOPS_OT_triangulate(bpy.types.Operator):
    bl_idname = 'sourceops.triangulate'
    bl_label = 'Add Triangulate Modifier'
    bl_description = 'Add a triangulate modifier to the selected objects and remove existing triangulate modifiers'
    bl_options = {'REGISTER', 'UNDO'}

    quad_method: bpy.props.EnumProperty(
        name='Quad Method',
        description='Method for splitting the quads into triangles',
        items=[
            ('BEAUTY', 'Beauty', 'Split the quads in nice triangles, slower method'),
            ('FIXED', 'Fixed', 'Split the quads on the first and third vertices'),
            ('FIXED_ALTERNATE', 'Fixed Alternate', 'Split the quads on the 2nd and 4th vertice'),
            ('SHORTEST_DIAGONAL', 'Shortest Diagonal', 'Split the quads based on the distance between the vertices'),
        ],
        default='BEAUTY',
    )

    ngon_method: bpy.props.EnumProperty(
        name='N-gon Method',
        description='Method for splitting the n-gons into triangles',
        items=[
            ('BEAUTY', 'Beauty', 'Arrange the triangles evenly (slow)'),
            ('CLIP', 'Clip', 'Split the polygons with an ear clipping algorithm'),
        ],
        default='BEAUTY',
    )

    min_vertices: bpy.props.IntProperty(
        name='Minimum Vertices',
        description='Triangulate only polygons with vertex count greater than or equal to this number',
        min=4,
        default=4,
    )

    keep_custom_normals: bpy.props.BoolProperty(
        name='Keep Normals',
        description='Try to preserve custom normals.\nWarning: Depending on chosen triangulation method, shading may not be fully preserved, "Fixed" method usually gives the best result here.\nDoes nothing in Blender 4.2 or newer',
        default=True,
    )

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type in {'MESH', 'CURVE', 'SURFACE', 'FONT'}:
                for mod in obj.modifiers[:]:
                    if mod.type == 'TRIANGULATE':
                        obj.modifiers.remove(mod)

                mod = obj.modifiers.new('Triangulate', 'TRIANGULATE')
                mod.quad_method = self.quad_method
                mod.ngon_method = self.ngon_method
                mod.min_vertices = self.min_vertices
                if hasattr(mod, 'keep_custom_normals'):
                    mod.keep_custom_normals = self.keep_custom_normals

        return {'FINISHED'}
