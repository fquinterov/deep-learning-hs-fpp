import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat, savemat
from scipy.ndimage import zoom

plt.close('all')

def map_camera_to_projector(camera_points, camera_matrix, projector_matrix, extrinsic_params, z_min_pixelwise):
    """
    Map camera pixels to projector pixels using calibration parameters and a pixel-wise z_min.

    Parameters:
        camera_points (ndarray): Camera pixel coordinates (Nx2).
        camera_matrix (ndarray): Intrinsic matrix of the camera.
        projector_matrix (ndarray): Intrinsic matrix of the projector.
        extrinsic_params (dict): Rotation (R) and translation (T) between camera and projector.
        z_min_pixelwise (ndarray): Pixel-wise depth map for z_min.

    Returns:
        projector_coords (ndarray): Corresponding projector pixel coordinates (Nx2).
    """
    R, T = extrinsic_params['R'], extrinsic_params['T']

    # Convert camera pixels to normalized coordinates
    cam_points_h = np.hstack((camera_points, np.ones((camera_points.shape[0], 1))))  # Homogeneous
    cam_normalized = np.linalg.inv(camera_matrix) @ cam_points_h.T  # Normalize

    # Ray-plane intersection using pixel-wise z_min
    scale = z_min_pixelwise.ravel() / cam_normalized[2, :]  # Scaling factor for depth
    world_coords = cam_normalized * scale  # Scale normalized rays to the depth plane

    # Transform world coordinates to the projector's frame
    projector_coords_h = R @ world_coords + T[:, np.newaxis]

    # Normalize to projector image plane
    projector_points = projector_matrix @ projector_coords_h
    projector_points /= projector_points[2, :]  # Normalize by depth

    return projector_points[:2, :].T  # Return projector coordinates (u_p, v_p)

def calculate_phi_min_from_calibration(projector_coords, fringe_period):
    """
    Calculate Phi_min using the vertical (v_p) projector coordinates.

    Parameters:
        projector_coords (ndarray): Projector coordinates (Nx2).
        fringe_period (float): Fringe period in projector pixels.

    Returns:
        phi_min (ndarray): Minimum phase map Phi_min using vertical coordinates.
    """
    v_p = projector_coords[:, 1]  # Projector vertical coordinates
    phi_min = (2 * np.pi * v_p) / fringe_period
    return phi_min

# Parameters
calib_dir = 'data\calib_params\One stage_TSC_0_calib_pyread2.mat'
depth_pred_file = 'data/example/mask_depth_pred.npy'  # Path to pixel-wise depth map
mat_contents = loadmat(calib_dir)
camera_width, camera_height = 1280, 1024  # Camera resolution in pixels
camera_points = np.array([[x, y] for y in range(camera_height) for x in range(camera_width)])  # Camera pixel grid
camera_matrix = mat_contents['K1']  # Intrinsic matrix for camera
projector_matrix = mat_contents['K2']  # Intrinsic matrix for projector
extrinsic_params = {
    'R': mat_contents['R'].T,  # Rotation matrix
    'T': mat_contents['t'][0]  # Translation vector
}
fringe_period = 18  # Fringe period in projector pixels

# Load pixel-wise z_min
z_min_pixelwise = np.load(depth_pred_file)  # Depth map from depth_pred_00.npy
print(f"Original depth map shape: {z_min_pixelwise.shape}")

plt.figure(figsize=(10, 6))
plt.imshow(z_min_pixelwise, cmap='viridis', aspect='auto')  # Unwrapped phase map
plt.colorbar(label='Phase (radians)')
plt.title(r"Predicted depth")
plt.xlabel("Camera Pixels (Horizontal)")
plt.ylabel("Camera Pixels (Vertical)")
plt.show()

# Resize depth map if dimensions do not match
if z_min_pixelwise.shape != (1024, 1280):
    scale_y = 1024 / z_min_pixelwise.shape[0]
    scale_x = 1280 / z_min_pixelwise.shape[1]
    z_min_pixelwise = zoom(z_min_pixelwise, (scale_y, scale_x), order=1)
    print(f"Resized depth map shape: {z_min_pixelwise.shape}")

# Map camera pixels to projector pixels using pixel-wise z_min
projector_coords = map_camera_to_projector(camera_points, camera_matrix, projector_matrix, extrinsic_params, z_min_pixelwise)

# Calculate Phi_min
phi_min_flat = calculate_phi_min_from_calibration(projector_coords, fringe_period)
phi_min = phi_min_flat.reshape(camera_height, camera_width)  # Reshape for 2D plotting

# Plot Phi_min (Unwrapped)
plt.figure(figsize=(10, 6))
plt.imshow(phi_min, cmap='viridis', aspect='auto')  # Unwrapped phase map
plt.colorbar(label='Phase (radians)')
plt.title(r"Unwrapped Minimum Phase Map (Phase in $Y$)")
plt.xlabel("Camera Pixels (Horizontal)")
plt.ylabel("Camera Pixels (Vertical)")
plt.show()

# Read wrapped phase
phase_dir = 'data/example/mask_wrapped_phase.mat'
mat_phase = loadmat(phase_dir)
wrapped_phase = mat_phase['ph']

plt.figure(figsize=(10, 6))
plt.imshow(wrapped_phase, cmap='viridis', aspect='auto')  # Wrapped phase map
plt.colorbar(label='Phase (radians)')
plt.title(r"Wrapped Phase Map")
plt.xlabel("Camera Pixels (Horizontal)")
plt.ylabel("Camera Pixels (Vertical)")
plt.show()

# Calculate fringe order and unwrapped phase
K = np.ceil((phi_min - wrapped_phase) / (2 * np.pi))
abs_phase = wrapped_phase + (2 * np.pi * K)

plt.figure(figsize=(10, 6))
plt.imshow(abs_phase, cmap='viridis', aspect='auto')  # Unwrapped phase map
plt.colorbar(label='Phase (radians)')
plt.title(r"Unwrapped Phase Map")
plt.xlabel("Camera Pixels (Horizontal)")
plt.ylabel("Camera Pixels (Vertical)")
plt.show()

# Save the absolute phase to a .mat file
output_file = "abs_phase_pose_04_with_depth_pred.mat"
savemat(output_file, {"ph": abs_phase})
