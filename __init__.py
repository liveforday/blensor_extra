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
from .scan import SimCloudGenerator

class ExtraBlensor(bpy.types.Panel):
    bl_label = "Extra Blensor"
    bl_idname = "OBJECT_PT_extra_blensor"
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
        
        row = layout.row()
        row.prop(context.scene, "extrablensor_numofset")



class ScanAnimation(bpy.types.Operator):
    bl_idname = "extrablensor.scan_animation"
    bl_label = "Scan Animation"

    def execute(self, context):
        # This is where the code for your operator goes
        save_path = context.scene.extrablensor_folder_path
        num_of_set = context.scene.extrablensor_numofset
        tobin = context.scene.tobin
        cloud_generator = SimCloudGenerator()
        cloud_generator.set_tobin(tobin)
        cloud_generator.number_of_sets(num_of_set)
        cloud_generator.set_save_path(save_path, 'L')
        cloud_generator.set_path_name('aircraft_path')
        cloud_generator.generate()
        print("scaning")
        return {'FINISHED'}




def register():
    bpy.utils.register_class(ExtraBlensor)
    bpy.utils.register_class(ScanAnimation)

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

    bpy.types.Scene.extrablensor_numofset = bpy.props.IntProperty(
        name="num of set",
        description = "num of set",
        default = 1,
        subtype='UNSIGNED'
    )


def unregister():
    bpy.utils.unregister_class(ExtraBlensor)
    bpy.utils.unregister_class(ScanAnimation)

if __name__ == "__main__":
    register()
