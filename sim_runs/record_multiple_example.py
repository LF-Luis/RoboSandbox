import genesis as gs

from src.robots.droid import DroidManager
from src.inference.pi0_inference import Pi0Inference
from src.sims.replicad_plus_objs_scenes import get_sim_settings
from src.utils.run_sim_helper import user_input_should_reset, user_input_update_prompt, sim_arg_parser, auto_reset


"""
To use renderer=gs.renderers.RayTracer() with the current setup you must fix the
following bug:
/opt/conda/lib/python3.11/site-packages/genesis/vis/raytracer.py
Line 174
        LuisaRenderPy.init(
            ...
            device_index=self.cuda_device,  <--- bug, this is the fix
            ...
        )
"""

if __name__ == "__main__":
    args = sim_arg_parser()
    task_prompt, sim_setting = args["task_prompt"], args["sim_run"]

    # Model inference
    pi0 = Pi0Inference()
    # Setup sim
    ss = get_sim_settings(sim_name=sim_setting)
    gs.init(backend=gs.gpu, logging_level="info")
    scene = gs.Scene(
        show_viewer=False,  # Disable GUI
        show_FPS=False,
        sim_options=gs.options.SimOptions(dt=ss.dt, requires_grad=False),
        renderer=gs.renderers.Rasterizer(),
    )
    ss.setup_scene(scene)
    ss.render_all_steps = True  # Render cams every step so that all frames are recorded
    franka_droid = DroidManager(scene, ss.franka_pos, ss.franka_quat, ss.render_all_steps, enable_left_2_cam=True, rest_pose=ss.rest_pose)
    # Build sim and reset franka arm
    scene.build()
    franka_droid.setup()

    # Run sim loop
    loop = 0
    restart_loop_mod = 40

    franka_droid.cams_start_recording()

    while True:
        if loop > restart_loop_mod*5: break;

        if auto_reset(loop=loop, restart_loop_mod=restart_loop_mod):
            print("Resetting scene!")
            scene.reset()
            ss.scene_reset()
            franka_droid.goto_start_pos()

        scene_obv = franka_droid.get_scene_observation()
        actions = pi0.forward(droid_observation=scene_obv, prompt=task_prompt, actions=8)
        franka_droid.apply_abs_joint_actions(actions=actions, steps_per_action=ss.steps_per_action)
        loop += 1

    franka_droid.cams_end_recording(path="/workspace/RoboSandbox/temp_data/")
