
'''
test_setup.py
This file is used to setup the test environment. Making sure the libraries are installed properly.
It also generates a random point cloud with a random number of shapes.
The point cloud is then visualized using Open3D.
'''

import numpy as np
import open3d as o3d


def generate_random_point_cloud(num_points=1000, num_shapes = 1):
    points = []
    for _ in range(num_shapes):
        shape_type = np.random.choice(['sphere', 'cylinder', 'plane', 'cube'])
        shape_points = num_points // num_shapes
        shape_center = np.random.uniform(-5, 5, 3)

        if shape_type == 'sphere':
            radius = np.random.uniform(0.1, 0.5)
            theta = np.random.uniform(0, 2 * np.pi, shape_points)
            phi = np.random.uniform(0, np.pi, shape_points)
            x = radius * np.sin(phi) * np.cos(theta)
            y = radius * np.sin(phi) * np.sin(theta)
            z = radius * np.cos(phi)
            points.extend(np.column_stack([x, y, z]))

        elif shape_type == 'cylinder':
            radius = np.random.uniform(0.1, 0.5)
            height = np.random.uniform(0.5, 2.0)
            theta = np.random.uniform(0, 2 * np.pi, shape_points)
            z = np.random.uniform(0, height, shape_points)
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            points.extend(np.column_stack([x, y, z]) + shape_center)

        elif shape_type == 'plane':
            size = np.random.uniform(1.0, 3.0)
            x = np.random.uniform(-size/2, size/2, shape_points)
            y = np.random.uniform(-size/2, size/2, shape_points)
            z = np.zeros(shape_points)
            points.extend(np.column_stack([x, y, z]) + shape_center)

        elif shape_type == 'cube':
            size = np.random.uniform(0.5, 2.0)
            x = np.random.uniform(-size/2, size/2, shape_points)
            y = np.random.uniform(-size/2, size/2, shape_points)
            z = np.random.uniform(-size/2, size/2, shape_points)
            points.extend(np.column_stack([x, y, z]) + shape_center)

    return np.array(points)

point_cloud = generate_random_point_cloud(num_points=1000, num_shapes=3)

# Create a point cloud object and visualize it
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(point_cloud)
o3d.visualization.draw_geometries([pcd])