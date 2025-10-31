from doctest import debug
from math import sqrt

import numpy as np
import genesis as gs

from src.robots.droid_const import REST_POSE
from src.sims.base import BaseSimSettings, ReplicadBase
from src.environment.rigid_objs import add_replicacad_obj
from src.environment.scene import get_replicacad_scene_config
from src.utils.root import get_assets_abs_path, get_temp_data_abs_path


def get_sim_settings(sim_name: str) -> BaseSimSettings:
    available_scenes = {
        "replicad_apt0_plus_objs": ReplicadApt0PlusObjs,
        "replicad_apt5_kitchen": ReplicadApt5Kitchen,
        "replicad_apt4_google_scan_objs": ReplicadApt4_GoogleScanObjs,
    }
    if sim_name not in available_scenes:
        raise ValueError(f"Unknown scene setup: {sim_name}. Available scenes: {list(available_scenes.keys())}")
    return available_scenes[sim_name]()


class ReplicadApt0PlusObjs(ReplicadBase):
    """
    # Sim info
    Freq = 15Hz = 1/15 secs/action
    DT = 0.01 secs/step
    STEPS_PER_ACTION = Freq / DT = 6.6777 steps/actions = 7 steps/actions
    """
    dt = 0.01  # time per sim-step
    steps_per_action = 7  # Number of sim-steps to take per control-action cmd
    render_all_steps = False  # Whether to render cameras at all sim steps

    # Scene info
    scene_config_file = get_replicacad_scene_config("apt_0")
    keep_as_rigid = {"frl_apartment_table_02"}
    skip_loading = {"frl_apartment_lamp_02"}  # We're using the table that has lamps, so get the lamps out of the way
    franka_pos = [0.7, -2.9, 0.9]
    franka_quat = [np.cos(np.pi/8), 0., 0., np.sin(np.pi/8)]
    rest_pose = REST_POSE
    load_articulated = False

    # Sim objects
    _bottle = None
    _replica_bowl = None
    def _add_objects(self, scene: gs.Scene):
        self._bottle = scene.add_entity(
            material=gs.materials.Rigid(rho=300),
            morph=gs.morphs.URDF(
                file=str(get_assets_abs_path("3763/mobility_vhacd_fixed.urdf")),
                scale=0.09,
                pos=[0.95, -2.55, 0.95],
                quat=[1/sqrt(2), 0, 1/sqrt(2), 0],
            ),
        )
        self._replica_bowl = add_replicacad_obj(scene, "frl_apartment_bowl_07", [0.6, -2.3,  1], [0.7071, 0.7071, 0, 0])

    def scene_reset(self):
        self._bottle.set_pos([0.95, -2.55, 0.95])
        self._bottle.set_quat([1/sqrt(2), 0, 1/sqrt(2), 0])
        self._replica_bowl.set_pos([0.6, -2.3,  1])
        self._replica_bowl.set_quat([0.7071, 0.7071, 0, 0])


class ReplicadApt4_GoogleScanObjs(ReplicadBase):
    dt = 0.01
    steps_per_action = 7
    render_all_steps = False
    load_articulated = False
    scene_config_file = get_replicacad_scene_config("apt_4")
    franka_pos = [2.75, -5.1, 0.4]
    franka_quat = [0, 0, 0, 1]
    rest_pose = [0, -0.4, 0, -1.8, 0, 1.4, 0, 0., 0.]
    # keep_as_rigid = {"frl_apartment_table_03"}
    keep_as_rigid = {}
    skip_loading = {}
    _table_plane = None
    _g_chicken_racer_toy = None  # Google Scan Dataset object
    _g_basket = None             # Google Scan Dataset object
    _g_helicopter = None         # Google Scan Dataset object
    _g_fire_truck = None         # Google Scan Dataset object

    def _add_mjcf_obj(self, file, scene, pos, quat=[1, 0, 0, 0]):
        return scene.add_entity(
            gs.morphs.MJCF(
                file=file, pos=pos, quat=quat, visualization=True,
                collision=True, convexify=False,
            ),
            material=gs.materials.Rigid(),
            surface=gs.surfaces.Default(vis_mode="visual"),
        )

    def _add_objects(self, scene: gs.Scene):
        # FIXME: figure out why this specific table "frl_apartment_table_03" has odd collision
        # properties with partial obj passthrough
        self._table_plane = scene.add_entity(
            morph=gs.morphs.Box(
                pos=[2.27, -5.33, 0.363], size=[0.7, 1.2, 0.1],
                fixed=True, collision=True, visualization=False,
            ),
        )
        self._g_chicken_racer_toy = self._add_mjcf_obj(
            file="/workspace/RoboSandbox/assets/CHICKEN_RACER/model.xml", scene=scene, pos=[2.3, -5.4, 0.42],
        )
        self._g_basket = self._add_mjcf_obj(
            file="/workspace/RoboSandbox/assets/Target_Basket_Medium/model.xml", scene=scene, pos=[2.3, -4.95, 0.52],
        )
        self._g_helicopter = self._add_mjcf_obj(
            file="/workspace/RoboSandbox/assets/HELICOPTER/model.xml", scene=scene, pos=[2.375, -5.225, 0.41], quat=[0.7071, 0, 0, 0.7071],
        )
        self._g_fire_truck = self._add_mjcf_obj(
            file="/workspace/RoboSandbox/assets/FIRE_TRUCK/model.xml", scene=scene, pos=[2.15, -5.2, 0.41],
        )

    def scene_reset(self):
        self._g_chicken_racer_toy.set_pos([2.3, -5.25, 0.45])
        self._g_chicken_racer_toy.set_quat([1, 0, 0, 0])
        self._g_basket.set_pos([2.3, -4.95, 0.42])
        self._g_basket.set_quat([1, 0, 0, 0])
        self._g_helicopter.set_pos([2.375, -5.225, 0.41])
        self._g_helicopter.set_quat([0.7071, 0, 0, 0.7071])
        self._g_fire_truck.set_pos([2.15, -5.2, 0.41])
        self._g_fire_truck.set_quat([1, 0, 0, 0])


class ReplicadApt5Kitchen(ReplicadBase):
    dt = 0.01
    steps_per_action = 7
    render_all_steps = False
    franka_pos = [-1.3, -2.5, 0.9]
    franka_quat = [0, 0, 0, -1]
    rest_pose = REST_POSE
    keep_articulated = {"fridge"}
    load_articulated = True
    scene_config_file = get_replicacad_scene_config("apt_5")
    def _add_objects(self, scene: gs.Scene): pass
    def scene_reset(self): pass
