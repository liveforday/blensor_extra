import numpy as np
import linecache
import glob
import os
import shutil

def rotate_x(points, yaw):

    theta = np.radians(yaw)

    rot_matrix = np.array([[np.cos(theta), -np.sin(theta), 0],
                       [np.sin(theta), np.cos(theta), 0],
                       [0, 0, 1]])
    
    rotated_points = np.dot(rot_matrix, points.T).T

    return rotated_points


def coord_conver(point):
    point[:, [1,2]] = point[:, [2, 1]]
    point[:,1] = -point[:,1]
    
    point = rotate_x(point, -90)
    return point


def load_from_pcd(path):
    text = linecache.getline(path, 10)
    points_num = int(text.split(' ')[-1])

    if points_num < 30:
        return None
    
    data = np.loadtxt(path, skiprows=11)
    return data


def convert_to_numbers(arr):
    sorted_arr = np.sort(arr)
    unique_vals, counts = np.unique(sorted_arr, return_counts=True)
    num_dict = {val: i+1 for i, val in enumerate(unique_vals)}
    num_arr = np.vectorize(num_dict.get)(arr)
    return num_arr


def pcd2bin(path):
    points = load_from_pcd(path)

    if points is None:
        return None

    points_without_label = coord_conver(points[:,:3])
    new_label = convert_to_numbers(points[:,-1])
    points = np.hstack((points_without_label, new_label.reshape(-1,1)))
    points = np.array(points, dtype=np.float32)
    save_path = path + '.bin'
    save_path = path.replace("pcd", "bin")
    points.tofile(save_path)

def convert_format(folder_path):
    for path in glob.glob(folder_path._str +"/*.pcd"):
        pcd2bin(path)

    