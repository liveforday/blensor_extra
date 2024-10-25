import bpy
import sys
import os
from .util import *

def get_context():
    for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                context = bpy.context.copy()
                context['area'] = area
    return context

class Part(object):
    def __init__(self, name):
        self.name = name
        self.part_list = []
        
    def join(self):  
        if len(self.part_list) == 0:
            return
        if len(self.part_list) == 1:
            pass

        for  part in self.part_list:
            bpy.data.objects[part].select = True

        bpy.context.scene.objects.active = bpy.data.objects[self.part_list[0]]
        bpy.ops.object.join()
        bpy.data.objects[self.part_list[0]].name = self.name
        bpy.ops.object.select_all(action='DESELECT')


def import_obj(path):
    pass 


def obj2blend(parts_name, obj_path, save_path):
    #get aircraft name
    # airc_name = obj_path.split('/')[-1].split('+')[-1][:-4]
    airc_name = obj_path.stem

    #import obj
    print(obj_path)
    bpy.ops.import_scene.obj(filepath=obj_path._str)
    bpy.ops.object.select_all(action='DESELECT')

    # create parts container
    parts_container = []
    for name in parts_name:
        parts_container.append(Part(name))

    #add parts to container which it is belong
    for obj in bpy.data.objects:
        for part in parts_container:
            if part.name in obj.name:
                part.part_list.append(obj.name)

    # part join 
    for part in parts_container:
        part.join()

    # add a refence point in (0,0) named 'airc_name'
    context = get_context()
    bpy.ops.view3d.snap_cursor_to_center(context)
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    bpy.data.objects['Empty'].name = airc_name

    #  select parts 
    for name in parts_name:
        bpy.data.objects[name].select = True

    bpy.ops.object.parent_set(type='OBJECT')
    
    
    part_path = save_path + f'/{len(parts_name)}_part/{airc_name}.blend'
    part_dir = save_path + f'/{len(parts_name)}_part'
    if os.path.exists(part_dir):
        pass
    else:
        os.makedirs(part_dir)
        
    bpy.ops.wm.save_as_mainfile(filepath=part_path)
    
    # part join
    bpy.ops.object.select_all(action='SELECT')
    bpy.data.objects[airc_name].select = False
    bpy.context.scene.objects.active = bpy.data.objects[parts_name[0]]
    bpy.ops.object.join()
    bpy.data.objects[parts_name[0]].name = 'aircraft'
    
    part_0path = save_path + '/0_part/{}.blend'.format(airc_name)
    bpy.ops.wm.save_as_mainfile(filepath=part_0path)
    
    # delete all object except camera
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # part join
    
    # part_0path = save_path + '/0_part/{}.blend'.format(airc_name)
    # bpy.ops.wm.save_as_mainfile(filepath=part_5path)


# import param
# parts_name = ['body', 'wing', 'engine', 'empennage', 'wheel']
# parts_name = ['nose','body', 'L_wing', 'R_wing', 'L_engine', 'R_engine', 'empennage', 'wheel']
# save_path = 'D:/project/vdgs_project/数据/飞机模型�?/1.民航/3.blend_model'
# path = 'D:/project/vdgs_project/数据/飞机模型�?/1.民航/2.obj_model/path.txt'

# # read objpath�? change path acroding to os
# f = open(path, 'r', encoding='utf-8')
# obj_paths_str = f.read().splitlines()
# obj_paths = []
# if sys.platform.startswith('win'):
#     for path in obj_paths_str:
#         path = path[1] + ':' + path[2:] 
#         obj_paths.append(path)
# else:
#     pass
         
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete()
# for obj_path in obj_paths:
#     obj2blend(parts_name, obj_path, save_path)


from .join_part import obj2blend
from pathlib import Path

# module_path = os.path.dirname(__file__)
# print("path :", module_path)
# sys.path.append(module_path)

# import zz_scan_animation_group

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


class AAJoinParts():
    def __init__(self):
        pass
    
    def register(self):
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