import argparse


def sim_arg_parser():
    """Lightweight argument parser for sim runs"""
    parser = argparse.ArgumentParser(description="Run sim with specified settings")
    parser.add_argument("--sim_run", required=True, help="Sim setting, see src/sims/replicad_plus_objs_scenes.py")
    parser.add_argument("--prompt", default="", help="VLA prompt")
    args = parser.parse_args()
    return {
        "sim_run": args.sim_run,
        "task_prompt": args.prompt,
    }


def user_input_should_reset(loop: int, restart_loop_mod: int):
    if loop > 0 and loop % restart_loop_mod == 0:
        user_input = input("Reset and restart sim? (Y/N): ").strip().upper()
        if user_input == "Y":
            print("Will restart sim.")
            return True
        else:
            print("Will continue sim.")
    return False


def user_input_update_prompt(prompt: str):
    user_input = input("Type new prompt (or just press RETURN to not update prompt): ").strip()
    if user_input:
        return user_input
    return prompt


def auto_reset(loop: int, restart_loop_mod: int, max_loops: int = None):
    if max_loops and loop > max_loops:
        import sys; sys.exit()
    if loop > 0 and loop % restart_loop_mod == 0:
        return True
    return False
