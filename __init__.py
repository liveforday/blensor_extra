bl_info = {
    "name": "My Addon",
    "description": "Description of my addon",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Tools > My Addon",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "category": "Object"
}

import os
import bpy
from .scan_animation import ScanAnimation
from .scan_animation_group import ScanAnimationGroup, FollowConstraint, load_object_from,delete_hierarchy,set_animation,LabelList, StringList
from .join_part import obj2blend
from pathlib import Path

class ScanAnimationPanel(bpy.types.Panel):
    bl_label = "Scan Animation"
    bl_idname = "OBJECT_PT_Scan_animation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Blensor"


    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("extrablensor.scan_animation", text="scan animation")

        layout.prop(context.scene, "tobin", text="tobin")

        row = layout.row()
        row.prop(context.scene, "extrablensor_folder_path")

class ScanAnimationOperator(bpy.types.Operator):
    bl_idname = "extrablensor.scan_animation"
    bl_label = "Scan Animation"

    def execute(self, context):
        # This is where the code for your operator goes
        save_path = context.scene.extrablensor_folder_path
        tobin = context.scene.tobin
        cloud_generator = ScanAnimation(save_path)
        cloud_generator.start(tobin)
        print("scaning")
        return {'FINISHED'}

class ScanAnimationGroupPanel(bpy.types.Panel):
    bl_label = "Scan Animation Group"
    bl_idname = "OBJECT_PT_Scan_animation_group"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Blensor"


    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("extrablensor.scan_animation_group", text="scan animation group")

        layout.prop(context.scene, "tobin_group", text="tobin")

        row = layout.row()
        row.prop(context.scene.extrablensor_follow_param, "name")
        row.operator("extrablensor.record_follow_param", text="Apply")

        row = layout.row()
        row.prop(context.scene.extrablensor_follow_param, "use_curve_follow")
        row.prop(context.scene.extrablensor_follow_param, "forward_axis")
        row.prop(context.scene.extrablensor_follow_param, "up_axis")
        # row.prop(context.scene.extrablensor_follow_param, "offset")
        row.enabled = False

        row = layout.row()
        row.prop(context.scene.extrablensor_follow_param, "start_frame")
        row.prop(context.scene.extrablensor_follow_param, "end_frame")
        row.enabled = False

        row = layout.row()
        row.prop(context.scene, "random_path", text="path random")
        row.prop(context.scene, "cam_pos", text="random camera")

        row = layout.row()
        row.prop(context.scene, "low_limit", text="Low limit")
        row.prop(context.scene, "top_limit", text="Top limit")
        
        row.operator("extrablensor.record_parts", text="Apply")

       
        for item in context.scene.extrablensor_obj_parts:
            row = layout.row()
            row.label(text=item.name)
            row.prop(item, "value")
        
        row = layout.row()
        row.prop(context.scene, "extrablensor_group_folder_path")

        row = layout.row()
        row.prop(context.scene, "extrablensor_numofset")

        row = layout.row()
        row.label(text="Select files:")
        row.operator("extrablensor.addfiles", text="", icon="PLUS")
        for item in context.scene.extrablensor_selected_files:
            row = layout.row()
            row.label(text=item.name)
        # row = layout.row()
        # row.operator("extrablensor.addfiles", text="")


    
class ScanAnimationGroupOperator(bpy.types.Operator):
    bl_idname = "extrablensor.scan_animation_group"
    bl_label = "Scan Animation Group"

    def execute(self, context):
        save_path = context.scene.extrablensor_group_folder_path
        num_of_set = context.scene.extrablensor_numofset

        tobin = context.scene.tobin_group
        random_path = context.scene.random_path
        cam_pos = context.scene.cam_pos
        range = [context.scene.low_limit, context.scene.top_limit]
        labels = []
        for item in context.scene.extrablensor_obj_parts:
            label = [item.name, item.value] 
            labels.append(label)
        # first = context.scene.extrablensor_selected_files[0]
        # first_path = Path(first.name)
        obj = bpy.data.objects[context.scene.extrablensor_follow_param.obj]
        delete_hierarchy(obj)

        for blend_file in context.scene.extrablensor_selected_files:
            blend_path = Path(blend_file.name)
            load_object_from(blend_path)
            follow_param = context.scene.extrablensor_follow_param

            if follow_param.path == follow_param.obj:
                obj_new = bpy.data.objects[blend_path.stem]
                set_animation(context.scene.extrablensor_follow_param, obj_new )
                
                
            print("generator")

            cloud_generator = ScanAnimationGroup()
            cloud_generator.set_tobin(tobin)
            cloud_generator.set_random_path(random_path)
            cloud_generator.set_random_cam_pos(cam_pos, range)
            cloud_generator.number_of_sets(num_of_set)
            cloud_generator.set_save_path(save_path, blend_path.stem,'L')
            cloud_generator.set_label(labels)
            cloud_generator.set_path_name('aircraft_path')
            cloud_generator.generate()


            delete_hierarchy(bpy.data.objects[blend_path.stem])

        load_object_from(context.scene.extrablensor_follow_param.obj)
        # if not obj:
        #     obj_new = bpy.data.objects[context.scene.extrablensor_follow_param.obj]
        #     set_animation(context.scene.extrablensor_follow_param, obj_new)
        
        return {'FINISHED'}

