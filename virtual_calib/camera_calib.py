import os
import bpy
import cv2
import datetime
import numpy as np

collection = bpy.data.collections.get('acircleboard.svg')
if collection:
    print('the calibration patters is already loaded')
else:
    bpy.ops.import_curve.svg(filepath = 'acircleboard.svg')
    collection = bpy.data.collections.get('acircleboard.svg')

curves = bpy.data.collections["acircleboard.svg"].all_objects

for obj in curves:
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target='MESH')

bpy.ops.object.join()
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
calibr_pattern = bpy.data.collections["acircleboard.svg"].all_objects[0]

poses_xml = cv2.FileStorage("calib_poses.xml", cv2.FILE_STORAGE_READ)
poses = poses_xml.getNode("calibr_poses").mat() 
nposes = np.shape(poses)[0]

# check if the xml file has registered valid poses
if nposes == ():
    print("The xml file does not contain any poses registered")
    os._exit(0)

# 05. we prepare the scene to capture the poses images
camera = bpy.data.objects['Camera']
scene = bpy.context.scene
scene.camera = camera
scene.use_nodes = True
scene_nodes = scene.node_tree
                   
calib_path = "E:/Documents/vision/vision-fpp-blender/calibrations"
calib_number = len(os.listdir(calib_path))

# Get the current date formatted as YYYY-MM-DD
current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

for pos in range(nposes):
    calibr_pattern.location =  poses[pos,0:3]
    calibr_pattern.rotation_euler = poses[pos,3:6]
    scene.render.image_settings.file_format = 'PNG'

    # Include the current date in the path
    cimg_camera_path = calib_path + "/calib_" + current_date + "/" + str(pos)
    bpy.context.scene.render.filepath = cimg_camera_path
    bpy.ops.render.render(use_viewport = True, write_still=True)