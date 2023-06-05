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

class StringList(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name")

class LabelList(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="")
    value = bpy.props.IntProperty(name="", default=0, subtype="UNSIGNED" )

class FollowConstraint(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Follow Path", default="Follow Path")
    path = bpy.props.StringProperty(name="path")
    obj = bpy.props.StringProperty(name="obj")

    target = bpy.props.PointerProperty(type=bpy.types.Object)
    offset = bpy.props.IntProperty(name="offset", default = 0, options={'HIDDEN', "SKIP_SAVE"})
    forward_axis = bpy.props.StringProperty(name="Forward")
    up_axis = bpy.props.StringProperty(name="Up")
    use_curve_follow = bpy.props.BoolProperty(name="Follow Curve")
    start_frame = bpy.props.IntProperty(name="start frame", default=1)
    end_frame = bpy.props.IntProperty(name="end frame", default=1)



def load_object_from(path):
    print(path)
    print(path._str)
    with bpy.data.libraries.load(path._str, link=False) as (data_from, data_to):
        for obj in data_from.objects:
            data_to.objects.append(obj)
                

    for obj in data_to.objects:
        bpy.context.scene.objects.link(obj)

def set_animation(follow_param, obj):
    follow_path_constraint = obj.constraints.new(type="FOLLOW_PATH")
    follow_path_constraint.target = follow_param.target
    follow_path_constraint.use_curve_follow = follow_param.use_curve_follow
    follow_path_constraint.forward_axis = follow_param.forward_axis

    bpy.context.scene.frame_start = follow_param.start_frame
    bpy.context.scene.frame_end = follow_param.end_frame
    follow_path_constraint.offset = 0.0
    follow_path_constraint.keyframe_insert(data_path='offset', frame=1)
    follow_path_constraint.offset = -100
    follow_path_constraint.keyframe_insert(data_path='offset', frame=100)


def delete_hierarchy(obj):
    for child in obj.children:
        delete_hierarchy(child) 

    bpy.context.scene.objects.unlink(obj)
    bpy.data.objects.remove(obj)

class ScanAnimationGroup():
    def __init__(self) -> None:
        self.filepaths = []
        self.num_of_sets = 0
        self.num_of_frame = 0
        self.tobin = False
        self.random_flag = True
        self.labels = None
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
    
    def random_camera_pos(self):
        obj = bpy.data.objects['Camera']
        obj.location.z = random.uniform(6, 8)
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
    
    def generate(self):
        for path in self.filepaths: 
            if self.random_flag:
                self.random_path()
                self.random_camera_pos()
            scan_start(1, self.num_of_frame, str(path), 0.01) 
            self.remove_binfile(str(path))
            if self.tobin:
                convert_format(path, self.labels)
                

                
   
if __name__ == "__main__":
    cloud_generator = ScanAnimationGroup()
    cloud_generator.number_of_sets(1,3)
    cloud_generator.set_save_path('d:/data/', 'L')
    # cloud_generator.set_path_name('aircraft_path')
    cloud_generator.generate()
