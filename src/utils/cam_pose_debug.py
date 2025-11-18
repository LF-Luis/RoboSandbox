import numpy as np
import genesis as gs


class CamPoseDebug:

    def __init__(self, camera, verbose = False):
        """
        Initialize camera debug layout with movement and rotation controls.
        Works with camera's current pose for all transformations.

        Args:
            camera: Genesis camera object to control
        """
        self._cam = camera
        self._verbose = verbose

        # Define movement vectors in local coordinates
        self._directions = {
            'right':   np.array([1, 0, 0]),
            'left':     np.array([-1, 0, 0]),
            'up':       np.array([0, 1, 0]),
            'down':     np.array([0, -1, 0]),
            'forward':  np.array([0, 0, -1]),
            'backward': np.array([0, 0, 1]),
        }

    # Movement shortcuts
    def left(self, d=0.1): self._move_camera('left', d)
    def right(self, d=0.1): self._move_camera('right', d)
    def up(self, d=0.1): self._move_camera('up', d)
    def down(self, d=0.1): self._move_camera('down', d)
    def forward(self, d=0.1): self._move_camera('forward', d)
    def back(self, d=0.1): self._move_camera('backward', d)

    # Rotation shortcuts
    def roll(self, angle=10): self._rotate_camera('x', angle)
    def pitch(self, angle=10): self._rotate_camera('y', angle)
    def yaw(self, angle=10): self._rotate_camera('z', angle)

    def log_spatial_info(self):
        if self._verbose:
            print(f"pos: {self._cam.pos} \nlookat: {self._cam.lookat} \ntransform: {self._cam.transform} \nextrinsics: {self._cam.extrinsics}")

    def _move_camera(self, direction, distance):
        """
        Move camera in a specified direction by a given distance.
        Uses camera's current transform for movement direction.

        Args:
            direction: 'left', 'right', 'up', 'down', 'forward', 'backward'
            distance: float, distance to move in meters
        """
        # Get current transform
        current_transform = self._cam.transform
        current_pos = self._cam.pos

        # Extract rotation part from transform (3x3 rotation matrix)
        current_rot = current_transform[:3, :3]

        # Convert direction vector to world coordinates using current rotation
        move_vector = current_rot @ (self._directions[direction] * distance)

        # Calculate new position
        new_pos = current_pos + move_vector

        # Create new transform, keeping the same rotation
        new_transform = current_transform.copy()
        new_transform[:3, 3] = new_pos

        # Update camera
        self._cam.set_pose(transform=new_transform)
        self._cam.render()

        self.log_spatial_info()

    def _rotate_camera(self, axis, angle_degrees):
        """
        Rotate camera around specified axis by given angle.

        Args:
            axis: 'x', 'y', or 'z'
            angle_degrees: float, angle in degrees (positive is counterclockwise)
        """
        # Get current transform
        current_transform = self._cam.transform
        current_pos = np.asarray(self._cam.pos, dtype=np.float32)

        # Convert angle to radians
        angle_rad = np.deg2rad(angle_degrees)

        # Create rotation quaternion [w, x, y, z] with consistent dtype
        if axis == 'x':
            rot_quat = np.array([np.cos(angle_rad/2), np.sin(angle_rad/2), 0, 0], dtype=np.float32)
        elif axis == 'y':
            rot_quat = np.array([np.cos(angle_rad/2), 0, np.sin(angle_rad/2), 0], dtype=np.float32)
        elif axis == 'z':
            rot_quat = np.array([np.cos(angle_rad/2), 0, 0, np.sin(angle_rad/2)], dtype=np.float32)
        else:
            raise ValueError("Axis must be 'x', 'y', or 'z'")

        # Convert current transform to quaternion
        current_rot = current_transform[:3, :3]
        current_quat = gs.utils.geom.R_to_quat(current_rot)
        # Ensure consistent dtype
        current_quat = np.asarray(current_quat, dtype=np.float32)

        # Combine rotations
        new_quat = gs.utils.geom.transform_quat_by_quat(current_quat, rot_quat)
        # Ensure consistent dtype
        new_quat = np.asarray(new_quat, dtype=np.float32)

        # Create new transform
        new_transform = gs.utils.geom.trans_quat_to_T(current_pos, new_quat)

        # Update camera
        self._cam.set_pose(transform=new_transform)
        self._cam.render()

        self.log_spatial_info()
