import numpy as np
import genesis as gs
from datetime import datetime

from src.robots.droid_const import (
    JOINT_DAMPING,  POSITIONAL_GAINS,  VELOCITY_GAINS,  FORCE_RANGES_LOWER, FORCE_RANGES_UPPER,
    CAM_RES, CAM_FOV, MUJOCO_FILE, EXT_CAM_1_LEFT_OFFSET_T, WRIST_CAM_OFFSET_T, REST_POSE,
    SETUP_STABILITY_STEPS, JOINT_NAMES, END_EFFECTOR_NAME,
)


"""
DROID setup in Genesis sim.

This setup attempts to match as closely as possible the DROID setup in sim. It tries to match camera placement,
starting position, joint configs, etc. It does not attempt to match any of the DROID-dataset scenes though.

- DROID dataset: https://droid-dataset.github.io/droid/the-droid-dataset
- DROID HW setup: https://droid-dataset.github.io/droid/docs/hardware-setup
    - More info: https://huggingface.co/KarlP/droid
    - More info documented in src/robots/droid_const.py
"""

class DroidManager:
    """
    One-off class to manage the DROID setup in sim.
    """

    def __init__(self, scene: gs.Scene, base_pos: list, base_quat: list, render_all_steps: bool):
        self._scene = scene
        self._render_all_steps = render_all_steps
        self._franka = self._scene.add_entity(
            gs.morphs.MJCF(file=str(MUJOCO_FILE), pos=base_pos, quat=base_quat),
            material=gs.materials.Rigid(
                coup_restitution=0.0,  # No bouncing during coupling
            ),
            surface=gs.surfaces.Default(vis_mode="visual"),
        )
        self._end_effector = self._franka.get_link(name=END_EFFECTOR_NAME)
        self._dofs_idx = [self._franka.get_joint(name).dof_idx_local for name in JOINT_NAMES]
        self._create_cams()

    def _create_cams(self):
        def _pinhole_cam():
            # pos/lookat will be reset after GS Scene build
            return self._scene.add_camera(pos=[0, 0, 0], lookat=[0, 0, 0], res=CAM_RES, fov=CAM_FOV, GUI=True)
        self._wrist_camera = _pinhole_cam()
        self._ext_cam_1_left = _pinhole_cam()

    def _set_control_params(self):
        self._franka.set_dofs_kv(VELOCITY_GAINS, self._dofs_idx)
        self._franka.set_dofs_kp(POSITIONAL_GAINS, self._dofs_idx)
        self._franka.set_dofs_damping(damping=JOINT_DAMPING, dofs_idx_local=self._dofs_idx)
        self._franka.set_dofs_force_range(FORCE_RANGES_LOWER, FORCE_RANGES_UPPER, self._dofs_idx)

    def goto_start_pos(self):
        # Teleport to starting position
        self._franka.set_dofs_position(REST_POSE, self._dofs_idx)
        # Solve for starting position
        self._franka.control_dofs_position(REST_POSE, self._dofs_idx)
        # Wait for stabilization
        print(f"Running {SETUP_STABILITY_STEPS} steps to stabilize at home position.")
        # for _ in range(SETUP_STABILITY_STEPS):
        #     self._scene.step()
        # self.steps(n=1)  # Perform setup once
        self.steps(n=SETUP_STABILITY_STEPS)
        print(f"Done waiting for stabilization.")

    def setup(self):
        """
        After GS Scene has build, setup arm + cameras tp their desired state.
        """
        # Place cameras in scene
        self._wrist_camera.attach(rigid_link=self._end_effector, offset_T=WRIST_CAM_OFFSET_T)
        self._ext_cam_1_left.attach(rigid_link=self._franka.base_link, offset_T=EXT_CAM_1_LEFT_OFFSET_T)
        # Setup manipulator+EEF control params
        self._set_control_params()
        # Solve for starting position
        self.goto_start_pos()

    def get_scene_observation(self):
        """
        Get DROID state, mainly joint pos and camera data
        """
        # Make sure wrist cam is on gripper, facing correctly
        self._wrist_camera.move_to_attach()
        # Get the current joint and gripper revolute angles in radians
        dofs_positions = self._franka.get_dofs_position(dofs_idx_local=self._dofs_idx)  # 9 joints, held in CUDA Tensor
        joint_positions = dofs_positions[:7]  # First 7 DOFs are the arm joints
        gripper_position = dofs_positions[7:]  # 8th and 9th DOF is the gripper joints
        # Get cam images
        wrist_cam_img = self._wrist_camera.render()[0]  # 0th is the rgb_arr, numpy.ndarray, uint8, Shape: (720, 1280, 3)
        ext_camera_img = self._ext_cam_1_left.render()[0]

        return {
            "joint_positions": joint_positions,
            "gripper_position": gripper_position,
            "wrist_cam_img": wrist_cam_img,
            "ext_camera_img": ext_camera_img,
        }

    def steps(self, n: int = 1):
        """
        Helper, run through multiple sim steps
        Skip computing cam location and graphics during movement to run sim faster.
        """
        for _ in range(n):
            self._scene.step()
            if self._render_all_steps:
                self._wrist_camera.move_to_attach()
                _ = self._wrist_camera.render()
                _ = self._ext_cam_1_left.render()

    def apply_abs_joint_actions(self, actions: np.ndarray, steps_per_action: int):
        # Absolute joint pos approach
        for i, action in enumerate(actions):
            arm_targets = action[:7]    # desired joint positions (radians)
            gripper_cmd = action[7]     # this will be 0.0 or 1.0 from model output
            # print(f"LF_DEBUG: model out, gripper_cmd: {gripper_cmd}")
            # if gripper_cmd > 0.5:
            if gripper_cmd > 0.2:
                gripper_target = np.pi / 4  # ~45° in radians, closed
            else:
                gripper_target = 0.0       # open
            franka_act = np.hstack([arm_targets, [gripper_target], [gripper_target]])
            self._franka.control_dofs_position(franka_act, self._dofs_idx)
            self.steps(steps_per_action)

    def cams_start_recording(self):
        self._wrist_camera.start_recording()
        self._ext_cam_1_left.start_recording()

    def cams_end_recording(self, path: str):
        time_stamp = datetime.now().strftime("%m-%d-%y_%H-%M")
        self._wrist_camera.stop_recording(
            save_to_filename=f"{path}/wrist_{time_stamp}.mp4"
        )
        self._ext_cam_1_left.stop_recording(
            save_to_filename=f"{path}/scene_{time_stamp}.mp4"
        )
