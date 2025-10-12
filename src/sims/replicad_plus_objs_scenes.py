from doctest import debug
from math import sqrt

import numpy as np
import genesis as gs

from src.sims.base import BaseSimSettings, ReplicadBase
from src.environment.rigid_objs import add_replicacad_obj
from src.environment.scene import get_replicacad_scene_config
from src.utils.root import get_assets_abs_path, get_temp_data_abs_path


def get_sim_settings(sim_name: str) -> BaseSimSettings:
    available_scenes = {
        "replicad_apt0_plus_objs": ReplicadApt0PlusObjs,
        "replicad_apt0_partnet_desk_objs": ReplicadApt0PartNetDeskObjs,
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
    # """
    # # Sim info
    # Freq = 15Hz = 1/15 secs/action
    # DT = 0.002 secs/step
    # STEPS_PER_ACTION = Freq / DT = 33.333 steps/actions = 33 steps/actions
    # """
    # dt=0.002  # time per sim-step
    # steps_per_action = 33  # Number of sim-steps to take per control-action cmd
    render_all_steps = False  # Whether to render cameras at all sim steps

    # Scene info
    scene_config_file = get_replicacad_scene_config("apt_0")
    keep_as_rigid = {"frl_apartment_table_02"}
    skip_loadding = {"frl_apartment_lamp_02"}  # We're using the table that has lamps, so get the lamps out of the way
    franka_pos = [0.7, -2.9, 0.9]
    franka_quat = [np.cos(np.pi/8), 0., 0., np.sin(np.pi/8)]

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


class ReplicadApt0PartNetDeskObjs(ReplicadApt0PlusObjs):
    # Sim objects
    _mouse = None
    _stapler = None
    def _add_objects(self, scene: gs.Scene):
        self._mouse = scene.add_entity(
            material=gs.materials.Rigid(rho=300),
            morph=gs.morphs.URDF(
                file=str(get_temp_data_abs_path("PartNet-Mobility/103025/mobility.urdf")),
                scale=0.065,
                pos=[0.8, -2.45, 0.97],
                quat=[1/sqrt(2), 0, 0, -1/sqrt(2)],
            ),
        )
        self._stapler = scene.add_entity(
            material=gs.materials.Rigid(rho=300),
            morph=gs.morphs.URDF(
                file=str(get_temp_data_abs_path("PartNet-Mobility/103280/mobility.urdf")),
                scale=0.09,
                pos=[0.8, -2.2, 0.97],
                quat=[1/sqrt(2), 0, 0, -1/sqrt(2)],
            ),
        )

    def scene_reset(self):
        self._mouse.set_pos([0.8, -2.45, 0.97])
        self._mouse.set_quat([1/sqrt(2), 0, 0, -1/sqrt(2)])
        self._stapler.set_pos([0.8, -2.2, 0.97])
        self._stapler.set_quat([1/sqrt(2), 0, 0, -1/sqrt(2)])

