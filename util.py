import bpy

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