import genesis as gs

from src.environment.scene import REPLICACAD_DIR


def add_replicacad_obj(scene: gs.Scene, name: str, pos: list, quat: list, scale: int = 1):
    return scene.add_entity(
        gs.morphs.Mesh(
            file=str(REPLICACAD_DIR / "objects" / f"{name}.glb"),
            pos=pos,
            quat=quat,
            scale=scale,
            visualization=True,
            collision=True,
            fixed=False,
            convexify=False,
            decimate=True,
            decompose_nonconvex=False,
        ),
        surface=gs.surfaces.Default(vis_mode="visual"),
    )



# import enum
# from typing import List
# from dataclasses import dataclass




# class ObjDatasets(enum.Enum):
#     ReplicaCAD = enum.auto()
#     PartNet = enum.auto()

# @dataclass
# class ObjInfo:
#     path: str
#     pos: List[float]
#     quat: List[float]  # scalar first ([w, x, y, z])
#     source: ObjDatasets


# def add_objects(scene: gs.Scene, objs: List[ObjInfo]):

# def add_object(scene: gs.Scene, obj: ObjInfo):
#     """
#     Add rigid object with collision physics. Use source to load object correctly
#     ObjInfo fields: path, pos, rot, source
#     """

# def add_replicad_object(scene: gs.Scene, path: str):
#     """
#     Add as rigid object
#     """

# def add_part_net_object(scene: gs.Scene, path: str):
#     """
#     Add as rigid object
#     """