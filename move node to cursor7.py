bl_info = {
    "name": "Move Nodes and Frames to Cursor",
    "author": "ChatGPT, deepseek and duhazzz",
    "version": (1, 8),
    "blender": (3, 6, 0),
    "location": "Node Editor > Node Menu, Right-Click, Search",
    "description": "Moves selected nodes and frames to cursor, preserving group offset",
    "category": "Node",
}

import bpy


class NODE_OT_MoveNodeToCursor(bpy.types.Operator):
    bl_idname = "node.move_to_cursor_nested"
    bl_label = "Move Selected Nodes/Frames to Cursor"
    bl_options = {'REGISTER', 'UNDO'}

    def get_absolute_node_position(self, node):
        x, y = node.location.x, node.location.y
        parent = node.parent
        while parent and parent.type == 'FRAME':
            x += parent.location.x
            y += parent.location.y
            parent = parent.parent
        return x, y

    def execute(self, context):
        selected_nodes = context.selected_nodes
        if not selected_nodes:
            self.report({'ERROR'}, "No nodes or frames selected!")
            return {'CANCELLED'}

        cursor = context.space_data.cursor_location

        abs_positions = []
        for node in selected_nodes:
            abs_x, abs_y = self.get_absolute_node_position(node)
            if node.type == 'FRAME':
                center_x = abs_x + node.width / 2
                center_y = abs_y - node.height / 2
                abs_positions.append((center_x, center_y))
            else:
                abs_positions.append((abs_x, abs_y))

        min_x = min(pos[0] for pos in abs_positions)
        max_x = max(pos[0] for pos in abs_positions)
        min_y = min(pos[1] for pos in abs_positions)
        max_y = max(pos[1] for pos in abs_positions)

        group_center_x = (min_x + max_x) / 2
        group_center_y = (min_y + max_y) / 2

        offset_x = cursor.x - group_center_x
        offset_y = cursor.y - group_center_y

        for node in selected_nodes:
            abs_x, abs_y = self.get_absolute_node_position(node)

            if node.type == 'FRAME':
                new_center_x = abs_x + node.width / 2 + offset_x
                new_center_y = abs_y - node.height / 2 + offset_y
                new_abs_x = new_center_x - node.width / 2
                new_abs_y = new_center_y + node.height / 2
            else:
                new_abs_x = abs_x + offset_x
                new_abs_y = abs_y + offset_y

            parent = node.parent
            new_local_x = new_abs_x
            new_local_y = new_abs_y
            while parent and parent.type == 'FRAME':
                new_local_x -= parent.location.x
                new_local_y -= parent.location.y
                parent = parent.parent

            node.location.x = new_local_x
            node.location.y = new_local_y

        return {'FINISHED'}


def draw_move_to_cursor_context(self, context):
    self.layout.separator()
    self.layout.operator("node.move_to_cursor_nested", icon='CURSOR')


def draw_node_menu(self, context):
    self.layout.separator()
    self.layout.operator("node.move_to_cursor_nested", icon='CURSOR')


def register():
    bpy.utils.register_class(NODE_OT_MoveNodeToCursor)
    bpy.types.NODE_MT_context_menu.append(draw_move_to_cursor_context)
    bpy.types.NODE_MT_node.append(draw_node_menu)


def unregister():
    bpy.utils.unregister_class(NODE_OT_MoveNodeToCursor)
    bpy.types.NODE_MT_context_menu.remove(draw_move_to_cursor_context)
    bpy.types.NODE_MT_node.remove(draw_node_menu)


if __name__ == "__main__":
    register()
