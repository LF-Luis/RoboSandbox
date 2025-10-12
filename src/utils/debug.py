import sys
import inspect
from collections import ChainMap

import torch
import IPython
import numpy as np


"""
from src.utils.debug import enter_interactive; enter_interactive()
"""

def enter_interactive(exit_at_end=False, stack_depth=1):
    """
    Type `exit` to continue from this point in the code.
    Use `stack_depth` to get variables down the stack, from other called functions. Only available when using `exit_at_end` for safety.

    Note in stack_depth a last-wins strategy is used to resolved vars with same name.
    """

    print("=" * 42)
    print("Entering interactive mode.")
    print("-" * 42)
    if exit_at_end:
        print("Type `exit` to exit the simulation.")
    else:
        print("Type `exit` to continue from this point in the code.")

    interactive_namespace = {}
    if exit_at_end:
        print(f"Capturing locals from up to {stack_depth + 1} stack frame(s)...")
        frames = []
        frame = inspect.currentframe()
        for _ in range(stack_depth + 1):  # +1, include current frame
            if frame:
                frames.append(frame)
                frame = frame.f_back
            else:
                break

        # Merge locals from outermost to innermost (last wins)
        locals_list = [f.f_locals.copy() for f in reversed(frames)]
        merged_ns = ChainMap(*locals_list)

        # Filter out d-under variables
        interactive_namespace = {
            k: v for k, v in merged_ns.items() if not k.startswith("__")
        }
        print(f"Injected variables from {len(locals_list)} frame(s).")
    else:
        # Inject only caller's locals only
        caller_frame = inspect.currentframe().f_back
        if caller_frame:
            print("Injecting caller's local vars...")
            caller_locals = caller_frame.f_locals.copy()
            interactive_namespace = caller_locals.copy()
        else:
            print("Not injecting caller's local vars...")

    print("=" * 42)
    IPython.embed(user_ns=interactive_namespace)
    if exit_at_end:
        sys.exit()


def inspect_structure(obj):
    """
    Inspect some APIs output.
    """

    print(f"Type: {type(obj)}")

    try:
        print(f"Length: {len(obj)}")
    except TypeError:
        print("Not iterable")
        return

    if isinstance(obj, np.ndarray):
        print(f"dtype: {obj.dtype}")
        print(f"shape: {obj.shape}")
        if obj.size > 0:
            print(f"element type: {type(obj.flat[0])}")

    elif torch and isinstance(obj, torch.Tensor):
        print(f"dtype: {obj.dtype}")
        print(f"shape: {obj.shape}")
        if obj.numel() > 0:
            print(f"element type: {type(obj.flatten()[0].item())}")

    elif isinstance(obj, list):
        if len(obj) > 0:
            print(f"element type: {type(obj[0])}")
            try:
                print(f"nested type: {type(obj[0][0])}")
            except Exception:
                pass
        else:
            print("empty list")
    else:
        print("unsupported type")