class RecordFollowParamOperator(bpy.types.Operator):
    bl_idname = "extrablensor.record_follow_param"
    bl_label = "Record Follow Path Param"

    def execute(self, context):
        # context.scene.extrablensor_follow_param.clear()
        obj = bpy.context.object
        follow_path_constraint = obj.constraints.get(context.scene.extrablensor_follow_param.name)

        if follow_path_constraint is not None:
            context.scene.extrablensor_follow_param.path = obj.name
            context.scene.extrablensor_follow_param.offset = follow_path_constraint.offset_factor
            context.scene.extrablensor_follow_param.forward_axis = follow_path_constraint.forward_axis
            context.scene.extrablensor_follow_param.up_axis = follow_path_constraint.up_axis
            context.scene.extrablensor_follow_param.use_curve_follow = follow_path_constraint.use_curve_follow
            context.scene.extrablensor_follow_param.target = follow_path_constraint.target
            context.scene.extrablensor_follow_param.start_frame = context.scene.frame_start
            context.scene.extrablensor_follow_param.end_frame = context.scene.frame_end
        else:
            print("target has no follow path constraint")

        return {'FINISHED'}

class RecordParts(bpy.types.Operator):
    bl_idname = "extrablensor.record_parts"
    bl_label = "Record Parts"

    def execute(self, context):
        obj = bpy.context.object
        context.scene.extrablensor_follow_param.obj = obj.name

        context.scene.extrablensor_obj_parts.clear()
        i = 0
        for child  in bpy.context.selected_objects[0].children:
            item = context.scene.extrablensor_obj_parts.add()
            item.name = child.name
            item.value = i
            i += 1
            pass
        print("record parts")
        return {'FINISHED'}

    
class AddFiles(bpy.types.Operator):
    bl_idname = "extrablensor.addfiles"
    bl_label = "Add Files"

    # files = bpy.props.CollectionProperty(
    #     type=bpy.types.OperatorFileListElement,
    #     options={'REGISTER','INTERNAL'}
    # )

    files= bpy.props.CollectionProperty(
        type=bpy.types.OperatorFileListElement
    )
    
    directory = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        # Use Blender's file browser to select multiple files
        context.scene.extrablensor_selected_files.clear()
        for file in self.files:
            filepath = self.directory + file.name
            item = context.scene.extrablensor_selected_files.add()
            item.name = filepath
            pass

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class JoinPartsPanel(bpy.types.Panel):
    bl_label = "Join Parts"
    bl_idname = "OBJECT_PT_Join_parts"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Blensor"


    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("extrablensor.join_parts", text="Join Parts")

        row = layout.row()
        row.prop(context.scene, "extrablensor_join_part_path")

        row = layout.row()
        row.operator("extrablensor.add_part", text="add_part")


        for i, input_data in enumerate(context.scene.extrablensor_parts):
            box = layout.box()
            row = box.row()
            row.prop(input_data, "name", text="Input #" + str(i+1))

            delete_op = row.operator("extrablensor.remove_part", text="", icon="X")
            delete_op.index = i

        row = layout.row()
        row.label(text="Select obj files:")
        row.operator("extrablensor.select_obj", text="", icon="PLUS")
        for item in context.scene.extrablensor_selected_objs:
            row = layout.row()
            row.label(text=item.name)

class JoinPartsOperator(bpy.types.Operator):
    bl_label = "Join Parts"
    bl_idname = "extrablensor.join_parts"

    def execute(self, context):
        parts_name=[]
        for item in context.scene.extrablensor_parts:
            parts_name.append(item.name)

        save_path = context.scene.extrablensor_join_part_path

        for item in context.scene.extrablensor_selected_objs:
            obj_path = Path(item.name)
            obj2blend(parts_name, obj_path, save_path)
        return {'FINISHED'}
        
    
class AddPart(bpy.types.Operator):
    bl_idname = "extrablensor.add_part"
    bl_label = "Add Parts"

    def execute(self, context):
        input_parts = context.scene.extrablensor_parts
        input_data = input_parts.add()
        input_data.name = "Input #" + str(len(input_parts))
        return {'FINISHED'}
 
