# import buildin package
import os
import time
import random
import shutil

import bpy
import blensor
from blensor import evd
from mathutils import Vector, Euler, Matrix

# import custom package
from .conver_format import convert_format
from .scan import scan_start, scan_range1

from pathlib import Path
class ScanAnimation():
    def __init__(self, root_path):
        root_path = Path(root_path)
        blendfile = Path(bpy.data.filepath)
        self.filepath = root_path/f'{str(blendfile.stem)}/pcd'
        bin_filepath = root_path/f'{str(blendfile.stem)}/bin'
        if os.path.exists(self.filepath):
            shutil.rmtree(self.filepath)
        os.makedirs(self.filepath)

        if os.path.exists(bin_filepath):
            shutil.rmtree(bin_filepath)
        os.makedirs(bin_filepath)

    def remove_binfile(self, path):
        os.remove(path + '/scan')

    def start(self, tobin):
        start_frame = bpy.context.scene.frame_start
        end_frame = bpy.context.scene.frame_end
        scan_start(start_frame, end_frame, str(self.filepath), 0.01)
        self.remove_binfile(str(self.filepath))
        if tobin:
            convert_format(self.filepath)

