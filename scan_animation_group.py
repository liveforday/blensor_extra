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
        self.is_random_cam = True
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
        # # change path direct
        # key_points[0].co.x = -key_points[0].co.x
        # key_points[1].co.x = -key_points[1].co.x

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
        
        self.draw_animation_path_panel(context)
        
        self.draw_title("Range Key Frame && Camera Height")
        self.draw_animation_keyframe_range(context)
        self.draw_camera_range(context)
        self.draw_mark_object_parts(context)
        self.draw_output_setting(context)
        self.draw_select_files(context)

        row = layout.row(align=True)
        row.label("")
        row.operator("extrablensor.scan_animation_group", text="Scan animation group")
        
    def draw_animation_path_panel(self, context):
        scan_props = context.scene.scan_props
        self.draw_title("Animation Path")
        row = self.layout.row()
        row.prop(scan_props, "selectable_obj")
        row.prop(scan_props, "selectable_constraints")
        # split = self.layout.split(percentage=0.33)
        # split.label(text="Direct:")
        # split.prop(scan_props, "direct", text=scan_props.direct_label, toggle=True)
    
        col = self.layout.column()
        col.prop(scan_props.follow_path, "forward_axis")
        col.prop(scan_props.follow_path, "up_axis")
        col.enabled = False
        
        row = self.layout.row()
        sub = row.column()
        sub.enabled = False
        sub.prop(scan_props.follow_path, "use_curve_follow")
        obj = bpy.data.objects[scan_props.selectable_obj]
        if(obj.type == "EMPTY"):
            row.prop(scan_props, "is_random_path")
        elif(obj.type == "CAMERA"):
            row.prop(scan_props, "is_random_cam")
        
        row = self.layout.row()
        row.label(text="")
        row.operator("extrablensor.record_follow_param", text="  Apply")
        self.layout.separator()
        
    def draw_animation_keyframe_range(self, context):
        scan_props = context.scene.scan_props
        row = self.layout.row(align=True)
        row.prop(scan_props.follow_path, "start_frame")
        row.prop(scan_props.follow_path, "end_frame")
        row.enabled = False
        
    def draw_camera_range(self, context):
        scan_props = context.scene.scan_props
        row = self.layout.row(align=True)
        row.prop(scan_props, "cam_height_lower")
        row.prop(scan_props, "cam_height_higher")
        self.layout.separator()
        
    def draw_mark_object_parts(self, context):
        self.draw_title("Mark Object Part")
        scan_props = context.scene.scan_props
        box = self.layout.box()
        row = box.row()
        row.prop(scan_props, "markable_obj")
        row.operator("extrablensor.mark_parks", text="Mark Parts")
        for item in scan_props.obj_parts:
            row = box.row()
            row.label(text=item.name + ":")
            row.prop(item, "value")
        self.layout.separator()
    
    def draw_output_setting(self, context):
        self.draw_title("Output Setting")
        scan_props = context.scene.scan_props
        row = self.layout.row()
        row.prop(scan_props, "output_path")
        row = self.layout.row()
        row.prop(scan_props, "tobin", text="tobin")
        row.prop(scan_props, "numofset")
        self.layout.separator()
        
    def draw_select_files(self, context):
        self.draw_title("Select Files")
        scan_props = context.scene.scan_props
        box = self.layout.box()
        row = box.row()
        row.label(text="Select files:")
        row.operator("extrablensor.addfiles", text="Add Files")
        for item in scan_props.files_to_convert:
            box.label(text=item.name)
        
    def draw_title(self, title):
        row = self.layout.row()
        row.label(text=title, icon="INFO")
        
