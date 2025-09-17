import numpy as np
import cv2
import os
import glob

# Read the calibration data
fs = cv2.FileStorage('../calib_parameters/calib_sl_python_trad_ao.xml', cv2.FILE_STORAGE_READ)
K1 = fs.getNode('K1').mat()
dist1_r = fs.getNode('dist1_r').mat()
dist1_t = fs.getNode('dist1_t').mat()
K2 = fs.getNode('K2').mat()
dist2_r = fs.getNode('dist2_r').mat()
dist2_t = fs.getNode('dist2_t').mat()
R = fs.getNode('R').mat()
t = fs.getNode('t').mat()
fs.release()

K = K1
#dist_coeffs = np.array([-0.122656746716572,	0.365219860230479, -0.00147098954992578, 0.000919274152451016, -0.539325524768831])
dist_coeffs = np.hstack((-2.8857770805167512e-03, -9.6478836804189727e-02, -6.9640053469271156e-04, -2.5824914554488973e-04,  0))
# Directory of images to distort
input_dir = '../calibrations/r3d_pose_08_AO3'
output_dir = '../calibrations/r3d_pose_08_AO3_distorted'

# Create the output directory structure, mirroring the input structure
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Process each image in the directory structure
for root, dirs, files in os.walk(input_dir):
    for file in files:
        if file.endswith(".png"):
            img_path = os.path.join(root, file)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

            h, w = img.shape[:2]
            x, y = np.meshgrid(np.arange(w), np.arange(h))
            points = np.c_[x.ravel(), y.ravel()].astype(np.float32)

            # Distorting the points
            points_distorted = cv2.undistortPoints(np.expand_dims(points, axis=1), K, dist_coeffs, P=K)
            x_distorted = points_distorted[:, :, 0].reshape(h, w)
            y_distorted = points_distorted[:, :, 1].reshape(h, w)

            # Remapping the image
            distorted_img = cv2.remap(img, x_distorted, y_distorted, interpolation=cv2.INTER_LINEAR)

            # Saving the distorted image in corresponding structure
            output_path = img_path.replace(input_dir, output_dir)
            output_folder = os.path.dirname(output_path)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            cv2.imwrite(output_path, distorted_img)
            print(f"Saved distorted image to {output_path}")
