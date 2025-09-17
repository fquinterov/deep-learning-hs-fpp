import os
import cv2
import bpy
import numpy as np
from scipy.spatial.transform import Rotation   

# Iterate over the lights in the data block and remove each
for light in bpy.data.lights:
    bpy.data.lights.remove(light)
    
# Add a light object to the scene    
bpy.ops.object.light_add(type='POINT')
projector = bpy.data.objects['Point']

# Use nodes for the light
bpy.data.lights[0].use_nodes = True

# Create the node tree
projector_nodes = bpy.data.lights["Point"].node_tree

# Create nodes
node_texture_coordinate = projector_nodes.nodes.new("ShaderNodeTexCoord")
node_mapping = projector_nodes.nodes.new("ShaderNodeMapping")
node_separate_xyz = projector_nodes.nodes.new("ShaderNodeSeparateXYZ")
node_dividex = projector_nodes.nodes.new("ShaderNodeMath")
node_dividey = projector_nodes.nodes.new("ShaderNodeMath")
node_addx = projector_nodes.nodes.new("ShaderNodeMath")
node_addy = projector_nodes.nodes.new("ShaderNodeMath")
node_dividex1 = projector_nodes.nodes.new("ShaderNodeMath")
node_dividey1 = projector_nodes.nodes.new("ShaderNodeMath")
node_combine_xyz = projector_nodes.nodes.new("ShaderNodeCombineXYZ")
node_tex_img = projector_nodes.nodes.new("ShaderNodeTexImage")
node_emission = projector_nodes.nodes['Emission']

node_dividex.operation = "DIVIDE"
node_dividey.operation = "DIVIDE"
node_dividex1.operation = "DIVIDE"
node_dividey1.operation = "DIVIDE"
node_addx.operation = "ADD"
node_addy.operation = "ADD"

# Specify the position of each node
projector_nodes.nodes["Texture Coordinate"].location = [0,0]
projector_nodes.nodes["Mapping"].location = [200,0]
projector_nodes.nodes["Separate XYZ"].location = [400,0]
projector_nodes.nodes["Math"].location = [600, 0]
projector_nodes.nodes["Math.001"].location = [600, -200]
projector_nodes.nodes["Math.002"].location = [800, 0]
projector_nodes.nodes["Math.003"].location = [800, -200]
projector_nodes.nodes["Math.004"].location = [1000, 0]
projector_nodes.nodes["Math.005"].location = [1000, -200]
projector_nodes.nodes["Combine XYZ"].location = [1200, 0]
projector_nodes.nodes["Image Texture"].location = [1400, 0]
projector_nodes.nodes["Emission"].location = [1700, 0]
projector_nodes.nodes["Light Output"].location = [1900, 0]

# Link nodes
projector_nodes.links.new(node_texture_coordinate.outputs[1], node_mapping.inputs[0])
projector_nodes.links.new(node_mapping.outputs[0], node_separate_xyz.inputs[0])
projector_nodes.links.new(node_separate_xyz.outputs[0], node_dividex.inputs[0])
projector_nodes.links.new(node_separate_xyz.outputs[2], node_dividex.inputs[1])
projector_nodes.links.new(node_separate_xyz.outputs[1], node_dividey.inputs[0])
projector_nodes.links.new(node_separate_xyz.outputs[2], node_dividey.inputs[1])
projector_nodes.links.new(node_dividex.outputs[0], node_addx.inputs[0])
projector_nodes.links.new(node_dividey.outputs[0], node_addy.inputs[0])
projector_nodes.links.new(node_addx.outputs[0], node_dividex1.inputs[0])
projector_nodes.links.new(node_addy.outputs[0], node_dividey1.inputs[0])
projector_nodes.links.new(node_dividex1.outputs[0], node_combine_xyz.inputs[0])
projector_nodes.links.new(node_dividey1.outputs[0], node_combine_xyz.inputs[1])
projector_nodes.links.new(node_combine_xyz.outputs[0], node_tex_img.inputs[0])
projector_nodes.links.new(node_tex_img.outputs[0], node_emission.inputs[0])


# Read calibration parameters (.xml file)
calib_params = cv2.FileStorage('calib_parameters/calib_sl_python_trad_ao.xml', cv2.FILE_STORAGE_READ)

K2 = calib_params.getNode('K2').mat()
dist2_r = calib_params.getNode('dist2_r').mat()
dist2_t = calib_params.getNode('dist2_t').mat()
R = calib_params.getNode('R').mat()
t = calib_params.getNode('t').mat()

# Combine R and t into a 3x4 matrix
transformation_matrix = np.hstack((R, t))

# Add the last row [0, 0, 0, 1] to make it a 4x4 matrix
transformation_matrix = np.vstack((transformation_matrix, [0, 0, 0, 1]))

# Compute the pseudo-inverse of the transformation matrix
M_p = np.linalg.pinv(transformation_matrix)
p = M_p@np.array([0,0,0,1])
Rp = M_p[:3, :3]

#p = -R.T@t
#Rp = R.T

resx = 1280
resy = 800
fx = K2[0,0]
fy = K2[1,1]
cx = K2[0,2] #resx/2 # px
cy = K2[1,2] #resy/2 # px

projector.location[0] = p[0]/1000
projector.location[1] = p[1]/1000
projector.location[2] = p[2]/1000

rot_matrix = Rotation.from_matrix(Rp)
angles = rot_matrix.as_euler("xyz",degrees=False)
projector.rotation_euler[0] = angles[0]
projector.rotation_euler[1] = angles[1]
projector.rotation_euler[2] = angles[2]

projector_nodes.nodes["Combine XYZ"].inputs[2].default_value = 1
projector_nodes.nodes["Image Texture"].extension = 'CLIP'
projector_nodes.nodes["Math.002"].inputs[1].default_value = cx #-(cx / resx) #(cx / resx) - 1
projector_nodes.nodes["Math.003"].inputs[1].default_value = (resy-cy) #-(cy / resy) + 1
projector_nodes.nodes["Math.004"].inputs[1].default_value = resx
projector_nodes.nodes["Math.005"].inputs[1].default_value = resy

projector_nodes.nodes["Mapping"].vector_type = 'POINT'
projector_nodes.nodes["Mapping"].inputs[3].default_value[0] = fx
projector_nodes.nodes["Mapping"].inputs[3].default_value[1] = -fy

fringe_img = bpy.data.images.load("E:/OneDrive - Universidad Tecnológica de Bolívar/Structured Light Stuff/Digital twin blender/fringe_images/projector_dell_AO_eberto/H_P18_F18.bmp") #"D:/Fernando Quintero/One drive/OneDrive - Universidad Tecnológica de Bolívar/Structured Light Stuff/Digital twin blender/fringe_images/lightcrafter/H_P18_F18.BMP", "E:/OneDrive - Universidad Tecnológica de Bolívar/Structured Light Stuff/Digital twin blender/fringe_images/lightcrafter/H_P18_F18.BMP"

# Set the image texture to the loaded fringe image
projector_nodes.nodes["Image Texture"].image = fringe_img