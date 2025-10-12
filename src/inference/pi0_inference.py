import numpy as np

from openpi_client import image_tools
from openpi_client.websocket_client_policy import WebsocketClientPolicy


class Pi0Inference:

    def __init__(self):
        self._pi0_model_client = WebsocketClientPolicy(host="localhost", port=8000)

    def forward(self, droid_observation: dict, prompt:str, actions: int = 10):
        """
        For simplicity, droid_observation should be of the following form, as seen
        in the output of src/robots/droid.py get_scene_observation(..)
            droid_observation {
                "joint_positions": joint_positions,
                "gripper_position": gripper_position,
                "wrist_cam_img": wrist_cam_img,
                "ext_camera_img": ext_camera_img,
            }
        """

        # Get scene "observation" data for Pi0 model (joint pos and cam images)
        joint_positions = droid_observation["joint_positions"]
        gripper_position = droid_observation["gripper_position"]
        wrist_cam_img = droid_observation["wrist_cam_img"]
        ext_camera_img = droid_observation["ext_camera_img"]

        joint_positions = joint_positions.cpu().numpy()
        gripper_position = gripper_position.cpu().numpy()

        """
        See src/data_inpection/droid_data.py
        'observation': FeaturesDict({
            'cartesian_position': Tensor(shape=(6,), dtype=float64),
            'exterior_image_1_left': Image(shape=(180, 320, 3), dtype=uint8),
            'exterior_image_2_left': Image(shape=(180, 320, 3), dtype=uint8),
            'gripper_position': Tensor(shape=(1,), dtype=float64),
            'joint_position': Tensor(shape=(7,), dtype=float64),
            'wrist_image_left': Image(shape=(180, 320, 3), dtype=uint8),
        }),
        """
        # Resize images on the client side to minimize bandwidth, latency, and match training routines.
        # Resizing it to 224x224 (as seen in openpi repo)
        ext_camera_img = image_tools.resize_with_pad(ext_camera_img, 224, 224)
        wrist_cam_img = image_tools.resize_with_pad(wrist_cam_img, 224, 224)

        gripper = gripper_position[0]
        gripper_norm = np.clip(gripper / (np.pi/4), 0.0, 1.0)
        gripper_norm = np.array([gripper_norm], dtype=np.float32)
        # print(f"gripper_position: {gripper_position}, gripper_norm: {gripper_norm}")  # Must end up between 0 and 1

        observation = {
            "observation/exterior_image_1_left": ext_camera_img,
            "observation/wrist_image_left": wrist_cam_img,
            "observation/joint_position": joint_positions,
            "observation/gripper_position": gripper_norm,  # must be a single number since it applies to both gripper fingers
            "prompt": prompt,
        }

        """
        At every inference call, π0 outputs a 10x8 chunk. That is 10 actions, with each action having 8
        values that correspond to the 8 joints+gripper in the Franka robot (7 rotary joints, 1 gripper action).
        Note that Franka defined in droid.py has 9 joints+gripper states (7 rotary joints, 2 gripper action). The 1 gripper
        action from π0 is applied to both gripper fingers.

        In the π0 paper, Franka runs at 20Hz with a 16 step horizon (π0 paper, APPENDIX D. Inference). Here I'll
        use 15-20Hz, with a 8-10 step horizon per chunk.
        # TODO: Record the tracking error (q_desired - q_actual).
        """
        try:
            # print(f"Running inference...")
            model_response = self._pi0_model_client.infer(observation)
            return model_response["actions"][:actions]  # Shape: (10, 8), numpy.float64
        except Exception:
            print("Failed to run Pi0 model inference")
            raise
