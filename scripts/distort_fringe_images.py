# -*- coding: utf-8 -*-


import numpy as np
import cv2
import glob
import os
import matplotlib.pyplot as plt


fs = cv2.FileStorage('../calib_parameters/calib_TESIS.xml', cv2.FILE_STORAGE_READ)

# Read the matrices from the file
K1 = fs.getNode('K1').mat()
dist1_r = fs.getNode('dist1_r').mat()
dist1_t = fs.getNode('dist1_t').mat()
K2 = fs.getNode('K2').mat()
dist2_r = fs.getNode('dist2_r').mat()
dist2_t = fs.getNode('dist2_t').mat()
R = fs.getNode('R').mat()
t = fs.getNode('t').mat()

K = K2

#dist_coeffs = np.array([-0.122656746716572,	0.365219860230479, -0.00147098954992578, 0.000919274152451016, -0.539325524768831])
dist_coeffs = np.hstack((dist2_r[0, 0:2], dist2_t[0], 0)) #dist2_r[0, 2]

images = glob.glob('../fringe_images/projector_dell/*.bmp')


# Create a folder for the distorted images
output_folder = '../fringe_images/dell_distorted_nok3_not'
os.makedirs(output_folder, exist_ok=True)

for img_name in images:
    img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)

    h, w = img.shape[:2]

    # Generate grid of coordinates
    x, y = np.meshgrid(np.arange(w), np.arange(h))
    x = x.astype(np.float32)
    y = y.astype(np.float32)
    
    x = x.flatten()
    y = y.flatten()
    
    points = np.array([x,y])
    #points_norm = np.linalg.pinv(K)@points
    
    #x_normalized = points_norm[0]
    #y_normalized = points_norm[1]
    # Apply radial and tangential distortion
    #r2 = x_normalized**2 + y_normalized**2
    #r4 = r2**2  
    #r6 = r2**3
    
    k1, k2, p1, p2, k3 = dist_coeffs
    
    #x_distorted = x_normalized * (1 + k1 * r2 + k2 * r4 + k3 * r6) + 2 * p1 * x_normalized * y_normalized + p2 * (r2 + 2 * x_normalized**2)
    #y_distorted = y_normalized * (1 + k1 * r2 + k2 * r4 + k3 * r6) + p1 * (r2 + 2 * y_normalized**2) + 2 * p2 * x_normalized * y_normalized
    
    #denormalize
    #points_distorted_norm = np.array([x_distorted,y_distorted,np.ones(len(x_distorted))])
    #points_distorted = K@points_distorted_norm
    points_distorted = cv2.undistortPoints(points, K, dist_coeffs, P = K)
    x_distorted = points_distorted[:,:,0]
    y_distorted = points_distorted[:,:,1]
    
    # Remap the image
    map_x = x_distorted.reshape((h, w)).astype(np.float32)
    map_y = y_distorted.reshape((h, w)).astype(np.float32)
    distorted_img = cv2.remap(img, map_x, map_y, interpolation=cv2.INTER_LINEAR)
    
    # Save the distorted image
    output_path = os.path.join(output_folder, os.path.basename(img_name))
    cv2.imwrite(output_path, distorted_img)
    print(f"Saved distorted image to {output_path}")