class RemovePart(bpy.types.Operator):
    bl_idname = "extrablensor.remove_part"
    bl_label = "remove Part"

    index = bpy.props.IntProperty()

    def execute(self, context):
        input_parts = context.scene.extrablensor_parts
        input_parts.remove(self.index)
        return {'FINISHED'}
    

class SelectObj(bpy.types.Operator):
    bl_idname = "extrablensor.select_obj"
    bl_label = "Select obj file"

    files= bpy.props.CollectionProperty(
        type=bpy.types.OperatorFileListElement
    )
    
    directory = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        # Use Blender's file browser to select multiple files
        context.scene.extrablensor_selected_objs.clear()
        for file in self.files:
            filepath = self.directory + file.name
            item = context.scene.extrablensor_selected_objs.add()
            item.name = filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



def register():
    bpy.utils.register_class(ScanAnimationPanel)
    bpy.utils.register_class(ScanAnimationGroupPanel) 
    bpy.utils.register_class(ScanAnimationOperator)
    bpy.utils.register_class(ScanAnimationGroupOperator)
    bpy.utils.register_class(AddFiles)
    bpy.utils.register_class(StringList)
    bpy.utils.register_class(LabelList)
    bpy.utils.register_class(RecordFollowParamOperator)
    bpy.utils.register_class(FollowConstraint)
    bpy.utils.register_class(RecordParts)


    bpy.types.Scene.tobin = bpy.props.BoolProperty(
        name="tobin",
        description = "if convert pcd to bin",
        default = True
    )
    bpy.types.Scene.extrablensor_folder_path = bpy.props.StringProperty(
        name="Folder Path",
        description = "Folder path to use",
        default = "D:/data/",
        subtype='DIR_PATH'
    )
    bpy.types.Scene.tobin_group = bpy.props.BoolProperty(
        name="tobin_group",
        description = "if convert pcd to bin",
        default = True
    )
    bpy.types.Scene.random_path = bpy.props.BoolProperty(
        name="random_path",
        description = "if random path",
        default = True
    )
    bpy.types.Scene.cam_pos = bpy.props.BoolProperty(
        name="cam_pos",
        description = "if random camera height",
        default = True
    )

    bpy.types.Scene.top_limit = bpy.props.IntProperty(
        name="top_limit",
        description = "camera position top limit",
        default = 8,
        subtype='UNSIGNED'
        )

    bpy.types.Scene.low_limit = bpy.props.IntProperty(
        name="low_limit",
        description = "camera position low limit",
        default = 5,
        subtype='UNSIGNED'
        )

    bpy.types.Scene.extrablensor_group_folder_path = bpy.props.StringProperty(
        name="Folder Path",
        description = "Folder path to use",
        default = "D:/data/",
        subtype='DIR_PATH'
    )
    bpy.types.Scene.extrablensor_select_folder_path = bpy.props.StringProperty(
        name="Folder Path",
        description = "Folder path to use",
        default = "D:/data/",
        subtype='DIR_PATH'
    )
    bpy.types.Scene.extrablensor_numofset = bpy.props.IntProperty(
        name="num of set",
        description = "num of set",
        default = 1,
        subtype='UNSIGNED'
        )

    bpy.types.Scene.extrablensor_selected_files = bpy.props.CollectionProperty(type=StringList)
    bpy.types.Scene.extrablensor_obj_parts = bpy.props.CollectionProperty(type=LabelList)
    bpy.types.Scene.extrablensor_follow_param = bpy.props.PointerProperty(type=FollowConstraint)

    bpy.utils.register_class(JoinPartsPanel)
    bpy.utils.register_class(AddPart)
    bpy.utils.register_class(RemovePart)
    bpy.utils.register_class(SelectObj)
    bpy.utils.register_class(JoinPartsOperator)
    bpy.types.Scene.extrablensor_parts = bpy.props.CollectionProperty(type=StringList)
    bpy.types.Scene.extrablensor_selected_objs = bpy.props.CollectionProperty(type=StringList)
    bpy.types.Scene.extrablensor_join_part_path = bpy.props.StringProperty(
        name="Folder Path",
        description = "Folder path to use",
        default = "D:/data/",
        subtype='DIR_PATH'
    )


def unregister():
    bpy.utils.unregister_class(ScanAnimationPanel)
    bpy.utils.unregister_class(ScanAnimationGroupPanel) 
    bpy.utils.unregister_class(ScanAnimationOperator)
    bpy.utils.unregister_class(ScanAnimationGroupOperator)
    bpy.utils.unregister_class(AddFiles)
    bpy.utils.unregister_class(RecordFollowParamOperator)
    

    bpy.utils.unregister_class(JoinPartsPanel)
    bpy.utils.unregister_class(AddPart)
    bpy.utils.unregister_class(RemovePart)
if __name__ == "__main__":
    register()
