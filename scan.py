import bpy
import blensor
from blensor import evd
import random
import os
import time
from mathutils import Vector, Euler, Matrix
import random
from .conver_format import convert_format
# from bind_path import BindPath

def scan_range1(scanner_object, 
                frame_start, 
                frame_end, 
                filename="/tmp/landscape.evd", 
                frame_time = (1.0/24.0), 
                rotation_speed = 10.0, 
                add_blender_mesh=False, 
                add_noisy_blender_mesh=False, 
                angle_resolution = 0.1728,
                max_distance = 120.0,
                noise_mu = 0.0,
                noise_sigma= 0.02,
                last_frame = True,
                world_transformation=Matrix(),
                src_angle=-60.0, des_angle=60.0):
    
    start_time = time.time()
    angle_per_second = 360.0 * rotation_speed
    angle_per_frame = angle_per_second * frame_time
    
    for i in range(frame_start,frame_end):
        bpy.context.scene.frame_current = i
        ok,start_radians,scan_time = blensor.blendodyne.scan_advanced(
            scanner_object, 
            rotation_speed=rotation_speed,
            angle_resolution = angle_resolution, 
            start_angle = src_angle, 
            end_angle=des_angle, 
            evd_file = filename, 
            evd_last_scan=False, 
            add_blender_mesh=add_blender_mesh, 
            add_noisy_blender_mesh=add_noisy_blender_mesh, 
            frame_time=frame_time, 
            simulation_time = float(i)*frame_time,
            max_distance=max_distance, 
            noise_mu = noise_mu, 
            noise_sigma=noise_sigma, 
            world_transformation=world_transformation)


def scan_start(start, end, path, sigma):
    scanner = bpy.data.objects['Camera']
    filepath = path + '/scan.pcd'
    for i in range(start, end):
        evd.frame_counter = i
        blensor.blendodyne.randomize_distance_bias(scanner, noise_sigma = sigma)
        #blensor.blendodyne.scan_range(scanner, i, i+1, filepath, frame_time = (1/8),noise_sigma=sigma)
        scan_range1(scanner, i, i+1, filepath, frame_time = (1/8),noise_sigma=sigma)

from pathlib import Path
class SimCloudGenerator():
    def __init__(self) -> None:
        self.filepaths = []
        self.num_of_sets = 0
        self.num_of_frame = 0
        self.tobin = False
        bpy.context.scene.camera = bpy.data.objects['Camera']

    
    def set_save_path(self, root_path, suffix=''):
        root_path = Path(root_path)
        blendfile = Path(bpy.data.filepath)
        for i in range(self.num_of_sets): 
            filepath = root_path/f'pcd/{str(blendfile.stem)}_{i:03d}{suffix}'
            bin_filepath = root_path/f'bin/{str(blendfile.stem)}_{i:03d}{suffix}'
            self.filepaths.append(filepath)
            if os.path.exists(filepath):
                pass
            else:
                os.makedirs(filepath)

            if os.path.exists(bin_filepath):
                pass
            else:
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
        obj.location.z = random.uniform(5, 8)
        pass
    
    def remove_binfile(self, path):
        os.remove(path + '/scan')
        
    def create_labeltxt(self):
        pass

    def set_tobin(self,flag):
        self.tobin = flag
    
    def generate(self):
        for path in self.filepaths: 
            # self.random_path()
            # self.random_camera_pos()
            scan_start(1, self.num_of_frame, str(path), 0.01) 
            self.remove_binfile(str(path))
            if self.tobin:
                convert_format(path)
                

                
   

if __name__ == "__main__":
    cloud_generator = SimCloudGenerator()
    cloud_generator.number_of_sets(1,3)
    cloud_generator.set_save_path('d:/data/', 'L')
    # cloud_generator.set_path_name('aircraft_path')
    cloud_generator.generate()
