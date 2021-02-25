import tkinter as tk
from tkinter import filedialog
import numpy as np
import math
from scipy.spatial.transform import Rotation as R
import progressbar

weights = None
'''
#W693
height = 1.53
image_points = [[286, 334],  # near front
                [373, 334],
                [294, 310],
                [365, 310],
                [305, 272],  # middle
                [352, 272],
                [310, 264],
                [352, 263],
                [400, 272],  # right
                [442, 270],
                [392, 264],
                [432, 262],
                [217, 271],  # left
                [261, 271],
                [229, 263],
                [269, 263],
                [294, 301],  # far front
                [358, 301],
                [229, 286],
                [355, 286],
                [308, 261],  # middle
                [347, 261],
                [310, 254],
                [345, 254],
                [387, 260],  # right
                [424, 259],
                [381, 254],
                [416, 253],
                [231, 261],  # left
                [267, 261],
                [239, 254],
                [274, 254]]
car_points = [[5.65, -0.5],  # near front
               [5.65, 0.5],
               [5.65, -0.5],
               [5.65, 0.5],
               [8.65, -0.5],   # middle
               [8.65, 0.5],
               [9.65, -0.5],
               [9.65, 0.5],
               [8.65, 1.5],   # right
               [8.65, 2.5],
               [9.65, 1.5],
               [9.65, 2.5],
               [8.65, -2.5],    # left
               [8.65, -1.5],
               [9.65, -2.5],
               [9.65, -1.5],
               [6.53, -0.5],  # far front
               [6.53, 0.5],
               [7.53, -0.5],
               [7.53, 0.5],
               [10.53, -0.5],  # middle
               [10.53, 0.5],
               [11.53, -0.5],
               [11.53, 0.5],
               [10.53, 1.5],  # right
               [10.53, 2.5],
               [11.53, 1.5],
               [11.53, 2.5],
               [10.53, -2.5],  # left
               [10.53, -1.5],
               [11.53, -2.5],
               [11.53, -1.5]]
polynomial_coefficients = np.array([408.1824388503350,-0.001488495144208,0.000001550635877780031,-0.000000002430019334469862])
distortion_center = np.array([319.1455569294537,228.7246144122634])
stretch_matrix = np.array([[1, 0],[0, 1]])
'''
'''
#W211
height = 1.28
image_points = [[300, 297],
                [368, 295],
                [312, 269],
                [358, 267],
                [314, 262],
                [353, 261],
                [266, 270],
                [224, 270],
                [272, 264],
                [232, 264],
                [402, 265],
                [443, 261],
                [395, 259],
                [434, 256],
                [303, 285],
                [363, 284],
                [308, 275],
                [360, 274],
                [316, 258],
                [353, 257],
                [317, 254],
                [352, 253],
                [279, 259],
                [243, 260],
                [283, 254],
                [249, 255],
                [390, 255],
                [424, 252],
                [386, 251],
                [420, 249]]
car_points = [[5.65, -0.5],
               [5.65, 0.5],
               [8.65, -0.5],
               [8.65, 0.5],
               [9.65, -0.5],
               [9.65, 0.5],
               [8.65, -1.5],
               [8.65, -2.5],
               [9.65, -1.5],
               [9.65, -2.5],
               [8.65, 1.5],
               [8.65, 2.5],
               [9.65, 1.5],
               [9.65, 2.5],
               [6.53, -0.5],
               [6.53, 0.5],
               [7.53, -0.5],
               [7.53, 0.5],
               [10.53, -0.5],
               [10.53, 0.5],
               [11.53, -0.5],
               [11.53, 0.5],
               [10.53, -1.5],
               [10.53, -2.5],
               [11.53, -1.5],
               [11.53, -2.5],
               [10.53, 1.5],
               [10.53, 2.5],
               [11.53, 1.5],
               [11.53, 2.5]]
polynomial_coefficients = np.array([402.9277417504681,-0.001330930621773,0.0000006962905292477972,-0.0000000009394025348668240])
distortion_center = np.array([326.1576815933253,203.8409099365607])
stretch_matrix = np.array([[1, 0],[0, 1]])
'''
'''
#Passat
height = 1.2
image_points = [[279, 355],
                [339, 354],
                [284, 344],
                [336, 344],

                [201, 337],
                [243, 339],
                [210, 331],
                [250, 332],

                [379, 337],
                [422, 334],
                [372, 330],
                [411, 328],

                [175, 317],
                [199, 318],
                [183, 314],
                [206, 314],

                [297, 319],
                [326, 319],
                [297, 315],
                [325, 315],

                [423, 315],
                [451, 314],
                [417, 313],
                [443, 311],

                [231, 305],
                [248, 306],
                [232, 304],
                [249, 305],

                [302, 306],
                [321, 306],
                [302, 304],
                [321, 304]
                ]
car_points = [[6.7, -0.5],
               [6.7, 0.5],
               [7.7, -0.5],
               [7.7, 0.5],

               [8.7, -2.5],
               [8.7, -1.5],
               [9.7, -2.5],
               [9.7, -1.5],

               [8.7, 1.5],
               [8.7, 2.5],
               [9.7, 1.5],
               [9.7, 2.5],

               [14.7, -5],
               [14.7, -4],
               [15.7, -5],
               [15.7, -4],

               [14.7, -0.5],
               [14.7, 0.5],
               [15.7, -0.5],
               [15.7, 0.5],

               [14.7, 4],
               [14.7, 5],
               [15.7, 4],
               [15.7, 5],

               [21.7, 4.5],
               [21.7, 3.5],
               [22.7, 4.5],
               [22.7, 3.5],

               [21.7, -0.5],
               [21.7, 0.5],
               [22.7, -0.5],
               [22.7, 0.5]
              ]
polynomial_coefficients = np.array([389.0629124862945, -0.001573091074774, 0.000002734730111359755,-0.000000006622934787551719])
distortion_center = np.array([320.9561509906940, 277.1249938113623])
stretch_matrix = np.array([[0.994303295214212,-0.037786301501645],[0.038044154795730, 1.0]])

'''

