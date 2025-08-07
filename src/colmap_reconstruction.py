import os
import open3d as o3d
import numpy as np
import subprocess
import time
from argh import arg
from pathlib import Path
from filesystem_helper import (
    get_project_root,
    get_image_dir,
    get_output_dir,
    check_if_path_exists,
    get_file_size,
    make_path,
)


# Helper function to run colmap comman
def run_command(args: list[str], description: str) -> bool:
    command_prefix = "colmap"
    print(f"Running: {description}")
    start_time = time.time()
    try:
        process = subprocess.run(
            [command_prefix] + args,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        end_time = time.time()
        print(f"Time taken for {description}: {end_time - start_time:.2f} seconds")
        return True
    except Exception as e:
        print(f"Error in {description}: {e}")
        print(f"Error output: {process.stderr}")
        return False


def visualize_point_cloud(file_path: Path, title: str) -> bool:
    print(f"Visualizing point cloud {title}")

    if not check_if_path_exists(file_path):
        print(f"Point cloud file {file_path} does not exist")
        return False
    try:
        file_size = get_file_size(file_path)
        print(f"File size: {file_size}")
        if file_size == 0:
            print(f"Point cloud file {file_path} is empty")
            return False

        pcd = o3d.io.read_point_cloud(file_path)
        if len(pcd.points) == 0:
            print("WARNING: Point cloud has no points")
            return False

        print(f"Point cloud has {len(pcd.points)} points")
        # Create a visualization window
        vis = o3d.visualization.Visualizer()
        vis.create_window(window_name=title, width=1280, height=720)

        # Add the point cloud to the visualization
        vis.add_geometry(pcd)

        # Set view control and rendering options
        opt = vis.get_render_option()
        opt.point_size = 1.0
        opt.background_color = np.array([0.1, 0.1, 0.1])

        # Update the visualization once
        vis.update_geometry(pcd)
        vis.poll_events()
        vis.update_renderer()

        # Capture a screenshot
        screenshot_path = str(file_path).replace(".ply", "_screenshot.png")
        vis.capture_screen_image(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        # Run the visualization for a few seconds then close
        print("Visualization window opened. Close the window to continue...")
        vis.run()
        vis.destroy_window()

        print(f"Visualization of {title} completed")
        return True
    except Exception as e:
        print(f"Error visualizing point cloud {title}: {e}")
        return False


def run_reconstruction_pipeline_with_colmap(image_dir: Path, output_dir: Path) -> bool:
    database_path = make_path(output_dir, "database.db", create_if_not_exists=False)
    sparse_path = make_path(output_dir, "sparse")
    dense_path = make_path(output_dir, "dense")
    reconstruction_path = make_path(output_dir, "reconstruction")
    if not check_if_path_exists(image_dir):
        print(f"Image directory {image_dir} does not exist")
        return False

    # Step 1: Feature extraction
    if not run_command(
        [
            "feature_extractor",
            "--database_path",
            str(database_path),
            "--image_path",
            str(image_dir),
        ],
        "Feature Extraction",
    ):
        return False

    # Step 2: Matching
    if not run_command(
        ["exhaustive_matcher", "--database_path", str(database_path)],
        "Exhaustive Matching",
    ):
        return False

    # Step 3: Sparse reconstruction (mapping)
    if not run_command(
        [
            "mapper",
            "--database_path",
            str(database_path),
            "--image_path",
            str(image_dir),
            "--output_path",
            str(sparse_path),
        ],
        "Sparse Reconstruction",
    ):
        return False

    # Check if sparse reconstruction was created
    if not check_if_path_exists(sparse_path / "0"):
        print(f"ERROR: Sparse reconstruction folder not found at {sparse_path / '0'}")
        return False

    # Export sparse reconstruction to PLY for visualization
    sparse_ply_path = make_path(
        reconstruction_path, "sparse.ply", create_if_not_exists=False
    )
    if not run_command(
        [
            "model_converter",
            "--input_path",
            str(sparse_path / "0"),
            "--output_path",
            str(sparse_ply_path),
            "--output_type",
            "PLY",
        ],
        "Sparse Model Conversion",
    ):
        return False

    # Step 4: Image undistortion
    if not run_command(
        [
            "image_undistorter",
            "--image_path",
            str(image_dir),
            "--input_path",
            str(sparse_path / "0"),
            "--output_path",
            str(dense_path),
            "--output_type",
            "COLMAP",
            "--max_image_size",
            "2000",
        ],
        "Image Undistortion",
    ):
        return False

    # Step 5: Dense reconstruction
    if not run_command(
        [
            "patch_match_stereo",
            "--workspace_path",
            str(dense_path),
            "--workspace_format",
            "COLMAP",
            "--PatchMatchStereo.geom_consistency",
            "true",
            "--PatchMatchStereo.window_step",
            "2",
        ],
        "Patch Match Stereo",
    ):
        return False

    # Step 6: Stereo fusion
    dense_ply_path = make_path(dense_path, "fused.ply", create_if_not_exists=False)
    if not run_command(
        [
            "stereo_fusion",
            "--workspace_path",
            str(dense_path),
            "--workspace_format",
            "COLMAP",
            "--input_type",
            "geometric",
            "--output_path",
            str(dense_ply_path),
        ],
        "Stereo Fusion",
    ):
        return False

    # Step 7: Meshing (Poisson)
    poisson_ply_path = make_path(
        reconstruction_path, "meshed-poisson.ply", create_if_not_exists=False
    )
    if not run_command(
        [
            "poisson_mesher",
            "--input_path",
            str(dense_ply_path),
            "--output_path",
            str(poisson_ply_path),
        ],
        "Poisson Mesher",
    ):
        return False

    # Step 8: Meshing (Delaunay)
    delaunay_ply_path = make_path(
        reconstruction_path, "meshed-delaunay.ply", create_if_not_exists=False
    )
    if not run_command(
        [
            "delaunay_mesher",
            "--input_path",
            str(dense_path),
            "--output_path",
            str(delaunay_ply_path),
        ],
        "Delaunay Mesher",
    ):
        return False

    print("\n=== COLMAP pipeline completed successfully ===")
    print(f"Results are stored in {reconstruction_path}")

    return True


@arg("-i", "--image_dir", default=get_image_dir(), help="Path to the image directory")
@arg(
    "-o", "--output_dir", default=get_output_dir(), help="Path to the output directory"
)
def main(
    image_dir: Path = get_image_dir(),
    output_dir: Path = get_output_dir(),
    visualize: bool = False,
):
    print(f"Processing images in {image_dir} and saving results to {output_dir}.")
    print(get_project_root())

    # Run colmap feature extraction
    # run_command(["feature_extractor", "--image_path", image_dir, "--output_path", output_dir / "features.txt"])


if __name__ == "__main__":
    main()
