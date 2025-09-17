import bpy

import numpy as np
import os
import cv2

# Iterate over the lights in the data block and remove each
for camera in bpy.data.cameras:
    bpy.data.cameras.remove(camera)

# Read calibration parameters (.xml file)
calib_params = cv2.FileStorage('calib_parameters/calib_sl_python_trad_ao.xml', cv2.FILE_STORAGE_READ)

K1 = calib_params.getNode('K1').mat()
dist1_r = calib_params.getNode('dist1_r').mat()
dist1_t = calib_params.getNode('dist1_t').mat()

resx = 1280 # px
resy = 1024 # px
fx = K1[0,0]
fy = K1[1,1]
cx = K1[0,2] #resx/2 # px K1[0,2]
cy = K1[1,2] #resy/2 # px K1[1,2]
cam_sensor_width = 6.14 # mm (sensor size can be found in most camera data sheets.)
cam_sensor_height = 4.92 # mm

# camera configuration and creation
K = np.array([[fx,  0, cx],
              [ 0, fy, cy],
              [ 0,  0,  1]])
                
R = np.array([[1.0, 0.0, 0.0],	
              [0.0, 1.0, 0.0],	
              [0.0, 0.0, 1.0]])
              
T = np.array([0, 0, 0])  

# Create camera
bpy.ops.object.camera_add()
camera = bpy.data.objects['Camera']
camera_lens = bpy.data.objects['Camera'].data

# Set Blender camera extrinsic parameters
camera_rotx = 180
camera_roty = 0
camera_rotz = 0
camera_locx = 0
camera_locy = 0
camera_locz = 0

camera.location[0] = T[0]
camera.location[1] = T[1]
camera.location[2] = T[2]
camera.rotation_euler[0] = radians(camera_rotx)
camera.rotation_euler[1] = radians(camera_roty)
camera.rotation_euler[2] = radians(camera_rotz)

# Set Blender camera intrinsic parameters
_,_, focal_length,  principalPoint, aspectRatio = cv2.calibrationMatrixValues( K1, (resx, resy), cam_sensor_width, cam_sensor_height) 

camera_lens.sensor_fit = 'HORIZONTAL'
camera_lens.lens = focal_length
camera_lens.sensor_width = cam_sensor_width
camera_lens.sensor_height = cam_sensor_height

camera_lens.shift_x = 0.5 - (cx / resx)
#(0.5 - cx / resx) * cam_sensor_width / focal_length #-(cx / resx - 0.5)
camera_lens.shift_y = (fy/fx) * (resy/resx) * ((cy / resy) - 0.5)

#(cam_sensor_height/cam_sensor_width)*((cy / resy) - 0.5)#(cy - 0.5 * resy) / resx

# Create Blender scene and set the pixel aspect ratio
scene = bpy.data.scenes["Scene"]


scene.render.resolution_x = resx
scene.render.resolution_y = resy

pixel_aspect = fy / fx
scene.render.pixel_aspect_x = 1/pixel_aspect
scene.render.pixel_aspect_y = 1.0

#if pixel_aspect > 1:
#    scene.render.pixel_aspect_x = 1.0
#    scene.render.pixel_aspect_y = pixel_aspect
#else:
#    scene.render.pixel_aspect_x = 1.0
#    scene.render.pixel_aspect_y = 1.0 /pixel_aspect
    
# for visualization only
camera.scale[0]=.2
camera.scale[1]=.2
camera.scale[2]=.2