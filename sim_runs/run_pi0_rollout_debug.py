import genesis as gs

from src.robots.droid import DroidManager
from src.inference.pi0_inference import Pi0Inference
from src.sims.replicad_plus_objs_scenes import get_sim_settings
from src.utils.debug import enter_interactive, inspect_structure
from src.utils.run_sim_helper import user_input_should_reset, user_input_update_prompt, sim_arg_parser


RUN_VLA = True  # False

if __name__ == "__main__":
    args = sim_arg_parser()
    task_prompt, sim_setting = args["task_prompt"], args["sim_run"]

    if RUN_VLA:
        # Model inference
        pi0 = Pi0Inference()
    # Setup sim
    ss = get_sim_settings(sim_name=sim_setting)
    gs.init(backend=gs.gpu, logging_level="info")
    scene = gs.Scene(
        show_viewer=True,  # Show viewer to help debug
        show_FPS=False,
        sim_options=gs.options.SimOptions(dt=ss.dt, requires_grad=False),
    )
    ss.setup_scene(scene)
    ss.render_all_steps = True  # Render cams every step to help debug
    franka_droid = DroidManager(scene, ss.franka_pos, ss.franka_quat, ss.render_all_steps, rest_pose=ss.rest_pose)
    # Build sim and reset franka arm
    scene.build()
    franka_droid.setup()

    """
    Make sure setup is correct. Type `exit` to continue.
    E.g. get pos/rot of an object:
        ss._mouse.get_pos()
        ss._mouse.get_quat()
    Or set it:
        ss._mouse.set_pos([0.8, -2.45, 0.97])
        ss._mouse.set_quat([1/sqrt(2), 0, 0, -1/sqrt(2)])  # rotate -90 degrees about z-axis
    move the scene a few steps to see how objects resolve:
        franka_droid.steps()  # it will also call scene.step() under the hood
    """
    enter_interactive()

    # Run sim loop
    loop = 0
    while True:
        if user_input_should_reset(loop=loop, restart_loop_mod=10):
            task_prompt = user_input_update_prompt(task_prompt)
            scene.reset()
            ss.scene_reset()
            franka_droid.goto_start_pos()
            # Check between runs
            enter_interactive()

        scene_obv = franka_droid.get_scene_observation()
        if RUN_VLA:
            actions = pi0.forward(droid_observation=scene_obv, prompt=task_prompt, actions=8)
            # Verify model output
            # inspect_structure(actions); enter_interactive()
            franka_droid.apply_abs_joint_actions(actions=actions, steps_per_action=ss.steps_per_action)
        loop += 1
