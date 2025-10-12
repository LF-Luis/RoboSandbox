from dataclasses import dataclass
from abc import ABC, abstractmethod

import genesis as gs

from src.environment.scene import add_replicad_scene


@dataclass
class BaseSimSettings(ABC):

    @abstractmethod
    def setup_scene(self, scene: gs.Scene):
        """
        Add background, objects, cameras, etc to a sim scene
        """
        pass

    @abstractmethod
    def scene_reset(self):
        """
        Reset scene objects to starting position
        """
        pass

    @abstractmethod
    def _add_objects(self, scene: gs.Scene):
        """
        Add objects
        """
        pass


class ReplicadBase(BaseSimSettings):

    def setup_scene(self, scene: gs.Scene):
        add_replicad_scene(
            scene=scene,
            scene_config_file=self.scene_config_file,
            keep_as_rigid=self.keep_as_rigid,
            skip_loadding=self.skip_loadding,
        )

        self._add_objects(scene)