#Smart
height = 1.28
image_points = [[277, 381],
                [360, 381],
                [282, 363],
                [352, 362],

                [176, 347],
                [229, 350],
                [188, 339],
                [238, 340],

                [404, 347],
                [457, 343],
                [392, 338],
                [438, 335],

                [154, 317],
                [183, 316],
                [163, 311],
                [190, 312],

                [296, 318],
                [329, 318],
                [296, 314],
                [328, 314],

                [443, 314],
                [472, 312],
                [437, 311],
                [463, 309],

                [220, 299],
                [240, 300],
                [221, 298],
                [241, 299],

                [300, 300],
                [320, 300],
                [300, 298],
                [319, 298],
                ]
car_points = [[4.7, -0.5],
               [4.7, 0.5],
               [5.7, -0.5],
               [5.7, 0.5],

               [6.7, -2.5],
               [6.7, -1.5],
               [7.7, -2.5],
               [7.7, -1.5],

               [6.7, 1.5],
               [6.7, 2.5],
               [7.7, 1.5],
               [7.7, 2.5],

               [12.7, -5],
               [12.7, -4],
               [13.7, -5],
               [13.7, -4],

               [12.7, -0.5],
               [12.7, 0.5],
               [13.7, -0.5],
               [13.7, 0.5],

               [12.7, 4],
               [12.7, 5],
               [13.7, 4],
               [13.7, 5],

               [19.7, 4.5],
               [19.7, 3.5],
               [20.7, 4.5],
               [20.7, 3.5],

               [19.7, -0.5],
               [19.7, 0.5],
               [20.7, -0.5],
               [20.7, 0.5],
              ]
polynomial_coefficients = np.array([405.4912462199090,-0.001440912782964,0.000001534038302671814,-0.000000003445578411650097])
distortion_center = np.array([322.9747299785971, 261.3262122251465])
stretch_matrix = np.array([[1, 0],[0, 1]])


'''
weights = np.ones(len(car_points))
weights[-1] = 2
weights[-2] = 8
weights[-3] = 15
'''

def uv2xyz(u, v):
    uv = np.array([[u], [v]])
    uv = np.subtract(uv, distortion_center)
    uv = np.dot(inv_stretch_matrix, uv)
    rho = math.sqrt(uv[0][0] ** 2 + uv[1][0] ** 2)
    matlab_xyz = np.array([[uv[0][0]],
                           [uv[1][0]],
                           [polynomial_coefficients[0] + polynomial_coefficients[1] * (rho ** 2) +
                            polynomial_coefficients[2] * (rho ** 3) + polynomial_coefficients[3] * (rho ** 4)]])
    #camera_xyz = np.array([[matlab_xyz[2][0]], [matlab_xyz[0][0]], [-matlab_xyz[1][0]]])
    camera_xyz = matlab_xyz / np.linalg.norm(matlab_xyz)
    return camera_xyz


def main():
    global inv_stretch_matrix

    distortion_center.shape = (2, 1)
    stretch_matrix.shape = (2, 2)
    inv_stretch_matrix = np.linalg.inv(stretch_matrix)

    camera_rays = [np.array(uv2xyz(image_point[0], image_point[1])).flatten() for image_point in image_points]
    heights = np.linspace(0, 5, 1000)
    tests = []
    widgets = [
        'Optimization: ', progressbar.SimpleProgress(),
        ' ', progressbar.Percentage(),
        ' ', progressbar.Bar(marker=progressbar.AnimatedMarker(fill='#')),
        ' ', progressbar.AdaptiveETA(),
        ' ', progressbar.AdaptiveTransferSpeed(unit="trials"),
    ]
    bar = progressbar.ProgressBar(widgets=widgets, max_value=1000, redirect_stdout=True).start()

    for nr, height in enumerate(heights):

        car_rays = []
        for point in car_points:
            longitudinal = point[0]
            lateral = point[1]
            length = math.sqrt(longitudinal**2 + lateral**2 + height**2)
            car_rays.append([lateral/length, height/length, longitudinal/length])

        if weights is not None:
            cam2world_rotation = R.align_vectors(car_rays, camera_rays, weights=weights)
        else:
            cam2world_rotation = R.align_vectors(car_rays, camera_rays)
        rotation = cam2world_rotation[0]
        test = {'height': height,
                'rotation': rotation.as_matrix(),
                'distance': cam2world_rotation[1]}
        tests.append(test)
        bar.update(nr)

    bar.finish()
    result = sorted(tests, key=lambda x: x["distance"])[0]
    print(result)


if __name__ == '__main__':
    main()
