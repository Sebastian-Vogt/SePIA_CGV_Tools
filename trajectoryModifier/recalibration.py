import numpy as np
import math
import progressbar
from scipy.spatial.transform import Rotation as R
import json


def uv2xyz(u, v):
    uv = np.array([[u], [v]])
    uv = np.subtract(uv, distortion_center)
    uv = np.dot(inv_stretch_matrix, uv)
    rho = math.sqrt(uv[0][0] ** 2 + uv[1][0] ** 2)
    matlab_xyz = np.array([[uv[0][0]],
                           [uv[1][0]],
                           [polynomial_coefficients[0] + polynomial_coefficients[1] * (rho ** 2) + polynomial_coefficients[2] * (rho ** 3) + polynomial_coefficients[3] * (rho ** 4)]])
    camera_xyz = matlab_xyz / np.linalg.norm(matlab_xyz)
    return camera_xyz


def calculate_optimal_parameter_set(ego_trajectory, path, image_points, relative_world_points, weights=None):
    global polynomial_coefficients, distortion_center, inv_stretch_matrix

    if not "camera" in ego_trajectory:
        print("No camera parameter provided.")
        return

    distortion_center = ego_trajectory["camera"]["distortion_center"]
    distortion_center = [[x] for x in distortion_center]
    polynomial_coefficients = ego_trajectory["camera"]["polynomial_coefficients"]
    inv_stretch_matrix = np.linalg.inv(np.array(ego_trajectory["camera"]["stretch_matrix"]))

    widgets = [
        'Optimization: ', progressbar.SimpleProgress(),
        ' ', progressbar.Percentage(),
        ' ', progressbar.Bar(marker=progressbar.AnimatedMarker(fill='#')),
        ' ', progressbar.AdaptiveETA(),
        ' ', progressbar.AdaptiveTransferSpeed(unit="trials"),
    ]
    bar = progressbar.ProgressBar(widgets=widgets, max_value=1000, redirect_stdout=True).start()

    camera_rays = [np.array(uv2xyz(image_point[0], image_point[1])).flatten() for image_point in image_points]

    tests = []
    if "height" in ego_trajectory["camera"] and "rotation_matrix" in ego_trajectory["camera"] and "distance" in ego_trajectory["camera"]:
        tests.append({"height": ego_trajectory["camera"]["height"],
                      "rotation": R.from_matrix(np.array(ego_trajectory["camera"]["rotation_matrix"])),
                      "distance": ego_trajectory["camera"]["distance"]})
    # test different heights
    heights = np.linspace(0, 5, 1000)
    for nr, height in enumerate(heights):

        car_rays = []
        for point in relative_world_points:
            x = point[0]
            y = point[1]
            length = math.sqrt(y ** 2 + x ** 2 + height ** 2)
            car_rays.append([x / length, height / length, y / length])

        if weights is not None:
            cam2world_rotation = R.align_vectors(car_rays, camera_rays, weights=weights)
        else:
            cam2world_rotation = R.align_vectors(car_rays, camera_rays)
        test = {'height': height,
                'rotation': cam2world_rotation[0],
                'distance': cam2world_rotation[1]}
        tests.append(test)
        bar.update(nr)

    bar.finish()
    result = sorted(tests, key=lambda x: x['distance'])[0]
    r = result["rotation"].as_matrix()
    result.pop('rotation', None)
    result["height"] = float(result["height"])
    result["distance"] = float(result["distance"])
    result["rotation_matrix"] = [[float(x) for x in l] for l in r]
    result["mappingCoefficients"] = polynomial_coefficients
    result["distortionCenter"] = distortion_center
    result["stretchMatrix"] = ego_trajectory["camera"]["stretch_matrix"]
    print(result)

    with open(path, 'w') as file:
        json.dump(result, file, indent=4)

    print("Finished")

