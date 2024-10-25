# import buildin package
import os
import random
from pathlib import Path
import shutil

import bpy
import blensor
from blensor import evd
from mathutils import Vector, Euler, Matrix

# import custom package
from .conver_format import convert_format
from .scan import scan_start,scan_range1
from .util import *

class CloudGenerator():
    def __init__(self) -> None:
        self.filepaths = []
        self.num_of_sets = 0
        self.num_of_frame = 0
        self.tobin = False
        self.random_flag = True
        self.labels = None
        self.cam_pos = True
        self.range = [5,8]
        bpy.context.scene.camera = bpy.data.objects['Camera']

    
    def set_save_path(self, root_path, blendfile,suffix=''):
        root_path = Path(root_path)
        for i in range(self.num_of_sets): 
            filepath = root_path/f'pcd/{blendfile}_{i:03d}{suffix}'
            bin_filepath = root_path/f'bin/{blendfile}_{i:03d}{suffix}'
            self.filepaths.append(filepath)
            if os.path.exists(filepath):
                shutil.rmtree(filepath)
            os.makedirs(filepath)
            if os.path.exists(bin_filepath):
                shutil.rmtree(bin_filepath)
            os.makedirs(bin_filepath)

    def number_of_sets(self, set_num):
        self.num_of_sets = set_num
        self.num_of_frame = bpy.context.scene.frame_end

    def set_pcd2bin(self, flag):
        self.bin = flag
    
    def set_coord2laser(self):
        pass

    def set_path_name(self, path_name):
        self.path_name = path_name
        pass

    def random_path(self):
        obj = bpy.data.objects[self.path_name]
        path_curves  = obj.data.splines[0]
        key_points = path_curves.points
        # change path direct
        key_points[0].co.x = -key_points[0].co.x
        key_points[1].co.x = -key_points[1].co.x

        # change path pos
        key_points = key_points[-5:-2]
        for point in key_points:
            mat_world = obj.matrix_world
            pos_world = mat_world * point.co
            pos_world.x = random.uniform(-2,2)
            point.co = mat_world.inverted()* pos_world 
    
    def random_camera_pos(self, range):
        obj = bpy.data.objects['Camera']
        obj.location.z = random.uniform(range[0], range[1])
        pass
    
    def remove_binfile(self, path):
        if os.path.exists(path + '/scan'):
            os.remove(path + '/scan')
        
    def create_labeltxt(self):
        pass

    def set_tobin(self,flag):
        self.tobin = flag

    def set_label(self, labels):
        self.labels = labels

    def set_random_path(self, random_flag):
        self.random_flag = random_flag

    def set_random_cam_pos(self, cam_pos, range):
        self.cam_pos = cam_pos
        self.range = range
    
    def generate(self):
        for path in self.filepaths: 
            if self.random_flag:
                self.random_path()

            if self.cam_pos:
                self.random_camera_pos(self.range)
            scan_start(1, self.num_of_frame, str(path), 0.01) 
            self.remove_binfile(str(path))
            if self.tobin:
                convert_format(path, self.labels)
   
