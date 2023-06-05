# import buildin package
import time

import bpy
import blensor
from blensor import evd
from mathutils import Vector, Euler, Matrix

# import custom package
from .conver_format import convert_format

def scan_range1(scanner_object, 
                frame_start, 
                frame_end, 
                filename="/tmp/landscape.evd", 
                frame_time = (1.0/24.0), 
                rotation_speed = 10.0, 
                add_blender_mesh=False, 
                add_noisy_blender_mesh=False, 
                angle_resolution = 0.1728,
                max_distance = 300.0,
                noise_mu = 0.0,
                noise_sigma= 0.02,
                last_frame = True,
                world_transformation=Matrix(),
                src_angle=0.0, des_angle=360.0):
    
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