class ScanAnimationGroupOperator(bpy.types.Operator):
    bl_idname = "extrablensor.scan_animation_group"
    bl_label = "Scan Animation Group"

    def execute(self, context):
        if(not self.is_input_validate(context)):
            return {'FINISHED'}
        
        scan_props = context.scene.scan_props
        obj = bpy.data.objects[scan_props.follow_path.obj]
        con_obj = bpy.data.objects[scan_props.selectable_obj]
        
        if con_obj.type == "CAMERA":
            scan_props.is_random_path = False
            
        delete_hierarchy(obj)

        for blend_file in scan_props.files_to_convert:
            blend_path = Path(blend_file.name)
            load_object_from(blend_path)

            if scan_props.follow_path.path == scan_props.follow_path.obj:
                obj_new = bpy.data.objects[blend_path.stem]
                set_animation(scan_props.follow_path, obj_new )
                
            print("generator")

            cloud_generator = CloudGenerator()
            cloud_generator.set_tobin(scan_props.tobin)
            cloud_generator.set_random_path(scan_props.is_random_path)
            cloud_generator.set_random_cam_pos(scan_props.is_random_cam, [scan_props.cam_height_lower, scan_props.cam_height_higher])
            cloud_generator.number_of_sets(scan_props.numofset)
            cloud_generator.set_save_path(scan_props.output_path, blend_path.stem,'')
            cloud_generator.set_label(self.get_part_marks(scan_props.obj_parts))
            cloud_generator.set_path_name('aircraft_path')
            cloud_generator.generate()
            delete_hierarchy(bpy.data.objects[blend_path.stem])

        load_object_from(scan_props.follow_path.obj)
        return {'FINISHED'}
    
    def is_input_validate(self, context):
        scan_props = context.scene.scan_props
        if(not scan_props.selectable_constraints):
            self.report({'WARNING'}, "No vaild Animation Path!")
            return False
        
        if(not scan_props.markable_obj):
            self.report({'WARNING'}, "No vaild Mark Object!")
            return False
        
        if(not scan_props.files_to_convert):
            self.report({'WARNING'}, "No vaild Select Files list !")
            return False
        return True
    
    def get_part_marks(self, obj_parts):
        labels = []
        for item in obj_parts:
            label = [item.name, item.value] 
            labels.append(label)
        return labels
               
class ApplyAnimationFollowPathOperator(bpy.types.Operator):
    bl_idname = "extrablensor.record_follow_param"
    bl_label = "Record Follow Path Param"

    def execute(self, context):
        if(not self.is_input_validate(context)):
            return {'FINISHED'}
        scan_props = context.scene.scan_props
        obj = bpy.data.objects[scan_props.selectable_obj]
        if(not scan_props.selectable_constraints):
            self.report({'WARNING'}, "No vaild constraint!")
            return {"FINISHED"}
        
        follow_path_constraint = obj.constraints[scan_props.selectable_constraints]
        scan_props.follow_path.path             = obj.name
        scan_props.follow_path.offset           = follow_path_constraint.offset_factor
        scan_props.follow_path.forward_axis     = follow_path_constraint.forward_axis
        scan_props.follow_path.up_axis          = follow_path_constraint.up_axis
        scan_props.follow_path.use_curve_follow = follow_path_constraint.use_curve_follow
        scan_props.follow_path.target           = follow_path_constraint.target
        scan_props.follow_path.start_frame      = context.scene.frame_start
        scan_props.follow_path.end_frame        = context.scene.frame_end
        return {'FINISHED'}
    
    def is_input_validate(self, context):
        scan_props = context.scene.scan_props
        if(not scan_props.selectable_constraints):
            self.report({'WARNING'}, "No vaild Animation Path!")
            return False
        return True
              
class MarkPartsOperator(bpy.types.Operator):
    bl_idname = "extrablensor.mark_parks"
    bl_label = "Mark Parts"

    def execute(self, context):
        if(not self.is_input_validate(context)):
            return {'FINISHED'}
        scan_props = context.scene.scan_props
        scan_props.follow_path.obj = scan_props.markable_obj
        scan_props.obj_parts.clear()
        i = 0
        for child  in bpy.data.objects[scan_props.markable_obj].children:
            item = scan_props.obj_parts.add()
            item.name = child.name
            item.value = i
            i += 1
            pass
        print("mark parts")
        return {'FINISHED'}
    
    def is_input_validate(self, context):
        scan_props = context.scene.scan_props
        
        if(not scan_props.markable_obj):
            self.report({'WARNING'}, "No vaild Mark Object!")
            return False
        return True

class AddFilesOperator(bpy.types.Operator):
    bl_idname = "extrablensor.addfiles"
    bl_label = "Add Files"

    # files = bpy.props.CollectionProperty(
    #     type=bpy.types.OperatorFileListElement,
    #     options={'REGISTER','INTERNAL'}
    # )
    filename_ext = ".blend"
    filter_glob = bpy.props.StringProperty(default="*.blend", options={'HIDDEN'})

    files= bpy.props.CollectionProperty(
        type=bpy.types.OperatorFileListElement
    )
    
    directory = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        scan_props = context.scene.scan_props
        # Use Blender's file browser to select multiple files
        scan_props.files_to_convert.clear()
        for file in self.files:
            filepath = self.directory + file.name
            item = scan_props.files_to_convert.add()
            item.name = filepath
            pass

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
       # return super().invoke(context, event)

