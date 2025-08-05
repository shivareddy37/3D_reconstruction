from pathlib import Path
from glob import glob


def get_project_root():
    return Path(__file__).parent.parent

def get_image_dir():
    return get_project_root() / "data" / "images"

def get_output_dir():
    return get_project_root() / "results"

