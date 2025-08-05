
import os
import open3d as o3d
import numpy as np
import subprocess
import time
from argh import arg
from pathlib import Path
from filesystem_helper import get_project_root, get_image_dir, get_output_dir

# Helper function to run colmap comman
def run_command(args, description):
    command_prefix = "colmap"
    print(f"Running: {description}")
    start_time = time.time()
    try:
        process = subprocess.run([command_prefix] + args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        end_time = time.time()
        print(f"Time taken for {description}: {end_time - start_time:.2f} seconds")
        return True
    except Exception as e:
        print(f"Error in {description}: {e}")
        print(f"Error output: {process.stderr}")
        return False

def visualize_point_cloud(file_path: Path, title: str):
    pass

def run_reconstruction_pipeline():
    pass

@arg("-i", "--image_dir", default=get_image_dir(), help="Path to the image directory")
@arg("-o", "--output_dir", default=get_output_dir(), help="Path to the output directory")

def main(image_dir=get_image_dir(), output_dir=get_output_dir(), visualize=False):
    print(f"Processing images in {image_dir} and saving results to {output_dir}.")
    print(get_project_root())

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run colmap feature extraction
    # run_command(["feature_extractor", "--image_path", image_dir, "--output_path", output_dir / "features.txt"])

if __name__ == "__main__":
    main()

