import numpy as np
from genesis.utils import geom as gu

from src.utils.root import get_assets_abs_path


MUJOCO_FILE = get_assets_abs_path("panda_wt_robotiq_2f85/panda_wt_2f85.xml")

JOINT_NAMES = ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6", "joint7", "left_driver_joint", "right_driver_joint"]
END_EFFECTOR_NAME = "base"

# REST_POSE source: https://github.com/droid-dataset/droid/blob/main/config/panda/franka_panda.yaml
REST_POSE = [-0.13935425877571106, -0.020481698215007782, -0.05201413854956627, -2.0691256523132324, 0.05058913677930832, 2.0028650760650635, -0.9167874455451965, 0., 0.]
SETUP_STABILITY_STEPS = 150  # Steps to wait for stabilization

# Joint damping source: https://github.com/droid-dataset/droid/blob/main/config/panda/franka_panda.yaml
# Gripper stays as default
JOINT_DAMPING = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 1., 1.]

"""
Original data from: https://github.com/droid-dataset/droid/blob/main/config/panda/franka_hardware.yaml
Not using gravity compensation (`gravity_compensation=1.0`), multiplying PD values by ~x100
(see https://genesis-world.readthedocs.io/en/latest/user_guide/getting_started/control_your_robot.html)
"""
# Once multiplied by 100, gripper will have default values
_POSITIONAL_GAINS = [40., 30., 50., 25., 35., 25., 10., 1., 1.]
_VELOCITY_GAINS = [ 4., 6., 5., 5., 3., 2., 1., .1, .1]
POSITIONAL_GAINS = [x*100 for x in _POSITIONAL_GAINS]
VELOCITY_GAINS = [x*100 for x in _VELOCITY_GAINS]

FORCE_RANGES_LOWER = [-86., -86., -86., -86., -11.5, -11.5, -11.5, -100., -100.]
FORCE_RANGES_UPPER = [86., 86., 86., 86., 11.5, 11.5, 11.5, 100., 100.]

# Cam config values
# https://www.stereolabs.com/store/products/zed-mini
CAM_RES = (1280, 720)  # Zed mini at 60 fps (this is for the wrist cam, using for scene cam as well for now)
CAM_FOV = 57.  # Vertical FOV for Zed mini: 57 degrees

EXT_CAM_1_LEFT_OFFSET_T = gu.trans_quat_to_T(
    # https://github.com/arhanjain/sim-evals/blob/main/src/environments/droid_environment.py#L53
    trans=np.array([0.05, 0.57, 0.66]),
    quat=np.array([-0.393, -0.195, 0.399, 0.805])  # (w,x,y,z)
)
EXT_CAM_2_LEFT_OFFSET_T = gu.trans_quat_to_T(  # Mirror opposite of EXT_CAM_1_LEFT_OFFSET_T
    trans=np.array([0.05, -0.57, 0.66]),
    quat=np.array([0.805, 0.399, -0.195, -0.393])
)

# Manually tuned values for pos_offset and rot_offset of wrist camera w.r.t. EEF
WRIST_CAM_OFFSET_T = gu.trans_quat_to_T(
    trans=np.array([0.03026469, 0.07047331, 0.02246456]),
    quat=np.array([-0.000662797508,  0.000376455792,  0.988124130,  0.153655398])  # (w,x,y,z)
)