class ScanAnimationGroupProperties(bpy.types.PropertyGroup):
    
    def update_selectable_list(self, context):
        items = [ (obj.name, obj.name, "") for obj in bpy.data.objects if obj.type == "EMPTY" or obj.type == "CAMERA"]
        return items
    
    selectable_obj =  bpy.props.EnumProperty(
            name="Object name",
            description = "Select an object",
            items=update_selectable_list,
        )
    
    def update_selectable_constraints(self, context):
        scan_props = context.scene.scan_props
        obj = bpy.data.objects[scan_props.selectable_obj]
        items=[]
        for con in obj.constraints:
            items.append((con.name, con.name, ""))
        return items
        
    selectable_constraints = bpy.props.EnumProperty(
        name="Object name",
        description = "Select an object",
        items=update_selectable_constraints,
    )
    
    # def update_label(self):
    #     self.direct_label = "Left" if self.direct else "Right"
        
    # direct = bpy.props.BoolProperty(
    #     name = "Direct",
    #     default = True,
    #     update = lambda self, context: self.update_label()
    # )
    
    direct_label = bpy.props.StringProperty(
        name="Label Text",
        default = "Left"
    )
    
    follow_path = bpy.props.PointerProperty(type=FollowConstraint)
    
    is_random_path = bpy.props.BoolProperty(
        name = "Path random",
        default = True,
    )
    
    is_random_cam = bpy.props.BoolProperty(
        name="Camera random",
        description = "if random camera height",
        default = True
    ) 
    
    obj_parts = bpy.props.CollectionProperty(type=LabelList)
    
    output_path = bpy.props.StringProperty(
            name="Output Location",
            description = "Output Location",
            default = "D:/data/",
            subtype='DIR_PATH'
        )
    
    tobin = bpy.props.BoolProperty(
            name="tobin",
            description = "if convert pcd to bin",
            default = True
        )
    
    numofset = bpy.props.IntProperty(
            name="num of set",
            description = "num of set",
            default = 1,
            subtype='UNSIGNED'
            )
    
    files_to_convert = bpy.props.CollectionProperty(type=StringList)
       
    cam_height_higher = bpy.props.IntProperty(
            name="high limit",
            description = "camera position top limit",
            default = 8,
            subtype='UNSIGNED'
            )

    cam_height_lower = bpy.props.IntProperty(
            name="low limit",
            description = "camera position low limit",
            default = 5,
            subtype='UNSIGNED'
            )
    
    def update_markable_list(self, context):
        items = [ (obj.name, obj.name, "") for obj in bpy.data.objects if obj.type == "EMPTY"]
        return items
            
    markable_obj =  bpy.props.EnumProperty(
            name="Object name",
            description = "Select an object",
            items=update_markable_list,
        )
    
   
    
class ScanAnimationGroup():
    
    def __init__(self):
        pass
    
    def register(self):
        bpy.utils.register_class(ScanAnimationGroupPanel)
        bpy.utils.register_class(ScanAnimationGroupOperator)
        bpy.utils.register_class(ApplyAnimationFollowPathOperator)
        bpy.utils.register_class(AddFilesOperator)
        bpy.utils.register_class(MarkPartsOperator)
        
        bpy.utils.register_class(StringList)
        bpy.utils.register_class(LabelList)
        bpy.utils.register_class(FollowConstraint)
        bpy.utils.register_class(ScanAnimationGroupProperties)
        bpy.types.Scene.scan_props = bpy.props.PointerProperty(type=ScanAnimationGroupProperties)


       
    def unregister(self):
        bpy.utils.unregister_class(ScanAnimationGroupPanel)
        bpy.utils.unregister_class(ScanAnimationGroupOperator)
        bpy.utils.unregister_class(ApplyAnimationFollowPathOperator)
        bpy.utils.unregister_class(AddFilesOperator)
        bpy.utils.unregister_class(MarkPartsOperator)
        
        bpy.utils.unregister_class(StringList)
        bpy.utils.unregister_class(LabelList)
        bpy.utils.unregister_class(FollowConstraint)
        bpy.utils.unregister_class(ScanAnimationGroupProperties)
    
    
if __name__ == "__main__":
    cloud_generator = CloudGenerator()
    cloud_generator.number_of_sets(1,3)
    cloud_generator.set_save_path('d:/data/', 'L')
    # cloud_generator.set_path_name('aircraft_path')
    cloud_generator.generate()
