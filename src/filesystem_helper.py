from pathlib import Path
from glob import glob
import os


def get_project_root():
    return Path(__file__).parent.parent


def get_image_dir():
    return get_project_root() / "data" / "images"


def get_output_dir():
    return get_project_root() / "results"


def check_if_path_exists(path):
    return os.path.exists(path)


def get_file_size(path):
    return os.path.getsize(path)


def make_path(root: Path, *args: str, create_if_not_exists: bool = True) -> Path:
    path = root / Path(*args)
    # check if path exists if not create it
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path
