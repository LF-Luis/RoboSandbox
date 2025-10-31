import genesis as gs

from src.robots.droid import DroidManager
from src.inference.pi0_inference import Pi0Inference
from src.sims.replicad_plus_objs_scenes import get_sim_settings
from src.utils.run_sim_helper import user_input_should_reset, user_input_update_prompt, sim_arg_parser


if __name__ == "__main__":
    args = sim_arg_parser()
    task_prompt, sim_setting = args["task_prompt"], args["sim_run"]

    # Model inference
    pi0 = Pi0Inference()
    # Setup sim
    ss = get_sim_settings(sim_name=sim_setting)
    gs.init(backend=gs.gpu, logging_level="info")
    scene = gs.Scene(
        show_viewer=False,
        show_FPS=False,
        sim_options=gs.options.SimOptions(dt=ss.dt, requires_grad=False),
        renderer=gs.renderers.Rasterizer(),
    )
    ss.setup_scene(scene)
    franka_droid = DroidManager(scene, ss.franka_pos, ss.franka_quat, ss.render_all_steps, rest_pose=ss.rest_pose)
    # Build sim and reset franka arm
    scene.build()
    franka_droid.setup()

    # Run sim loop
    loop = 0
    while True:
        if user_input_should_reset(loop=loop, restart_loop_mod=40):
            task_prompt = user_input_update_prompt(task_prompt)
            print(f"task_prompt: {task_prompt}")
            scene.reset()
            ss.scene_reset()
            franka_droid.goto_start_pos()

        scene_obv = franka_droid.get_scene_observation()
        actions = pi0.forward(droid_observation=scene_obv, prompt=task_prompt, actions=8)
        franka_droid.apply_abs_joint_actions(actions=actions, steps_per_action=ss.steps_per_action)
        loop += 1