class ScanAnimationGroupPanel(bpy.types.Panel):
    bl_label = "Scan Animation Group"
    bl_idname = "OBJECT_PT_Scan_animation_group"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Blensor"


    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Animation Path", icon="INFO")
        row = layout.row()
        row.prop(context.scene.extrablensor_follow_param, "name")
        split = layout.split(percentage=0.33)
        split.label(text="Direct:")
        split.prop(context.scene.path_props, "direct", text=context.scene.path_props.direct_name(), toggle=True)
        col = layout.column()
        col.prop(context.scene.extrablensor_follow_param, "forward_axis")
        col.prop(context.scene.extrablensor_follow_param, "up_axis")
        # row.prop(context.scene.extrablensor_follow_param, "offset")
        col.enabled = False
        
        row = layout.row()
        sub = row.column()
        sub.enabled = False
        sub.prop(context.scene.extrablensor_follow_param, "use_curve_follow")
        row.prop(context.scene, "random_path", text="Path random")
        
       
        row = layout.row()
        row.label(text="")
        row.operator("extrablensor.record_follow_param", text="  Apply")
        layout.separator()

        row = layout.row()
        row.label(text="Animation Key Frame Range", icon="INFO")
        row = layout.row(align=True)
        row.prop(context.scene.extrablensor_follow_param, "start_frame")
        row.prop(context.scene.extrablensor_follow_param, "end_frame")
        row.enabled = False

        row = layout.row()
        row.label(text="")
        row.operator("extrablensor.mark_parks", text="Mark Parts")
        layout.separator()
        
       
        ####
        row = layout.row()
        row.label(text="Output Param", icon="INFO")
        row = layout.row()
        row.prop(context.scene, "extrablensor_group_folder_path")
        row = layout.row()
        row.prop(context.scene, "tobin_group", text="tobin")
        row.prop(context.scene, "extrablensor_numofset")
        layout.separator()

        box = layout.box()
        box.label("Aircraft Parts: ")
        for item in context.scene.extrablensor_obj_parts:
            row = box.row()
            row.label(text=item.name + ":")
            row.prop(item, "value")
        layout.separator()
                    
        box = layout.box()
        row = box.row()
        row.label(text="Select files:")
        row.operator("extrablensor.addfiles", text="", icon="PLUS")
        #col = box.column()
        for item in context.scene.extrablensor_selected_files:
            box.label(text=item.name)
        # row = layout.row()
        # row.operator("extrablensor.addfiles", text="")

        row = layout.row(align=True)
        row.label("")
        row.operator("extrablensor.scan_animation_group", text="Scan animation group")

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

            cloud_generator = CloudGenerator()
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
               
class ApplyAnimationFollowPathOperator(bpy.types.Operator):
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
                
class MarkPartsOperator(bpy.types.Operator):
    bl_idname = "extrablensor.mark_parks"
    bl_label = "Mark Parts"

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
        print("mark parts")
        return {'FINISHED'}

class AddFilesOperator(bpy.types.Operator):
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
    
class PathSelectProperties(bpy.types.PropertyGroup):
    direct = bpy.props.BoolProperty(
        name="Left",
        description="Select the left path",
        default = True
    )
    
    def direct_name(self):
        if self.direct:
            return "Left"
        else:
            return "Right"
        
class ZZScanAnimationGroup():
    
    def __init__(self):
        pass
    
    def register(self):
        bpy.utils.register_class(ScanAnimationGroupPanel)
        bpy.utils.register_class(ScanAnimationGroupOperator)
        bpy.utils.register_class(AddFilesOperator)
        bpy.utils.register_class(StringList)
        bpy.utils.register_class(LabelList)
        bpy.utils.register_class(ApplyAnimationFollowPathOperator)
        bpy.utils.register_class(FollowConstraint)
        bpy.utils.register_class(MarkPartsOperator)
        bpy.utils.register_class(PathSelectProperties)
        bpy.types.Scene.path_props = bpy.props.PointerProperty(type=PathSelectProperties)
        
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

    def unregister(self):
        bpy.utils.unregister_class(ScanAnimationGroupPanel)
        bpy.utils.unregister_class(ScanAnimationGroupOperator)
        bpy.utils.unregister_class(AddFilesOperator)
        bpy.utils.unregister_class(StringList)
        bpy.utils.unregister_class(LabelList)
        bpy.utils.unregister_class(ApplyAnimationFollowPathOperator)
        bpy.utils.unregister_class(FollowConstraint)
        bpy.utils.unregister_class(MarkPartsOperator)
    
    
if __name__ == "__main__":
    cloud_generator = CloudGenerator()
    cloud_generator.number_of_sets(1,3)
    cloud_generator.set_save_path('d:/data/', 'L')
    # cloud_generator.set_path_name('aircraft_path')
    cloud_generator.generate()
