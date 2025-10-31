import os, json
from pathlib import Path

import genesis as gs

from src.utils.root import get_temp_data_abs_path
from src.utils.geom import habitat_to_genesis_transform


REPLICACAD_DIR: Path = get_temp_data_abs_path("haosulab-ReplicaCAD")


def open_read_json(file: str) -> dict:
    with open(file=file, mode='r',) as f:
        return json.load(f)

def get_replicacad_scene_config(scene_name: str) -> Path:
    scene_config_path = REPLICACAD_DIR / "configs" / "scenes" / f"{scene_name}.scene_instance.json"
    return get_temp_data_abs_path(scene_config_path)

def determine_urdf_path(name: str) -> Path:
    """Determine URDF file path for articulated object by its template name."""
    urdf_base = REPLICACAD_DIR / "urdf"
    return urdf_base / name / f"{name}.urdf"

def add_replicad_scene(
    scene: gs.Scene,
    scene_config_file: str,
    keep_as_rigid: set[str],
    skip_loading: set[str],
    load_articulated: bool = False,
    keep_articulated: set[str] = {},
):
    """
    keep_as_rigid: object names from ReplicaCAD scene to keep as rigid objects. Everything has no collision physics, is just for visual input
    """

    with open(scene_config_file, 'r') as f:
        scene_data = json.load(f)

    ###############################################################
    # Load static stage as visual mesh only (walls, floor mainly) #
    ###############################################################

    # e.g. "stages/frl_apartment_stage" -> "frl_apartment_stage"
    stage_name = Path(scene_data["stage_instance"]["template_name"]).name
    stage_cfg = open_read_json(REPLICACAD_DIR / "configs" / "stages" / f"{stage_name}.stage_config.json")
    # Add stage visual (Y-up -> Z-up: apply 90° X rotation)
    scene.add_entity(
        gs.morphs.Mesh(
            file=str(REPLICACAD_DIR / "stages" / Path(stage_cfg["render_asset"]).name),
            pos=(0,0,0),
            euler=(90,0,0),
            visualization=True,
            collision=False,
            fixed=True,
            decimate=False,
            convexify=False,
        ),
        surface=gs.surfaces.Default(vis_mode="visual"),
    )

    ###########################################
    # Load object instances (furniture, etc.) #
    ###########################################

    object_instances = scene_data.get("object_instances")
    objs_len = len(object_instances)

    for i, obj in enumerate(object_instances):
        # e.g. "objects/frl_apartment_table" -> "frl_apartment_table"
        obj_name = Path(obj["template_name"]).name
        print(f"Processing object {i+1}/{objs_len}, {obj_name}")
        if obj_name in skip_loading:
            print(f"Skip loading object: {obj_name}.")
            continue

        obj_cfg = open_read_json(REPLICACAD_DIR / "configs" / "objects" / f"{obj_name}.object_config.json")

        # Note: Not using "collision_asset" since those are already decomposed meshes and Genesis
        # will load them as individual meshes and then decompose each. Best to load the entire "render_asset"
        # mesh and have Genesis decompose that.
        vis_asset = REPLICACAD_DIR / "objects" / Path(obj_cfg["render_asset"]).name
        pos_gen, quat_gen = habitat_to_genesis_transform(obj.get("translation"), obj.get("rotation"))

        if obj_name in keep_as_rigid:
            print(f"Adding object: {obj_name} with collision.")
            scene.add_entity(
                gs.morphs.Mesh(
                    file=str(vis_asset),
                    pos=pos_gen,
                    quat=quat_gen,
                    visualization=True,
                    collision=True,
                    fixed=True,
                    convexify=False,  # Don't convert to convex-hull, try to keep original shape as much as possible (and most objects in scene have some concavity)
                    decimate=True,    # Simplify mesh for collision
                    decompose_nonconvex=False,
                ),
                surface=gs.surfaces.Default(vis_mode="visual"),  # debug with `vis_mode="collision"`
            )
        else:
            scene.add_entity(
                gs.morphs.Mesh(
                    file=str(vis_asset),
                    pos=pos_gen,
                    quat=quat_gen,
                    visualization=True,
                    collision=False,
                    fixed=True,
                    decimate=False,
                    convexify=False
                ),
                surface=gs.surfaces.Default(vis_mode="visual"),
            )

    if load_articulated == False:
        return

    #########################################################
    # Load articulated objects (doors, cabinets with URDFs) #
    #########################################################

    for art in scene_data.get("articulated_object_instances", []):
        name = art["template_name"]  # e.g. "fridge", "door2", "kitchenCupboard_01", ...
        urdf_path = determine_urdf_path(name)
        pos_hab = art.get("translation")
        rot_hab = art.get("rotation")
        pos_gen, quat_gen = habitat_to_genesis_transform(pos_hab, rot_hab)
        scale = 1

        # Need to hardcode scale for some URDFs that ReplicaCAD didn't give the scale to:
        if name == "kitchenCupboard_01":
            scale = 0.4

        if name in keep_articulated:
            scene.add_entity(
                gs.morphs.URDF(
                    file=str(urdf_path),
                    pos=pos_gen,
                    quat=quat_gen,
                    scale=scale,
                    # fixed=art.get("fixed_base"),
                    visualization=True,
                    collision=True,
                    fixed=True,
                    convexify=False,
                    # decimate=True,  # Need newer version of Genesis
                    # decompose_nonconvex=False,
                ),
                material=gs.materials.Rigid(friction=0.5, coup_restitution=0.0),
                surface=gs.surfaces.Default(vis_mode="visual")
            )
        else:
            scene.add_entity(
                gs.morphs.URDF(
                    file=str(urdf_path),
                    pos=pos_gen,
                    quat=quat_gen,
                    scale=scale,
                    fixed=art.get("fixed_base"),
                    collision=False,
                ),
                material=gs.materials.Rigid(friction=0.5, coup_restitution=0.0),
                surface=gs.surfaces.Default(vis_mode="visual")
            )
