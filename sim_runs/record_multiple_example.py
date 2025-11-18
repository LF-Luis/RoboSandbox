import genesis as gs

from src.robots.droid import DroidManager
from src.inference.pi0_inference import Pi0Inference
from src.sims.replicad_plus_objs_scenes import get_sim_settings
from src.utils.run_sim_helper import user_input_should_reset, user_input_update_prompt, sim_arg_parser, auto_reset


# NOTE: see src/robots/droid.py -- I disabled a few cam recording because if the recording is long it can eat up a lot of
# CPU mem. Keep recordings short (or stream them) -- enable all cams in src/robots/droid.py if you need them.

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
        rigid_options=gs.options.RigidOptions(
            integrator=gs.integrator.implicitfast,
            constraint_solver=gs.constraint_solver.Newton,
            iterations=200,
            ls_iterations=50,
            tolerance=1e-6,
            contact_resolve_time=0.02
        ),
        sim_options=gs.options.SimOptions(
            dt=ss.dt,  # 0.002,
            substeps=20,
            requires_grad=False,
        ),
        renderer=gs.renderers.Rasterizer()
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
