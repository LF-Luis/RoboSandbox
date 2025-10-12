import os
from pathlib import Path


def get_root_abs_path() -> Path:
    """
    Get absolute path of root directory of the project.
    Note this file must be in /<project_root>/src/utils/root.py
    """
    current_dir = Path(__file__).resolve().parent
    return current_dir.parent.parent

def _get_abs_path(*subpaths: str, check_exists: bool = True) -> Path:
    """
    Return the absolute path to subpath, which is expected to be under the root of this project.
    Works for files or dirs.
    """
    clean_subpaths = tuple(p for p in subpaths if p is not None)
    path = get_root_abs_path().joinpath(*clean_subpaths)
    if check_exists and not path.exists():
        raise FileNotFoundError(f"File/dir does not exist: {path}")
    return path

def get_assets_abs_path(subpath: str = None, check_exists: bool = True) -> Path:
    return _get_abs_path("assets", subpath, check_exists=check_exists)

def get_temp_data_abs_path(subpath: str = None, check_exists: bool = True) -> Path:
    return _get_abs_path("temp_data", subpath, check_exists=check_exists)


if __name__ == '__main__':
    print(f"get_root_abs_path(): {get_root_abs_path()}")
    print(f"get_assets_abs_path(): {get_assets_abs_path()}")
    print(f"get_temp_data_abs_path(): {get_temp_data_abs_path()}")
    print(get_assets_abs_path("panda_wt_robotiq_2f85/panda_wt_2f85.xml"))
