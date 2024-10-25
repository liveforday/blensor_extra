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
import sys
import bpy
from .scan_animation_group import ZZScanAnimationGroup
from .join_part import AAJoinParts

zz = ZZScanAnimationGroup()
aa = AAJoinParts()

def register():
    zz.register()
    aa.register()
    # bpy.types.Scene.tobin = bpy.props.BoolProperty(
    #     name="tobin",
    #     description = "if convert pcd to bin",
    #     default = True
    # )

if __name__ == "__main__":
    register()
